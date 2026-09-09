# Tablero RUFE · Valle del Cauca — V0.1

Mapa de calor y tablero de la afectación por el sismo del 10/08/2026, a partir del
Registro Unifamiliar de Emergencias (RUFE) consolidado por municipio.

## Abrirlo

Doble clic en **INICIAR_TABLERO.bat**. Busca Python en el lanzador `py`, en el PATH,
en el entorno conda activo y en las rutas típicas de Anaconda. Si no encuentra ninguno,
levanta el servidor con PowerShell, que viene incluido en Windows. En los dos casos
queda en `http://localhost:8000`. Deja esa ventana abierta mientras uses el tablero.

Si nada de eso funciona, abre **ABRIR_SIN_SERVIDOR.html** con doble clic: es el mismo
tablero con los datos incrustados, no necesita servidor. La contra es que no lee la
carpeta `data`, así que para cambiar los datos hay que arrastrarle el archivo.

No abras `index.html` con doble clic: el navegador bloquea la lectura de la carpeta
`data` cuando la página no viene de un servidor, y el tablero aparecería vacío.

Requiere conexión a internet: el fondo cartográfico y las librerías del mapa se
descargan en línea.

## Actualizar los datos

Hay dos caminos y los dos funcionan:

**Permanente.** Edita `data/datos_rufe.csv` en Excel y guárdalo como CSV UTF-8.
Las columnas son `codigo_divipola`, `municipio`, `aro`, `registros_rufe`. Refresca el
navegador y el tablero queda actualizado para todos los que usen esa carpeta.

**De una sola vez.** Arrastra un `.xlsx` o `.csv` sobre el tablero, o usa el botón
"Cargar archivo". Sirve para mirar un corte distinto sin tocar la carpeta. El tablero
busca en el libro la hoja que tenga una columna de municipio y otra de registros, así
que el consolidado RUFE original funciona tal como sale.

Cambia la fecha de corte, el título y la nota metodológica en `data/config.json`.

## Cómo se construye el mapa de calor

El RUFE se reporta agregado por municipio, sin ubicación intramunicipal. Para el mapa,
el conteo de cada municipio se reparte entre sus centros poblados: **80% en la cabecera
y 20% entre los demás**, en partes iguales. Los municipios que solo tienen cabecera
cartografiada reciben el 100% ahí.

Ese reparto es un supuesto de representación, no un dato. La nota está impresa en el
panel y en la imagen exportada para que viaje con el mapa.

## Controles

- **Áreas de respuesta operativa** — filtra por Norte, Centro y Sur. Se pueden combinar.
- **Incluir Cali y Buenaventura** — concentran el 38,2% del total departamental.
- **Escala de color fija** — fija: siempre referida a los 42 municipios, así los colores
  significan lo mismo entre vistas. Suelta: se recalcula con lo visible, útil para leer
  diferencias entre municipios pequeños.
- **Fondo del mapa** — Claro, Relieve, Satelital y Calles. Ninguno pide API key.
- **Mostrar centros poblados** — los 223 puntos, con las cabeceras destacadas y su
  nombre visible al acercar.
- **Radio del calor** — ajusta el tamaño de la mancha. Es un radio en pantalla, no en
  kilómetros: cambia con el zoom.
- Clic en un municipio, en el ranking o en la tabla para acercarse a él.
- Descarga el CSV de lo que está seleccionado, o el mapa en PNG con su encabezado.

## Verificar el paquete

**VALIDAR.bat** (este sí necesita Python) revisa que estén todos los archivos, que los 42 municipios crucen por
código DIVIPOLA, que cada uno tenga cabecera para el reparto y que los totales cuadren.

## Pendiente de validación

La asignación de cada municipio a un ARO (Norte 18, Centro 13, Sur 11) es una propuesta
geográfica mía, no la distribución oficial. Contrástala con la de UESVALLE y corrige la
columna `aro` del CSV antes de presentar el tablero.
