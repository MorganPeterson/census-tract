#!/usr/bin/env python
# tract.py

from osgeo import ogr, osr

import json
import shapefile
import sys

if len(sys.argv) != 3:
    print 'USAGE: {0}'.format('tract.py INFILE_NAME SHAPEFILE_NAME')
    print '{0}... {1}.json and {1}.shp\n'.format('Assuming defaults','index')
    head_obj   = 'index'
    shape_obj  = 'index'
else:
    head_obj   = '{0}'.format(sys.argv[1])
    shape_obj  = '{0}'.format(sys.argv[2])
    in_file    = '{0}'.format(head_obj)
    out_file   = '{0}.tract.json'.format(head_obj)
    shape_file = '{0}'.format(shape_obj)


field_nmes     = []
g_field_count  = 12 # hard coded and should be dynamic
lat_name       = 'latitude'
lon_name       = 'longitude'
out_json_obj   = 'census_tract'


def fmt_return_json(field_names, field_values, fc):
    """ Format all the shapefile values into a final JSON object that will
    attached to the object that came in. """
    x   = ','
    seq = []
    for fc in range(fc):
        if field_values is None:
            fv = 'null'
        else:
            fv = field_values.GetFieldAsString(fc)

        seq.append('"{0}":"{1}"'.format(\
                field_nmes[fc],fv))

    json_comp = "{"+x.join(seq)+"}"
    print json_comp
    return json.loads(json_comp)


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
        return fmt_return_json(field_nmes, None, g_field_count)

    if point.Within(p.GetGeometryRef()):
        # if we do have longitude and latitude then we loop through the
        # layers fields and make and object that we then return
        return fmt_return_json(field_nmes, p, g_field_count)


def get_parent_field(our_head_object):
    """ head_object is also the name of the parent field. We only nead the
    actual file name, though. Not the whole path. """
    temp = our_head_object.split('/')[-1]
    robj = temp.split('.')[-2]
    return robj


driver       = ogr.GetDriverByName('ESRI Shapefile')
sf           = driver.Open(shape_file, 0)
if sf is None:
    print "Could not open {0}".format(shape_file)
    sys.exit(1)


layers        = sf.GetLayer()
polydef       = layers.GetLayerDefn()
g_field_count = polydef.GetFieldCount()

for i in range(g_field_count):
    field_nmes.append(polydef.GetFieldDefn(i).GetName()[:-2])

with open(in_file,'rb') as inf:
    # size of file determined by memory. Need to re-write.
    x = json.load(inf)

parent_field = get_parent_field(head_obj)

for ele in x[parent_field]:
    # lon/lat to be passed to our census tract function
    our_lon = float(ele[lon_name])
    our_lat = float(ele[lat_name])

    # append our census tract object to our JSON object
    ele[out_json_obj] = get_census_tract(layers, our_lon, our_lat)

with open(out_file, 'wb') as outf:
    # size of output determined by memory. Need to re-write.
    json.dump(x, outf)

