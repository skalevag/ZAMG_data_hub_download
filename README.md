# ZAMG data hub download

Scripts for downloading selected datasets from [ZAMG data hub](https://data.hub.zamg.ac.at/) using the [API](https://dataset.api.hub.zamg.ac.at/v1/docs/).

**TODOs:**

- Include authentication token (currently added but not working)
- Better error handling
- Update licence and make freely available
- Include option to find closest station to geographical coordinates

## Authentication
For some datasets authenticacion is necessary. To download datasets that require authetication an API token is needed. This can be obtained after registering an account. On the user page there is a "API Tokens" button, which takes you to a page where the access tokens can be generated. When the query is sent through the API, the `auth=####`term is added. 

## Gridded datasets

Features:

- NetCDF download data for specified latitude longitude box
- NetCDF download of data in smaller slices
- merging NetCDF files by year
- download of grid cell timeseries at specified coordinates (lat,lon)

*Gridded datasets download currently implemented:*

- INCA, hourly
- SPARTACUS, daily and monthly
- APOLIS
- WINFORE
- SNOWGRID (requires authentication)

## Station data

Features:

- automatic selection of stations within a latitude longitude box
- requesting data in 1-year slices
- parallel processing for download

*Station data download currently implemented for:*

- 10-minute data
- hourly data


**To speed up download, it is strongly recommended to download the data using the annual slices and parallel processing options!**

