"""
Functions used to run the Open Source GIS Pre-processing training Jupyter Notebook
"""

import os
import matplotlib
import rasterio
import gdal

from ipyleaflet import Map, GeoJSON, ScaleControl, FullScreenControl, basemaps, SplitMapControl, basemap_to_tiles, LayersControl, ImageOverlay
from matplotlib import pyplot

def cmap_options(var_name):
    # Default plot options
    #cmap = 'Blues'
    cmap = pyplot.get_cmap('Blues')
    norm = None

    if var_name.lower() in ['latitude', 'longitude', 'channelgrid', 'frxst_pts']:
        #cmap = 'binary'
        cmap = pyplot.get_cmap('binary')
    elif var_name.lower() in ['topography', 'hgt_m']:
        #cmap = 'BrBG'  # 'gist_earth'
        cmap = pyplot.get_cmap('BrBG')
    elif var_name.lower() in ['flowdirection']:
        colors = ['#ff0000', '#5959a6', '#806c93', '#a65959', '#a68659', '#a6a659', '#93a659', '#669966', '#669988',
                  '#999999']
        scale = [0, 1, 2, 4, 8, 16, 32, 64, 128, 255]
        cmap = matplotlib.colors.ListedColormap(colors)
        norm = matplotlib.colors.BoundaryNorm(scale, len(colors))
    elif var_name.lower() in ['landuse']:
        colors = ['#ed0000', '#dbd83d', '#aa7028', '#fbf65d', '#e2e2c1', '#ccba7c', '#dcca8f', '#fde9aa', '#68aa63',
                  '#85c724', '#38814e', '#1c6330', '#b5c98e', '#476ba0', '#70a3ba', '#bad8ea', '#b2ada3', '#c9c977',
                  '#a58c30', '#d1ddf9']
        scale = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23]
        cmap = matplotlib.colors.ListedColormap(colors)
        norm = matplotlib.colors.BoundaryNorm(scale, len(colors))
    elif var_name.lower() in ['streamorder']:
        colors = ['blue', 'green', 'red', 'yellow', '#000000']
        scale = [.9, 1.9, 2.9, 3.9, 4]
        #         scale = [1, 2, 3, 4, 5]
        cmap = matplotlib.colors.ListedColormap(colors)
        norm = matplotlib.colors.BoundaryNorm(scale, len(colors))
    return cmap, norm

def show_raster_map(raster_path, map_id, shp, out_folder):
    # Make new folder if does not exist
    raster_outputs_prj = os.path.join(out_folder, 'Raster_Outputs_Prj')
    if not os.path.exists(raster_outputs_prj):
        os.mkdir(raster_outputs_prj)

    # Reproject raster
    input_raster = gdal.Open(raster_path)
    file_name = os.path.basename(raster_path)
    output_raster = os.path.join(raster_outputs_prj, file_name)
    gdal.Warp(output_raster, input_raster, dstSRS='EPSG:4326')

    # Open in rasterio, give colormap, make no data transparent, save as png
    src = rasterio.open(output_raster)

    varname = file_name.replace('.tif', '')
    cmap, norm = cmap_options(varname)
    pyplot.imshow(src.read(1), cmap=cmap, aspect='auto', vmin=0.1, norm=norm, interpolation='nearest')
    
    #cmap = pyplot.get_cmap('viridis')
    #pyplot.imshow(src.read(1), cmap=cmap, aspect='auto', vmin=0.1)
           
    cmap.set_under('k', alpha=0)
    pyplot.axis('off')
    new_file_name = file_name.replace('.tif', '.png')
    pyplot.savefig(os.path.join(raster_outputs_prj, new_file_name), transparent=True, bbox_inches='tight', dpi=500)

    # get bounds from boundary shapefile
    bounds_df = (shp.bounds)
    minx = bounds_df.iloc[0][0]
    miny = bounds_df.iloc[0][1]
    maxx = bounds_df.iloc[0][2]
    maxy = bounds_df.iloc[0][3]

    bounds = ((miny, minx), (maxy, maxx))

    # Overlay image on map
    map_name = new_file_name.replace(".png", "")
    image = ImageOverlay(
        url=f'files/GIS_Training/Outputs/Raster_Outputs_Prj/{new_file_name}',
        bounds=bounds, name=map_name)

    map_id.add_layer(image)
    pyplot.close()

def create_map(center, zoom):
    m = Map(center=center, zoom=zoom, scroll_wheel_zoom=True)
    m.add_control(ScaleControl(position='bottomleft'))
    m.add_control(FullScreenControl())
    control = LayersControl(position='topright')
    m.add_control(control)

    m.layout.width = '950px'
    m.layout.height = '750px'
    return m