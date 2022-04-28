"""
Module containing classes, methods and functions related to queries to the ZAMG datahub.
"""

import pandas as pd

class ZAMGdatahubQuery:
    """
    
    Attributes:
    
    """
    
    def __init__(self,dataset,params,gridboxlabel,lat_min,lat_max,lon_min,lon_max,output="netcdf"):
        dataset = dataset.upper()
        if dataset=="INCA":
            query = makeQuery(params,gridboxlabel,lat_min,lat_max,lon_min,lon_max,output=output)
            self.output_filename_head = "incal-hourly"
        elif dataset=="SPARTACUS":
            query = makeQuery(params,gridboxlabel,lat_min,lat_max,lon_min,lon_max,output=output)
            self.output_filename_head = "spartacus-daily"
        else:
            print("Specified dataset was not 'SPARTACUS' or 'INCA'. Setting the output filename to 'data'...")
            query = makeQuery(params,gridboxlabel,lat_min,lat_max,lon_min,lon_max,output=output)
            self.output_filename_head = "data"
        
        # add attributes
        self.query = query
        self.params = params
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.dataset = dataset
        self.name = gridboxlabel
        
    def saveQuery(self,filename=None,DIR=None):
        if DIR is None:
            DIR="."
        if filename is None:
            filename = f"{self.dataset}_query_{self.name}"
        saveQuery(self.query,filename,DIR=DIR)
        
    
def makeQuery(params,gridboxlabel,lat_min,lat_max,lon_min,lon_max,output="netcdf"):
    query = {"params":params,
             "gridboxlabel":gridboxlabel,
             "lat_min":lat_min,
             "lat_max":lat_max,
             "lon_min":lon_min,
             "lon_max":lon_max}
    if output == "netcdf":
        query["output_format"]=output
        query["file_extention"]="nc"
    elif output == "csv":
        query["output_format"]=output
        query["file_extention"]=output
    else:
        raise ValueError("The output can only be 'netcdf' or 'csv'.")
    return query

def saveQuery(query,filename,DIR="."):
    queryTable = pd.DataFrame.from_dict(query,orient="index",columns=["query"])
    queryTable.to_csv(f"{DIR}/{filename}.txt",sep="\t")
    print(f'Query saved to "{DIR}/{filename}.txt"')
    
def loadQuery(file):
    query = pd.read_table(file,index_col=0).to_dict()["query"]
    return query

