# Crear un bot para aumentar las visitas de YouTube con Python

#librerías (se requiere instalar selenium / descargar webdriver)
import time;
from selenium import webdriver;

#Tiempo para refrescas la página
Timer = 5

#Enlace (Blog, YouTube)
enlace = 'https://www.youtube.com/watch?v=Auzs95InJzo'

#Número visitas
views = 1000

#driver
driver = webdriver.Chrome("C:/gisbook/chromedriver.exe")
driver.get(enlace)

for i in range(views):
    time.sleep(Timer)
    driver.refresh()
    print(i)
