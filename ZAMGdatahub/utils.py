"""Basic functions needed for various steps of download process."""

import datetime
from dateutil.relativedelta import relativedelta
import urllib.request
import json


def makeTimeSlices(year: int,firstMonth = 1,lastMonth=12,maxMonths=2,maxDays: int =None,datetimeformat = "%Y-%m-%d %H:%M",firstDOY: datetime.datetime = None) -> list:
    """Makes a list of time slices (start and end times) for a specified year. Inteded to be used when downloading INCA or SPARTACUS data.

    Args:
        year (int): which year to create time slices for
        firstMonth (int, optional): the month to start the time slices. Defaults to 1.
        lastMonth (int, optional): the month to end the time slices. Defaults to 12.
        maxMonths (int, optional): maximum permitted number of months in each slice. Defaults to 2.
        datetimeformat (str, optional): Format of output datetime sting. Defaults to "%Y-%m-%d %H:%M".
        firstDOY (datetime.datetime, optional): The first date that is permitted in the first timeslice. Defaults to None.

    Returns:
        list: list of datetime stings as slices (tuples)
    """
    # set the last day of the year
    if firstDOY is None:
        firstDOY = datetime.datetime(2011,3,1,0,0) # INCA data is only available from March 2011 onwards
    lastDOY = datetime.datetime(year+1,1,1,0,0)
    now = datetime.datetime.now() #+ relativedelta(days=-2)
    if now < lastDOY:
        lastDOY = datetime.datetime(now.year,now.month,now.day,now.hour,0) 
        lastMonth = now.month
    # set start month
    month = firstMonth
    
    # make list of time slices
    slices = []
    while month<lastMonth+1:
        dtStart = datetime.datetime(year,month,1,0,0)
        # check the first
        if dtStart<firstDOY:
            dtStart = firstDOY
        if maxDays is None:
            dtEnd = dtStart + relativedelta(months=+maxMonths)
            # check that the end datetime does not exceed the last day of the year
            if dtEnd >= lastDOY:
                dtEnd = lastDOY
            # convert to string
            start = dtStart.strftime(datetimeformat)
            end = dtEnd.strftime(datetimeformat)

            slices.append((start,end))
        else:
            # if a maximum number of days are specified, override the max number of months
            maxMonths = 1
            # this will only slice the month in two slices
            # the first one will be equal to maxDays, and the rest simply the rest of the month
            dtEndMonth = dtStart + relativedelta(months=+maxMonths)
            dtEnd = dtStart + relativedelta(days=+maxDays)
            # check that the end datetime does not exceed the last day of the year
            if dtEndMonth >= lastDOY:
                dtEndMonth = lastDOY
            elif dtEnd >= lastDOY:
                dtEnd = lastDOY
            
            # convert to string
            start = dtStart.strftime(datetimeformat)
            middle = dtEnd.strftime(datetimeformat)
            end = dtEndMonth.strftime(datetimeformat)

            slices.append((start,middle))
            slices.append((middle,end))
        
        

        month = month + maxMonths
    
    return slices


def makeDailyTimeSlices(start: str,end: str, maxDays=1,datetimeformat: str = "%Y-%m-%d %H:%M") -> list:
    """Make time slices that are a speficied length.

    Args:
        start (str): start of the first slice
        end (str): end of the last slice
        maxDays (int, optional): maximum number of days in each slice. Defaults to 1.
        datetimeformat (_type_, optional): Format of output datetime sting. Defaults to "%Y-%m-%d %H:%M".

    Returns:
        list: list of datetime slices as tuples
    """
    start = datetime.datetime.strptime(start,datetimeformat)
    end = datetime.datetime.strptime(end,datetimeformat)

    slices = []
    s = start
    while s < end:
        e = s + relativedelta(days=+maxDays)
        slices.append((s.strftime(datetimeformat),e.strftime(datetimeformat)))
        s = e
    return slices

def makeAnnualTimeSlices(start: str,end: str, datetimeformat: str = "%Y-%m-%d %H:%M"):
    """_summary_

    Args:
        start (str): start date or datetime as string
        end (str): end date or datetime as string
        datetimeformat (str, optional): format of input and output. Defaults to "%Y-%m-%d %H:%M".

    Returns:
        list: list of datetime slices as tuples
    """
    start = datetime.datetime.strptime(start,datetimeformat)
    end = datetime.datetime.strptime(end,datetimeformat)

    slices = []
    for year in list(range(start.year,end.year+1)):
        s = max(start,datetime.datetime(year,1,1,0,0))
        e = min(end,datetime.datetime(year,12,31,23,59))
        slices.append((s.strftime(datetimeformat),e.strftime(datetimeformat)))
    return slices

def makeFilename(start: str, end: str, ZAMGquery):
    """Makes a filename based on a specified start and end date plus ZAMGquery.

    Args:
        start (str): start date or datetime as string
        end (str): end date or datetime as string
        ZAMGquery (ZAMGdatahub.query.stationQuery or ZAMGdatahub.query.stationQuery): the query submitted to ZAMG datahub to request data

    Returns:
        str: filename based on ZAMGquery
    """
    format_to_extention = {"netcdf": "nc", "csv": "csv"}
    # compact the datetime notation
    s = start.replace("-", "").replace(" ", "").replace(":", "")
    e = end.replace("-", "").replace(" ", "").replace(":", "")
    timeslice = f"{s}-{e}"
    # make filename
    filename = (
        "_".join(
            [
                ZAMGquery.output_filename_head,
                ",".join(ZAMGquery.params),
                ZAMGquery.location_label,
                timeslice,
            ]
        )
        + f".{format_to_extention[ZAMGquery.output_format]}"
    )
    return filename

def makeStationFilenames(start: str, end: str, ZAMGquery):
    """Make filename from a ZAMG datahub query for station data.

    Args:
        start (str): start date or datetime as string
        end (str): end date or datetime as string
        ZAMGquery (ZAMGdatahub.query.stationQuery or ZAMGdatahub.query.stationQuery): the query submitted to ZAMG datahub to request data

    Returns:
        list: list of filenames
    """
    format_to_extention = {"netcdf": "nc", "csv": "csv"}
    
    
    filenames = []
    for station,name,start,subdir in zip(ZAMGquery.station_ids,ZAMGquery.station_names,ZAMGquery.station_starts,ZAMGquery.station_longnames):
        if ZAMGquery.annualSlices:
            start = datetime.datetime.strptime(start,"%Y-%m-%d").strftime("%Y-%m-%d %H:%M")
            slices = makeAnnualTimeSlices(start,end)
            for s,e in slices:
                # make filename
                filenames.append(
                    (
                        subdir,
                        "_".join(
                            [
                                station,
                                name.replace("/","-").replace(" ","-"),
                                ZAMGquery.output_filename_head,
                                f"{s[:4]}",
                            ]
                        ) + f".{format_to_extention[ZAMGquery.output_format]}"
                    )
                )
        else:
            # compact the datetime notation
            e = end.replace("-", "").replace(" ", "").replace(":", "")
            s = start.replace("-", "").replace(" ", "").replace(":", "")
            # make filename
            filenames.append(
                "_".join(
                    [
                        station,
                        name.replace("/","-").replace(" ","-"),
                        ZAMGquery.output_filename_head,
                        f"{s[:8]}-{e[:8]}",
                    ]
                )
                + f".{format_to_extention[ZAMGquery.output_format]}"
            )
    return filenames


def getJSONfromURL(url,token=None):
    with urllib.request.urlopen(url) as the_url:
        data = json.loads(the_url.read().decode())
    return data
        
def getMyAuthToken(file):
    with open(file,"r") as f:
        token = f.read()
    return token