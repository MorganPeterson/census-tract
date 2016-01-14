# tract.py

Aggregate JSON objects containing lon/lat and census tract shapefile data

### USAGE
```
./tract.py INFILE_NAME SHAPEFILE_NAME
```
tract.py assumes that INFILE_NAME is a JSON file and that there are two fields in each object named longitude and latitude. If the longitude and latitude fields are named something else, you must change the variables lon_name and lat_name in tract.py to the your lon/lat field names. 

### INSTALLATION

#Ubuntu
You must make sure that you have libgdal-dev packages installed on you system.

Easiest way to install python packages is to install the PPA:
```bash
$ sudo apt-add-repository ppa:ubuntugis/ubuntugis-unstable

$ sudo apt-get update

$ sudo apt-get install python-gdal
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


