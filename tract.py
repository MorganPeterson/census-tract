#!/usr/bin/env python3
# tract.py

from osgeo import ogr, osr, gdal

import ijson
import json
import os
import sys

if len(sys.argv) != 3:
    print('USAGE: {0}'.format('tract.py INFILE_NAME SHAPEFILE_NAME'))
    print('{0}... {1}.json and {1}.shp\n'.format('Assuming defaults','index'))
    head_obj   = 'index'
    shape_obj  = 'index'
else:
    head_obj   = '{0}'.format(sys.argv[1])
    shape_obj  = '{0}'.format(sys.argv[2])
    in_file    = '{0}'.format(head_obj)
    out_file   = '{0}.tract.json'.format(head_obj)
    shape_file = '{0}'.format(shape_obj)

field_nmes     = []
g_field_count  = 12
lat_name       = 'latitude'
lon_name       = 'longitude'
out_json_obj   = 'census_tract'


def fmt_return_json(field_values, fc):
    """ Format all the shapefile values into a final JSON object that will
    attached to the object that came in. """
    x   = ','

    def builder(ele):
        if field_values is None:
            fv = 'null'
        else:
            fv = field_values.GetFieldAsString(ele)

        x = '"{0}":"{1}"'.format(field_nmes[ele],fv)
        return x

    seq = [builder(fc) for fc in range(fc)]
    return json.loads("{{{0}}}\n".format(x.join(seq)))


def get_census_tract(polylayer, pref, longitude, latitude):
    """ takes in all layers and searches through them looking for the tract
    that matches our longitude and latitude values. If a tract is not found,
    then it returns an object with null fields"""
    try:
        geo_ref       = polylayer.GetSpatialRef()
        ctran         = osr.CoordinateTransformation(pref, geo_ref)
        [lon, lat, z] = ctran.TransformPoint(longitude, latitude)
        point         = ogr.Geometry(ogr.wkbPoint)
        point.SetPoint_2D(0, lon, lat)
        polylayer.SetSpatialFilter(point)
        p = polylayer.GetNextFeature()
    except:
        p = None

    if p is None:
        # if p is None then there was a fault in the longitude and/or
        # latitude values and we eturn an object with field values of null
        return fmt_return_json(None, g_field_count)

    if point.Within(p.GetGeometryRef()):
        # if we do have longitude and latitude then we loop through the
        # layers fields and make and object that we then return
        return fmt_return_json(p, g_field_count)


def get_parent_field(our_head_object):
    """ head_object is also the name of the parent field. We only nead the
    actual file name, though. Not the whole path. """
    temp = our_head_object.split('/')[-1]
    robj = temp.split('.')[-2]
    return robj


driver       = ogr.GetDriverByName('ESRI Shapefile')
sf           = driver.Open(shape_file, 0)
if sf is None:
    print("Could not open {0}".format(shape_file))
    sys.exit(1)

# set all osgeo.gdal options
layers        = sf.GetLayer()
polydef       = layers.GetLayerDefn()
g_field_count = polydef.GetFieldCount()
pnt_ref       = osr.SpatialReference()
pnt_ref.ImportFromEPSG(4326)

field_nmes = \
        [polydef.GetFieldDefn(x).GetName()[:-2] for x in range(g_field_count)]

parent_field = get_parent_field(head_obj)

in_size  = os.stat(in_file).st_size

with open(in_file,'rb') as inf:
    outf = open(out_file, 'a')
    if outf == None:
        print('unable to open write file: {}'.format(out_file))
        sys.exit(1)

    # start getting our items from the file
    dir_item = '{}.item'.format(parent_field)

    # this print is only here to make the console output look cleaner
    print('\n')

    for ele in ijson.items(inf,dir_item):
        # lon/lat to be passed to our census tract function
        try:
            our_lon = float(ele[lon_name])
            our_lat = float(ele[lat_name])
        except:
            our_lon = ele[lon_name]
            our_lat = ele[lat_name]
        # append our census tract object to our JSON object
        ele[out_json_obj] = get_census_tract(layers, pnt_ref, our_lon, our_lat)
        json.dump(ele, outf)

        # all for the console progress tracker
        out_size = float(os.stat(out_file).st_size)
        sys.stdout.write(\
                '\rIn: {0}MB - Out: {1:.0f}MB - {2:.2f}%'.format(\
                (in_size/1000000), (out_size/1000000), out_size/in_size*100))
        sys.stdout.flush()

# erase all console output
sys.stdout.write('\r')
sys.stdout.flush()

#close write file
outf.close()


