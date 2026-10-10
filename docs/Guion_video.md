# Guion del video — Actividad 4

Santiago Duque Mora y Geraldine Ríos. Video separado. Duración estimada de lectura: 6 a 8 minutos con pausas; comprobar duración al montar. Máximo: 10 minutos.

Guion para revisión. Las indicaciones de pantalla sirven para el montaje y no se leen en voz alta. Las cifras corresponden a los resultados guardados en el repositorio.

## 01 · Santiago · Presentación

Pantalla: README.md

Somos Santiago Duque Mora y Geraldine Ríos. Esta es la Actividad 4, sobre aprendizaje no supervisado. Continuamos con el Metro de Medellín y la misma muestra usada en la Actividad 3. Esta vez no queremos predecir una clase conocida: buscamos grupos de escenarios y estaciones que compartan características de demanda.

## 02 · Geraldine · Datos y continuidad

Pantalla: dataset_transporte.csv y Descripcion_datos.pdf

Trabajamos con cinco mil escenarios simulados de ocho estaciones. Tras retirar veintisiete duplicados exactos quedan cuatro mil novecientos setenta y tres filas. La fórmula y la semilla están documentadas. Las cifras no son observaciones oficiales. Cada fila describe una estación y una franja horaria, con variables que permiten comparar distintos escenarios de demanda.

## 03 · Santiago · Ejecución

Pantalla: clustering.py y docs/resultados/ejecucion.txt

Después de instalar las dependencias, ejecutamos python clustering punto py. El programa carga y valida los datos, crea la carpeta de salida y produce los perfiles, las gráficas y las métricas. Las pantallas de este video corresponden a esas salidas reales. También podemos indicar otra ruta de datos o de resultados mediante los argumentos que aparecen en el archivo de instrucciones.

## 04 · Geraldine · Variables y escalado

Pantalla: clustering.py: preparar y COLUMNAS

Para K medias seleccionamos hora, pasajeros y una variable que indica si el día es no laborable. Esta última combina fines de semana y festivos. No utilizamos nivel de ocupación y el programa funciona incluso cuando esa columna no existe. Estandarizamos las tres variables para que la escala numérica de pasajeros no domine únicamente por sus unidades. La variable no laborable tiene una influencia fuerte en los grupos y debemos tenerla en cuenta al interpretar.

## 05 · Santiago · Elección del número de grupos

Pantalla: docs/resultados/codo_silueta.png

Evaluamos entre dos y ocho grupos. El método del codo muestra cómo disminuye la inercia al añadir grupos. También calculamos la silueta, que compara la cercanía de cada ejemplo a su grupo frente a otros. Entre los valores probados, siete grupos obtienen la mejor silueta, aproximadamente cero coma cuatrocientos ochenta y cinco. Esto no prueba un número perfecto para cualquier conjunto de datos; es la mejor opción según este criterio y este intervalo.

## 06 · Geraldine · Perfiles y proyección

Pantalla: perfil_clusters.csv y clusters_pca.png

Los perfiles permiten describir los grupos con sus unidades originales. Por ejemplo, un grupo reúne escenarios laborables de la mañana, con una hora media cercana a siete coma dos y alrededor de mil veinticuatro pasajeros. Otro reúne escenarios laborables de la tarde, cerca de las dieciocho horas y mil ciento dieciocho pasajeros. Los identificadores de los grupos son arbitrarios: no son etiquetas baja, media o alta. La proyección con componentes principales ayuda a ver los grupos en dos dimensiones, pero el modelo se entrenó con las tres variables estandarizadas.

## 07 · Santiago · Agrupamiento de estaciones

Pantalla: dendrograma_estaciones.png y grupos_estaciones.csv

También construimos un perfil por estación con demanda media en pico, valle y fin de semana, además de la razón descriptiva entre escenarios con y sin lluvia. Aplicamos agrupamiento jerárquico con enlace Ward. El dendrograma muestra cómo se van uniendo las estaciones. Elegimos tres grupos para explorar sus diferencias, sin afirmar que ese número sea óptimo. La razón de lluvia no demuestra un efecto causal y todos los perfiles siguen dependiendo de la simulación.

## 08 · Geraldine · Pruebas y estabilidad

Pantalla: docs/resultados/pruebas.txt y metricas.json

Ejecutamos catorce pruebas automatizadas y todas pasaron. Verifican la carga de datos, el escalado, la ejecución sin etiqueta objetivo y el rechazo de perfiles incompletos. Cambiar las etiquetas no altera la matriz utilizada para agrupar. Además, comparamos particiones obtenidas con otras tres semillas mediante el índice Rand ajustado. Esta comparación evalúa estabilidad ante la inicialización; no compara con una verdad de grupos que no tenemos.

## 09 · Santiago · Conclusión

Pantalla: PDF de pruebas y enlaces de entrega

El componente permite explorar patrones sin una respuesta etiquetada. Se entregan los datos, el código, la descripción, las pruebas y las visualizaciones. Los grupos son útiles para comprender el método, pero no justifican decisiones operativas reales. El siguiente paso sería obtener mediciones verificadas y evaluar si estos perfiles se mantienen en el tiempo.

## 10 · Geraldine · Cierre

Pantalla: Repositorio

La diferencia con la Actividad 3 es el objetivo: allí clasificamos ejemplos con etiquetas; aquí descubrimos agrupaciones a partir de sus características. Ambos ejercicios continúan el proyecto del Metro de Medellín. Gracias.
