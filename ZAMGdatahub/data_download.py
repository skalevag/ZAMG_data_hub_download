import requests
import urllib
from pathlib import Path
import subprocess
from ZAMGdatahub import utils,query

def makeURL(ZAMGquery, start, end):
    """
    Makes a URL string for requesting gridded dataset from ZAMG data hub (https://data.hub.zamg.ac.at).
    
    Default parameters requests 2-meter air temperature in a lat-lon box of the Ötztal Alps.
    
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
    #if ZAMGquery.dataset is query.DatasetType.STATION_10min:
    #    sd = sd.replace(":","%3A")
    #    ed = ed.replace(":","%3A")

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
        baseurl = "https://dataset.api.hub.zamg.ac.at/v1/station/historical/klima-v1-10min"
        paramurl = "&".join(["parameters=" + par for par in ZAMGquery.params])
        url = [baseurl + "?"+ paramurl + f"&start={sd}&end={ed}&station_ids={station}&output_format={ZAMGquery.output_format}&filename=dummy" for station in ZAMGquery.station_ids]

    return url

def downloadData(ZAMGquery,start,end,ODIR,overwrite=False,verbose=True):
    """
    Requests and downloads data from ZAMG data hub, and saves the file in a specifed directory.
    """
    ODIR = Path(ODIR)
    
    # make filename
    if ZAMGquery.dataset is query.DatasetType.STATION_10min or ZAMGquery.dataset is query.DatasetType.STATION_1h:
        filenames = utils.makeStationFilenames(start,end,ZAMGquery)
        outfiles = [ODIR.joinpath(f) for f in filenames]
        urls = makeURL(ZAMGquery,start,end)
    else:
        filenames = [utils.makeFilename(start,end,ZAMGquery)]
        outfiles = [ODIR.joinpath(filename)]
        urls = [makeURL(ZAMGquery,start,end)]
    
    for outfile,filename,url in zip(outfiles,filenames,urls):
        # check whether file already exists
        if overwrite or not outfile.is_file():
            r = requests.get(url)
            if str(r) == "<Response [400]>":
                #print(url)
                raise requests.HTTPError(f"{r}: Bad request! Click link for more info: {url}")
            ff,html = urllib.request.urlretrieve(url, outfile)
            if verbose: print(filename, "was downloaded.")
        else:
            if verbose: print(filename, "has already been downloaded:",outfile)
        
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