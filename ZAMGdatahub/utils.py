import datetime
from dateutil.relativedelta import relativedelta

def makeTimeSlices(year,firstMonth = 1,lastMonth=12,maxMonths=2,datetimeformat = "%Y-%m-%d %H:%M",firstDOY=None):
    """
    Makes a list of time slices (start and end times) for a specified year.
    
    Parameters
    ----------
    year : int
    firstMonth : int
        default: 1
    lastMonth : int
        default: 12
    maxMonth : int
        default: 2
    datetimeformat : str
        default: '%Y-%m-%d %H:%M'
    """
    # set the last day of the year
    if firstDOY is None:
        firstDOY = datetime.datetime(2011,3,1,0,0) # INCA data is only available from March 2011 onwards
    lastDOY = datetime.datetime(year+1,1,1,0,0)
    # set start month
    month = firstMonth
    
    # make list of time slices
    slices = []
    while month<lastMonth+1:
        dtStart = datetime.datetime(year,month,1,0,0)
        # check the first
        if dtStart<firstDOY:
            dtStart = firstDOY
        dtEnd = dtStart + relativedelta(months=+maxMonths)
        # check that the end datetime does not exceed the last day of the year
        if dtEnd >= lastDOY:
            dtEnd = lastDOY
        
        # convert to string
        start = dtStart.strftime(datetimeformat)
        end = dtEnd.strftime(datetimeformat)

        slices.append((start,end))

        month = month + maxMonths
    
    return slices


def makeFilename(start,end,ZAMGquery):
    """
    Make filename from a ZAMG datahub query.
    """
    format_to_extention = {"netcdf":"nc","csv":"csv"}
    # compact the datetime notation
    s = start.replace("-","").replace(" ","").replace(":","")
    e = end.replace("-","").replace(" ","").replace(":","")
    timeslice = f"{s}-{e}"
    # make filename
    filename = "_".join([ZAMGquery.output_filename_head,','.join(ZAMGquery.params),ZAMGquery.location_label,timeslice])+f".{format_to_extention[ZAMGquery.output_format]}"
    return filename
