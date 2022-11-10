"""
Module containing classes, methods and functions related to queries to the ZAMG datahub.
"""

import pandas as pd
from enum import Enum
from ZAMGdatahub import utils
import json

class DatasetType(Enum):
    INCA = "https://dataset.api.hub.zamg.ac.at/v1/grid/historical/inca-v1-1h-1km"
    INCA_15min = "https://dataset.api.hub.zamg.ac.at/v1/grid/historical/inca-v1-15min-1km"
    INCA_POINT = "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/inca-v1-1h-1km"
    SPARTACUS = "https://dataset.api.hub.zamg.ac.at/v1/grid/historical/spartacus-v1-1d-1km"
    SPARTACUS_v2 = "https://dataset.api.hub.zamg.ac.at/v1/grid/historical/spartacus-v2-1d-1km"
    SPARTACUS_POINT = "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/spartacus-v1-1d-1km"
    SNOWGRID = "https://dataset.api.hub.zamg.ac.at/v1/grid/historical/snowgrid_cl-v1-1d-1km"
    WINFORE = "https://dataset.api.hub.zamg.ac.at/v1/grid/historical/winfore-v1-1d-1km"
    APOLIS = "https://dataset.api.hub.zamg.ac.at/v1/grid/historical/apolis_short-v1-1d-100m"
    STATION_10min = "https://dataset.api.hub.zamg.ac.at/v1/station/historical/klima-v1-10min"
    STATION_1h = "https://dataset.api.hub.zamg.ac.at/v1/station/historical/klima-v1-1h"

    def getMetadata(self,token=None):
        try:
            meta_url = self.value+"/metadata"
            metadata = utils.getJSONfromURL(meta_url)
            return metadata
        except json.JSONDecodeError:
            print("Failed to get JSON from URL. Maybe you need to log in? Try visiting the website:")
            print(meta_url)
        
    
    
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

    
class RasterQuery:
    """
    Query for downloading raster data or gridcell timeseries from raster data from the ZAMG datahub.
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
        elif dataset is DatasetType.INCA_15min:
            self.output_filename_head = "incal-15min"
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
        elif dataset is DatasetType.SPARTACUS_v2:
            self.output_filename_head = "spartacus-daily-v2"
            self.output_format = "netcdf"
            self.lat_min = gridbox.lat_min
            self.lat_max = gridbox.lat_max
            self.lon_min = gridbox.lon_min
            self.lon_max = gridbox.lon_max
        elif dataset is DatasetType.APOLIS:
            self.output_filename_head = dataset.value.split("/")[-1]
            self.output_format = "netcdf"
            self.lat_min = gridbox.lat_min
            self.lat_max = gridbox.lat_max
            self.lon_min = gridbox.lon_min
            self.lon_max = gridbox.lon_max
        elif dataset is DatasetType.SNOWGRID:
            self.output_filename_head = "snowgrid"
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
            raise TypeError("Specified dataset was not any of the INCA, SPARTACUS or SNOWGRID datasets.")
        
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

class StationQuery:
    """
    Query for downloading station data from the ZAMG datahub.
    """
    
    def __init__(self, dataset: DatasetType, params: list or str , station_ids: list, station_names: list, station_starts: list, annualSlices = True, location_label = None, output="csv"):
        """Initialise the query for the defined dataset type."""
        # add common attributes
        if type(params) is str:
            # convert to list
            params = [params]
        if dataset is DatasetType.STATION_10min:
            # add quality flag id
            params.append("QFLAG")
        self.params = params
        self.dataset = dataset
        self.station_ids = [str(station) for station in station_ids]
        self.station_names = station_names
        self.station_longnames = [f"{str(ids)}_{str(station.replace('/','-').replace(' ','-'))}" for station,ids in zip(station_names,station_ids)]
        self.station_starts = station_starts
        self.output_format = output
        self.annualSlices = annualSlices
        # optional attributes
        if location_label:
            self.location_label = location_label
        else:
            self.location_label = "station-selection"
        
        # add attributes depending on dataset type
        if dataset is DatasetType.STATION_10min:
            self.output_filename_head = "station-10min"
        elif dataset is DatasetType.STATION_1h:
            self.output_filename_head = "station-hourly"
        else:
            raise TypeError("Must be either DatasetType.STATION_10min or DatasetType.STATION_1h")
        
    def __repr__(self):
        return "stationQuery()"
    
    def __str__(self):
        out = '\n'.join([f'{key}: {value}' for key,value in self.__dict__.items()])
        return f"stationQuery for download of {self.dataset.name}. \n{out}"
        
        
    def saveQuery(self,filename=None,DIR=None):
        """_summary_

        Args:
            filename (_type_, optional): _description_. Defaults to None.
            DIR (_type_, optional): _description_. Defaults to None.
        """
        if DIR is None:
            DIR="."
        if filename is None:
            filename = f"{self.dataset.name}_query_{self.location_label}"
        saveQuery(self.__dict__.copy(),filename,DIR=DIR)

def saveQuery(query,filename,DIR="."):
    query["params"] = ",".join(query["params"])
    try:
        query["station_ids"] = ",".join(query["station_ids"])
        query["station_names"] = ",".join(query["station_names"])
        query["station_starts"] = ",".join(query["station_starts"])
    except KeyError:
        pass
    queryTable = pd.DataFrame.from_dict(query,orient="index",columns=["query"])
    queryTable.to_csv(f"{DIR}/{filename}.txt",sep="\t")
    print(f'Query saved to "{DIR}/{filename}.txt"')
    
    
def loadQuery(file):
    queryDict = pd.read_table(file,index_col=0).to_dict()["query"]
    dataset = DatasetType[queryDict["dataset"].split(".")[-1]]
    params = queryDict["params"]
    if "lat_min" in queryDict.keys():
        loadedQuery = RasterQuery(
            dataset = dataset,
            params = params.split(","), 
            gridbox = LatLonBox(queryDict["location_label"],queryDict["lat_min"],queryDict["lat_max"],queryDict["lon_min"],queryDict["lon_max"]),
            output = queryDict["output_format"]
        )
    elif "lat" in queryDict.keys():
        loadedQuery = RasterQuery(
            dataset = dataset,
            params = params.split(","), 
            point_location = LatLonLocation(queryDict["location_label"],queryDict["lat"],queryDict["lon"]),
            output = queryDict["output_format"]
        )
    elif "station_ids" in queryDict.keys():
        loadedQuery = StationQuery(
            dataset = dataset,
            params = params.split(","), 
            station_ids = queryDict["station_ids"].split(","),
            station_names = queryDict["station_names"].split(","),
            station_starts = queryDict["station_starts"].split(","),
            output = queryDict["output_format"]
        )

    return loadedQuery

