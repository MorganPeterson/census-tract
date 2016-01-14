#!/usr/bin/env python

# tract.py

from osgeo import ogr, osr
import json
import shapefile
import sys

if len(sys.argv) != 3:
    print '{0}'.format('USAGE: tract.py INFILE_NAME SHAPEFILE_NAME')
    sys.exit(1)
else:
    head_obj  = '{0}'.format(sys.argv[1])
    shape_obj = '{0}'.format(sys.argv[2])

our_json_obj  = 'census_tract'

in_file       = 'formatted-data/{0}.json'.format(head_obj)
out_file      = 'formatted-data/{0}-tract.json'.format(head_obj)
shape_file    = '{0}/{0}.shp'.format(shape_obj)

lat_name      = 'latitude'
lon_name      = 'longitude'

field_nmes    = []
g_field_count = 12

def get_census_tract(polylayer, longitude, latitude):
    """ takes in all layers and searches through them looking for the tract
    that matches our longitude and latitude values. If a tract is not found,
    then it returns an object with null fields"""

    pnt_ref       = osr.SpatialReference()
    pnt_ref.ImportFromEPSG(4326)

    geo_ref       = polylayer.GetSpatialRef()
    ctran         = osr.CoordinateTransformation(pnt_ref, geo_ref)
    [lon, lat, z] = ctran.TransformPoint(longitude, latitude)
    point         = ogr.Geometry(ogr.wkbPoint)

    point.SetPoint_2D(int(z), lon, lat)
    polylayer.SetSpatialFilter(point)

    p = polylayer.GetNextFeature()

    if p is None:
        # if p is None then there was a fault in the longitude and/or
        # latitude values and we eturn an object with field values of null
        x   = ','
        seq = []
        for field_count in range(g_field_count):
            seq.append('"{0}":null'.format(field_nmes[field_count]))
        pops = "{"+x.join(seq)+"}"
        return json.loads(pops)

    if point.Within(p.GetGeometryRef()):
        # if we do have longitude and latitude then we loop through the
        # layers fields and make and object that we then return
        x = ','
        seq = []
        for field_count in range(p.GetFieldCount()):
            seq.append('"{0}":"{1}"'.format(\
                    field_nmes[field_count],\
                    p.GetFieldAsString(field_count)))
        pops = "{"+x.join(seq)+"}"
        return json.loads(pops)

driver       = ogr.GetDriverByName('ESRI Shapefile')
sf           = driver.Open(shape_file, 0)
layers       = sf.GetLayer()

if sf is None:
    print "Could not open {0}".format(shape_file)
    sys.exit(1)

polydef = layers.GetLayerDefn()
for i in range(polydef.GetFieldCount()):
    field_nmes.append(polydef.GetFieldDefn(i).GetName()[:-2])

with open(in_file,'rb') as inf:
    # size of file determined by memory. Need to re-write.
    x = json.load(inf)

for ele in x[head_obj]:
    # lon/lat to be passed to our census tract function
    our_lon = float(ele[lon_name])
    our_lat = float(ele[lat_name])

    # append our census tract object to our JSON object
    ele[our_json_obj] = get_census_tract(layers, our_lon, our_lat)

with open(out_file, 'wb') as outf:
    # size of output determined by memory. Need to re-write.
    json.dump(x, outf)

