## Ejecución de ejercicio 1 y 4

Enlace de la google sheet:
https://docs.google.com/spreadsheets/d/1WqenBn3AAcPtIcHsIJuala6jPMt8jYBXun8tgGm4cDw/edit?usp=sharing

Si se quiere obtener todos los datos:
```
python scrap-peliculas.py -a scrap
```

Si se quiere obtener obtener el top 50 por categoria:
```
python scrap-peliculas.py -a top50
```

Si se quiere obtener obtener el top 15 de las descripciones más detalladas:
```
python scrap-peliculas.py -a top15Detailed
```

## Notas
* Como ya hay datos obtenidos en la google sheet se recomienda ejecutar el top 50, antes de hacer el scrap. Se crea una nueva hoja.
* En el archivo de generos_peliculas.data, se quitan o agregan categorías que existan a las que se requiere hacer scrap
* En config.py se pueden cambiar distintos parámetros, como el nombre de las columnas en la google_sheet, el link principal de la página.
* No manipular el navegador que se abre.
