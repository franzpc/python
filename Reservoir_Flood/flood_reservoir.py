# -*- coding: utf-8 -*-
"""
Created on Wed May 15 10:04:54 2024

@author: franz
"""

import rasterio
from rasterio.plot import show
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Definir la ruta de los archivos
dem_path = r'E:\Temp\FloodChatGPT\WGS84\DEM.tif'
rio_shp_path = r'E:\Temp\FloodChatGPT\WGS84\rio.shp'
represa_shp_path = r'E:\Temp\FloodChatGPT\WGS84\represa.shp'  # Ruta del shapefile de la represa
sat_image_path = r'E:\Temp\FloodChatGPT\WGS84\image.tif'  # Ruta de la imagen satelital
output_tif_path = r'E:\Temp\FloodChatGPT\WGS84\water_depth.tif'  # Ruta de salida para el archivo TIFF

# Cargar el DEM
dem_data = rasterio.open(dem_path)
dem_array = dem_data.read(1)
dem_transform = dem_data.transform

# Cargar el shapefile del río
rio_data = gpd.read_file(rio_shp_path)

# Cargar el shapefile de la represa
represa_data = gpd.read_file(represa_shp_path)

# Cargar la imagen satelital
sat_image_data = rasterio.open(sat_image_path)
sat_image_array = sat_image_data.read([1, 2, 3])  # Leer solo las bandas RGB
sat_image_extent = rasterio.plot.plotting_extent(sat_image_data)

# Verificar y transformar las proyecciones de las capas vectoriales al CRS de la imagen satelital
rio_data = rio_data.to_crs(sat_image_data.crs)
represa_data = represa_data.to_crs(sat_image_data.crs)

# Definir la elevación del agua
water_level = 25  # metros por encima del nivel del río

# Calcular la profundidad del agua
water_depth = np.maximum(0, (dem_array.min() + water_level) - dem_array)

# Crear una máscara para los valores de cero
water_depth_masked = np.ma.masked_equal(water_depth, 0)

# Guardar el ráster de profundidad en un archivo TIFF con nodata
with rasterio.open(
    output_tif_path,
    'w',
    driver='GTiff',
    height=water_depth.shape[0],
    width=water_depth.shape[1],
    count=1,
    dtype=water_depth.dtype,
    crs=dem_data.crs,
    transform=dem_transform,
    nodata=-9999  # Establecer el valor de nodata
) as dst:
    dst.write(water_depth_masked.filled(-9999), 1)  # Escribir el ráster con nodata

# Crear un nuevo colormap con tonos de azul similares al de la imagen
colors = [
    (0.0, 1.0, 1.0),  # cyan claro
    (0.0, 0.5, 1.0),  # azul medio
    (0.0, 0.0, 0.5)   # azul oscuro
]
n_bins = 256  # Número de niveles de color
new_cmap = LinearSegmentedColormap.from_list('custom_blues', colors, N=n_bins)

# Crear la figura y los ejes
fig, ax = plt.subplots(figsize=(10, 10))

# Mostrar imagen satelital de fondo
show(sat_image_data, ax=ax)

# Mostrar raster de inundación con colormap personalizado
show(water_depth_masked, ax=ax, cmap=new_cmap, alpha=0.6, transform=dem_transform)

# Plotear capas vectoriales
rio_data.plot(ax=ax, color='blue', label='Río')
represa_data.plot(ax=ax, color='red', linewidth=4, label='Represa')

# Ajustar límites de los ejes
x_min = min(rio_data.total_bounds[0], represa_data.total_bounds[0], dem_data.bounds.left, sat_image_data.bounds.left)
x_max = max(rio_data.total_bounds[2], represa_data.total_bounds[2], dem_data.bounds.right, sat_image_data.bounds.right)
y_min = min(rio_data.total_bounds[1], represa_data.total_bounds[1], dem_data.bounds.bottom, sat_image_data.bounds.bottom)
y_max = max(rio_data.total_bounds[3], represa_data.total_bounds[3], dem_data.bounds.top, sat_image_data.bounds.top)
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

# Configurar visualización
ax.set_title(f'Simulación de una Inundación al llenar un embalse (Nivel del Agua: +{water_level}m)')
ax.set_xlabel('')
ax.set_ylabel('')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}'))
ax.legend()
plt.xticks(rotation=0)
plt.yticks(rotation=90)
plt.show()

# Calcular el volumen total de agua almacenada usando el raster de profundidad guardado
with rasterio.open(output_tif_path) as depth_data:
    water_depth_array = depth_data.read(1)
    water_depth_masked = np.ma.masked_equal(water_depth_array, depth_data.nodata)

    # Calcular el área de cada celda en metros cuadrados
    cell_area = abs(depth_data.transform[0] * depth_data.transform[4])

    # Calcular el volumen total de agua almacenada
    total_volume = np.sum(water_depth_masked) * cell_area  # Volumen en metros cúbicos

    # Imprimir los resultados
    print(f'El volumen total de agua almacenada es: {total_volume:.2f} metros cúbicos')
    print(f'Tamaño de celda utilizado para el cálculo: {abs(depth_data.transform[0])} x {abs(depth_data.transform[4])} metros')