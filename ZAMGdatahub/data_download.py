import requests
import urllib
from pathlib import Path
import subprocess
import multiprocessing as mp
import time
from ZAMGdatahub import utils,query

def makeURL(ZAMGquery, start: str, end: str):
    """
    Makes a URL string for requesting gridded dataset from ZAMG data hub (https://data.hub.zamg.ac.at).
    
    Parameters
    ----------
    query : rasterQuery or stationQuery
    start : str
    end : str
    
    Returns
    -------
    url : str
    """

    # make start- and endtime strings
    sd = start.replace(" ","T")
    ed = end.replace(" ","T")

    # make query URL
    if ZAMGquery.dataset is query.DatasetType.INCA:
        bbox = f"{ZAMGquery.lat_min},{ZAMGquery.lon_min},{ZAMGquery.lat_max},{ZAMGquery.lon_max}"
        baseurl = "https://dataset.api.hub.zamg.ac.at/v1/grid/historical/inca-v1-1h-1km"
        url = baseurl + f"?anonymous=true&parameters={','.join(ZAMGquery.params)}&start={sd}&end={ed}&bbox={bbox}&output_format={ZAMGquery.output_format}"
    elif ZAMGquery.dataset is query.DatasetType.SPARTACUS:
        bbox = f"{ZAMGquery.lat_min},{ZAMGquery.lon_min},{ZAMGquery.lat_max},{ZAMGquery.lon_max}"
        baseurl = "https://dataset.api.hub.zamg.ac.at/v1/grid/historical/spartacus-v1-1d-1km"
        url = baseurl + f"?anonymous=true&parameters={','.join(ZAMGquery.params)}&start={sd}&end={ed}&bbox={bbox}&output_format={ZAMGquery.output_format}"
    elif ZAMGquery.dataset is query.DatasetType.INCA_POINT:
        baseurl = "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/inca-v1-1h-1km"
        url = baseurl + f"?anonymous=true&parameters={','.join(ZAMGquery.params)}&start={sd}&end={ed}&lon={ZAMGquery.lon}&lat={ZAMGquery.lat}&output_format={ZAMGquery.output_format}"
    elif ZAMGquery.dataset is query.DatasetType.SPARTACUS_POINT:
        baseurl = "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/spartacus-v1-1d-1km"
        url = baseurl + f"?anonymous=true&parameters={','.join(ZAMGquery.params)}&start={sd}&end={ed}&lon={ZAMGquery.lon}&lat={ZAMGquery.lat}&output_format={ZAMGquery.output_format}"
    elif ZAMGquery.dataset is query.DatasetType.STATION_10min:
        starts = [start.replace(" ","T") for start in ZAMGquery.station_starts]
        baseurl = "https://dataset.api.hub.zamg.ac.at/v1/station/historical/klima-v1-10min"
        paramurl = "&".join(["parameters=" + par for par in ZAMGquery.params])
        url = []
        for station,sd in zip(ZAMGquery.station_ids,ZAMGquery.station_starts):
            url.append( baseurl + "?"+ paramurl + f"&start={sd}&end={ed}&station_ids={station}&output_format={ZAMGquery.output_format}&filename=dummy")

    return url


def requestData(url,outfile,overwrite=False,verbose=True, max_retries = 3):
    """Send request for data and save to file."""
    # check whether file already exists
    if overwrite or not outfile.is_file():
        print("Starting download of",outfile.name)
        r = requests.get(url)
        if str(r) == "<Response [400]>":
            raise requests.HTTPError(f"{r}: Bad request! Click link for more info: {url}")
        try:
            urllib.request.urlretrieve(url, outfile)
            if verbose: print(outfile.name, "was downloaded.")
        except urllib.error.HTTPError as e:
            if verbose: print(e)
            if verbose: print("Trying again...")
            retries = 1
            success = False
            while not success and retries < max_retries+1:
                try:
                    urllib.request.urlretrieve(url, outfile)
                    if verbose: print(outfile.name, "was downloaded.")
                    success = True
                except urllib.error.HTTPError as e:
                    wait = retries * 5
                    if verbose: print(e)
                    if verbose: print(f"Failed again, will trying again after {wait} seconds.")
                    time.sleep(wait)
                    retries += 1 
                finally:
                    if not success:
                        print(f"Failed to download {outfile.name}\nTry requesting less data, e.g. fewer parameters or smaller time periods.")
    else:
        if verbose: print(outfile.name, "has already been downloaded:",outfile)
    
    return str(outfile)


def downloadData(ZAMGquery,start: str,end: str,ODIR,overwrite=False ,verbose=True, parallel=False):
    """
    Requests and downloads data from ZAMG data hub, and saves the file in a specifed directory.

    For station data parallel processing is highly recommended.
    """
    ODIR = Path(ODIR)
    
    # make filename
    if ZAMGquery.dataset is query.DatasetType.STATION_10min or ZAMGquery.dataset is query.DatasetType.STATION_1h:
        filenames = utils.makeStationFilenames(start,end,ZAMGquery)
        outfiles = [ODIR.joinpath(f) for f in filenames]
        urls = makeURL(ZAMGquery,start,end)
    else:
        filenames = [utils.makeFilename(start,end,ZAMGquery)]
        outfiles = [ODIR.joinpath(filenames[0])]
        urls = [makeURL(ZAMGquery,start,end)]
    
    if parallel:
        # init multiprocessing pool
        pool = mp.Pool(mp.cpu_count())
        # apply parallel processing
        outfiles = [pool.apply(requestData, args=(url,outfile,overwrite,verbose)) for outfile,url in zip(outfiles,urls)]
        # close pool
        pool.close()
    else:
        for outfile,url in zip(outfiles,urls):
            requestData(url,outfile,overwrite=overwrite,verbose=verbose)
        
    return outfiles

def mergeNetCDFfilesByYear(year,DIR,verbose=True,overwrite=False):
    """
    Merge NetCDF files from same year in a specified directory using cdo.
    
    Parameters
    ----------
    year : int or string
    DIR : str or pathlib.PosixPath
    verbose : boolean
        default True
    overwrite : boolean
        default False
    """
    # convert to PosixPath
    DIR = Path(DIR)
    # get files from directory
    files = [str(f) for f in list(DIR.glob(f"*_{year}*00.nc"))]
    # make outfile
    outfile = Path(files[0]).name.split(f"_{year}")[0]+f"_{year}.nc"
    # make command arguments
    if not overwrite:
        cmd = ["cdo","mergetime"] + files + [str(DIR.joinpath(outfile))]
    else:
        cmd = ["cdo","-O","mergetime"] + files + [str(DIR.joinpath(outfile))]
    # make string of argument list
    cmd = " ".join(cmd)
    # add environment variable that prohibits duplicate timestep indeces
    cmd = "export SKIP_SAME_TIME=1 ; " + cmd
    # run process
    if verbose:
        print(">>>",cmd)
    process = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True)
    # print output
    if verbose:
        print(process.stdout)
        print(process.stderr)