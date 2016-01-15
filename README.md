# tract.py

Aggregate JSON objects containing lon/lat and census tract shapefile data

### USAGE
```
./tract.py INFILE_NAME SHAPEFILE_NAME
```
Tract.py assumes that INFILE_NAME is a JSON file and that there are two fields in each object named longitude and latitude. If the longitude and latitude fields are named something else, you must change the variables lon_name and lat_name in tract.py to the your lon/lat field names. 

### Dependencies

##### Ubuntu
You must be sure to have the libgdal-dev packages installed on you system.

You will need to have python-gdal, shapefile, and ijson modules installed.

Easiest way to install python-gdal package is to install the PPA:
``` bash
$ sudo apt-add-repository ppa:ubuntugis/ubuntugis-unstable

$ sudo apt-get update

$ sudo apt-get install python-gdal
```
Shapefile and ijson can be installed using pip.
``` bash
$ pip install shapefile

$ pip install ijson
```

#### INFILE_NAME Format
Parent field matches INFILE_NAME
```json
{
  "parent": [
    {
      "longitude" : -70.000000,
      "latitude"  : 42.000000
    },
    { ... }
  ]
}
```

#### Census Tract Shapefiles
[Shapefiles](https://www.census.gov/cgi-bin/geo/shapefiles2010/main)

