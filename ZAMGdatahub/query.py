"""
Module containing classes, methods and functions related to queries to the ZAMG datahub.
"""

import pandas as pd
from enum import Enum, auto


class DatasetType(Enum):
    INCA = auto()
    SPARTACUS = auto()
    INCA_POINT = auto()
    SPARTACUS_POINT = auto()
    
    
class LatLonBox():
    """Class for containing the bounds of a latitude longitude gridbox."""
    
    def __init__(self,label,lat_min,lat_max,lon_min,lon_max):
        self.label = label
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max
    
    def __repr__(self):
        return "LatLonBox()"

    def __str__(self):
        output = f"LOCATION: {self.label}\nCOORDINATES: latitude: {self.lat_min} ... {self.lat_max} ; longitude {self.lon_min} ... {self.lon_max}"
        return output

    
class LatLonLocation():
    """Geographical location with coordinates and geographical coordinates."""
    
    def __init__(self,label,lat,lon):
        self.label = label
        self.lat = lat
        self.lon = lon
        
    def __repr__(self):
        return "LatLonLocation()"

    def __str__(self):
        output = f"LOCATION: {self.label}\nCOORDINATES: latitude: {self.lat} ; longitude {self.lon}"
        return output

    
class ZAMGdatahubQuery:
    """
    Query for the ZAMG datahub.
    
    Attributes:
    dataset : DatasetType class
        an instance of the custom DatasetType class
    params : list
    location_label : 
    
    """
    
    def __init__(self, dataset: DatasetType, params , gridbox : LatLonBox = None, point_location : LatLonLocation = None, output="netcdf"):
        """Initialise the query for the defined dataset type."""
        # add common attributes
        if type(params) is str:
            params = [params,]
        self.params = params
        self.dataset = dataset
        if gridbox is not None:
            self.location_label = gridbox.label
        if point_location is not None:
            self.location_label = point_location.label
        
        # add attributes depending on dataset type
        if dataset is DatasetType.INCA:
            self.output_filename_head = "incal-hourly"
            self.output_format = "netcdf"
            self.lat_min = gridbox.lat_min
            self.lat_max = gridbox.lat_max
            self.lon_min = gridbox.lon_min
            self.lon_max = gridbox.lon_max
        elif dataset is DatasetType.SPARTACUS:
            self.output_filename_head = "spartacus-daily"
            self.output_format = "netcdf"
            self.lat_min = gridbox.lat_min
            self.lat_max = gridbox.lat_max
            self.lon_min = gridbox.lon_min
            self.lon_max = gridbox.lon_max
        elif dataset is DatasetType.INCA_POINT:
            self.output_filename_head = "inca-point"
            self.output_format = "csv"
            self.lat = point_location.lat
            self.lon = point_location.lon
        elif dataset is DatasetType.SPARTACUS_POINT:
            self.output_filename_head = "spartacus-point"
            self.output_format = "csv"
            self.lat = point_location.lat
            self.lon = point_location.lon
        else:
            print("Specified dataset was not SPARTACUS or INCA. Setting a generic output_filename_head. You can change this manually by editing the attribute.")
            self.output_filename_head = "data"
            self.output_format = output
        
    def __repr__(self):
        return "ZAMGdatahubQuery()"
    
    def __str__(self):
        out = '\n'.join([f'{key}: {value}' for key,value in self.__dict__.items()])
        return f"ZAMGdatahubQuery for download of {self.dataset.name} with parameters {','.join(self.params)}. \n{out}"
        
        
    def saveQuery(self,filename=None,DIR=None):
        if DIR is None:
            DIR="."
        if filename is None:
            filename = f"{self.dataset.name}_query_{self.location_label}"
        saveQuery(self.__dict__.copy(),filename,DIR=DIR)


def saveQuery(query,filename,DIR="."):
    query["params"] = ",".join(query["params"])
    queryTable = pd.DataFrame.from_dict(query,orient="index",columns=["query"])
    queryTable.to_csv(f"{DIR}/{filename}.txt",sep="\t")
    print(f'Query saved to "{DIR}/{filename}.txt"')
    
    
def loadQuery(file):
    queryDict = pd.read_table(file,index_col=0).to_dict()["query"]
    dataset = DatasetType[queryDict["dataset"].split(".")[-1]]
    params = queryDict["params"]
    if "lat_min" in queryDict.keys():
        loadedQuery = ZAMGdatahubQuery(
            dataset = dataset,
            params = params.split(","), 
            gridbox = LatLonBox(queryDict["location_label"],queryDict["lat_min"],queryDict["lat_max"],queryDict["lon_min"],queryDict["lon_max"]),
            output = queryDict["output_format"]
        )
    elif "lat" in queryDict.keys():
        loadedQuery = ZAMGdatahubQuery(
            dataset = dataset,
            params = params.split(","), 
            point_location = LatLonLocation(queryDict["location_label"],queryDict["lat"],queryDict["lon"]),
            output = queryDict["output_format"]
        )
    
    return loadedQuery
