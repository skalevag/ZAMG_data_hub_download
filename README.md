# ZAMG data hub download

Rountines for downloading selected datasets from [ZAMG data hub](https://data.hub.zamg.ac.at/).

**TODOs:**

- Add custom error types for better error handling
- Adding other gridded datasets, e.g. Winfore, APOLIS
- Update licence and make freely available


## Gridded datasets

Features:

- NetCDF download data for specified latitude longitude box
- NetCDF download of data in smaller slices
- merging NetCDF files by year
- download of grid cell timeseries at specified coordinates (lat,lon)

### INCA


### SPARTACUS


## Station data

### 10-min resolution

Features:

- automatic selection of stations within a latitude longitude box
- requesting data in 1-year slices
- parallel processing for download

**To speed up download, it is strongly recommended to download the data using the annual slices and parallel processing options!**

