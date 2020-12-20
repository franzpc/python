# Aumentar las visitas de YouTube con Python

#librerías (se requiere instalar selenium / descargar webdriver)
import time;
from selenium import webdriver;

#Tiempo para refrescas la página
Timer = 4

#Enlace (Blog, YouTube)
link = 'https://acolita.com'

#number of views
views = 12520

#driver
driver = webdriver.Chrome("C:/gisbook/chromedriver.exe")
driver.get(link)

for i in range(views):
    time.sleep(Timer)
    driver.refresh()
    print(i)
