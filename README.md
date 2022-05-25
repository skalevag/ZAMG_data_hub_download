# ZAMG data hub download

Rountine for downloading INCA and other datasets from [ZAMG data hub](https://data.hub.zamg.ac.at/).

Define a latitude-longitude box as well as start and end dates. ZAMG data hub only allows for download of smaller datasets, so for a region, e.g. Ötztal Alps, Tyrol, only 2-3 months worth of data can be downloaded at a time.

**TODOs:**

- Station data download
    - make it more efficient by using the station metadata to define start and end dates, right now the download is super slow, because it downloads a lot of nans
- Add custom error types for better error handling
- Adding other gridded datasets, e.g. Winfore, APOLIS
- Update licence
