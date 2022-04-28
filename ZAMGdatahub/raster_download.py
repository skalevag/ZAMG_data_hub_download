import requests
import urllib
from pathlib import Path
import subprocess
from ZAMGdatahub import utils

def makeURL(dataset,start,end,**query):
    """
    Makes a URL string for requesting gridded dataset from ZAMG data hub (https://data.hub.zamg.ac.at).
    
    Default parameters requests 2-meter air temperature in a lat-lon box of the Ötztal Alps.
    
    Parameters
    ----------
    start : str
    end : str
    params : str
        default: "T2M"
    lat_min : str ; float
        default: 46.6
    lat_max : str ; float
        default: 47.3
    lon_min : str ; float
        default: 10.5
    lon_max : str ; float
        default: 11.4
    output_format : str
        default: "netcdf"
    
    Returns
    -------
    url : str
    """
    # unpack
    lat_min = query.get("lat_min",46.6)
    lat_max = query.get("lat_max",47.3)
    lon_min = query.get("lon_min",10.5)
    lon_max = query.get("lon_max",11.4)
    params = query.get("params","T2M")
    output_format = query.get('output_format',"netcdf")
    
    # make start- and endtime strings
    sd = start.replace(" ","T")
    ed = end.replace(" ","T")

    # make gridbox string
    bbox = f"{lat_min},{lon_min},{lat_max},{lon_max}"
    
    # make query URL
    dataset = dataset.upper()
    if dataset == "INCA":
        baseurl = "https://dataset.api.hub.zamg.ac.at/v1/grid/historical/inca-v1-1h-1km"
    elif dataset == "SPARTACUS":
        baseurl = "https://dataset.api.hub.zamg.ac.at/v1/grid/historical/spartacus-v1-1d-1km"
    url = baseurl + f"?anonymous=true&parameters={params}&start={sd}&end={ed}&bbox={bbox}&output_format={output_format}"

    return url

def downloadData(ZAMGquery,start,end,ODIR,overwrite=False,verbose=True):
    """
    Requests and downloads data from ZAMG data hub, and saves the file in a specifed directory.
    """
    ODIR = Path(ODIR)
    
    # make filename
    filename = utils.makeFilename(start,end,ZAMGquery)
    outfile = ODIR.joinpath(filename)
    
    # check whether file already exists
    if overwrite or not outfile.is_file():
        url = makeURL(ZAMGquery.dataset,start,end,**ZAMGquery.query)
        r = requests.get(url)
        if str(r) == "<Response [400]>":
            #print(url)
            raise requests.HTTPError(f"{r}: Bad request! {url}")
        ff,html = urllib.request.urlretrieve(url, outfile)
        if verbose: print(filename, "was downloaded.")
    else:
        if verbose: print(filename, "has already been downloaded:",outfile)
        
    return outfile

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
    # run process
    process = subprocess.run(cmd,shell=True,capture_output=True,universal_newlines=True)
    # print output
    if verbose:
        print(">>>",cmd)
        print(process.stderr)