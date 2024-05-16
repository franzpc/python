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
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LightSource

# Definir los parámetros
incremento = 0.25  # Incremento en metros
altura_maxima = 25.0  # Altura máxima en metros

# Definir la ruta de los archivos
dem_path = r'E:\Temp\FloodChatGPT\WGS84\DEM.tif'
rio_shp_path = r'E:\Temp\FloodChatGPT\WGS84\rio.shp'
represa_shp_path = r'E:\Temp\FloodChatGPT\WGS84\represa.shp'  # Ruta del shapefile de la represa

# Cargar el DEM
dem_data = rasterio.open(dem_path)
dem_array = dem_data.read(1)
dem_transform = dem_data.transform

# Crear un hillshade del DEM
ls = LightSource(azdeg=315, altdeg=45)
hillshade = ls.hillshade(dem_array, vert_exag=1, dx=1, dy=1)

# Cargar el shapefile del río
rio_data = gpd.read_file(rio_shp_path)

# Cargar el shapefile de la represa
represa_data = gpd.read_file(represa_shp_path)

# Verificar y transformar las proyecciones de las capas vectoriales al CRS del DEM
rio_data = rio_data.to_crs(dem_data.crs)
represa_data = represa_data.to_crs(dem_data.crs)

# Crear un nuevo colormap con tonos de azul similares al de la imagen
colors = [
    (0.0, 1.0, 1.0),  # cyan claro
    (0.0, 0.5, 1.0),  # azul medio
    (0.0, 0.0, 0.5)  # azul oscuro
]
n_bins = 256  # Número de niveles de color
new_cmap = LinearSegmentedColormap.from_list('custom_blues', colors, N=n_bins)

# Crear un objeto ScalarMappable para la leyenda de colores
sm = plt.cm.ScalarMappable(cmap=new_cmap, norm=plt.Normalize(vmin=0, vmax=altura_maxima))

# Crear la figura y los ejes
fig, ax = plt.subplots(figsize=(10, 10))

# Agregar la leyenda de colores dentro del mapa
cbar_ax = fig.add_axes([0.79, 0.2, 0.02, 0.2])  # Ajusta estos valores para posicionar la leyenda
cbar = fig.colorbar(sm, cax=cbar_ax)
cbar.ax.tick_params(labelsize=8)  # Ajusta el tamaño de fuente de la leyenda
cbar.set_label('Profundidad del Agua (m)', rotation=90, labelpad=5)

# Función de actualización para la animación
def update(frame):
    ax.clear()
    
    # Mostrar hillshade de fondo
    ax.imshow(hillshade, cmap='gray', extent=rasterio.plot.plotting_extent(dem_data))
    
    # Calcular la profundidad del agua para el frame actual
    current_level = frame * incremento
    water_depth = np.maximum(0, (dem_array.min() + current_level) - dem_array)
    masked_water_depth = np.ma.masked_where(water_depth <= 0, water_depth)  # Enmascarar áreas no inundadas
    
    # Mostrar raster de inundación con colormap personalizado
    show(masked_water_depth, ax=ax, cmap=new_cmap, alpha=0.6, transform=dem_transform)
    
    # Plotear capas vectoriales
    rio_data.plot(ax=ax, color='blue', label='Río')
    represa_data.plot(ax=ax, color='red', linewidth=4, label='Represa')
    
    # Ajustar límites de los ejes
    x_min = min(rio_data.total_bounds[0], represa_data.total_bounds[0], dem_data.bounds.left)
    x_max = max(rio_data.total_bounds[2], represa_data.total_bounds[2], dem_data.bounds.right)
    y_min = min(rio_data.total_bounds[1], represa_data.total_bounds[1], dem_data.bounds.bottom)
    y_max = max(rio_data.total_bounds[3], represa_data.total_bounds[3], dem_data.bounds.top)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    
    # Configurar visualización
    ax.set_title(f'Simulación de Inundación (Nivel del Agua: +{current_level:.2f}m)')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x)}'))
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    ax.legend()

# Calcular el número de frames
num_frames = int(altura_maxima / incremento)

# Crear la animación
ani = FuncAnimation(fig, update, frames=np.arange(0, num_frames + 1), repeat=False)

# Guardar la animación como GIF
ani.save('inundacion_parametrizada_hillshade.gif', writer=PillowWriter(fps=5))

plt.show()