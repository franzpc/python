# Crear un bot para aumentar las visitas de YouTube con Python

#librerías (se requiere instalar selenium / descargar webdriver)
import time;
from selenium import webdriver;

#Tiempo para refrescas la página
Timer = 150

#Enlace (Blog, YouTube)
enlace =https://youtu.be/2eywdrUyOfA?si=HvTFi3C52ncbqp9a
#Número visitas
views = 1000

#driver
driver = webdriver.Chrome (ID: cjighmmbcdpbfnhinpakjloafcpmefgl)
driver.get(enlace)

for i in range(views):
    time.sleep(Timer)
    driver.refresh()
    print(i)
