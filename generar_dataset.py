"""Muestra SIMULADA del Metro de Medellín. No son mediciones de operación."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import pandas as pd
BASE=Path(__file__).resolve().parent
# Estaciones del modelo académico de la Actividad 2. Bases elegidas para simulación.
ESTACIONES=[("Niquía","Línea A",380), ("Acevedo","Línea A",490),
 ("San Antonio","Línea A",560), ("Poblado","Línea A",430),
 ("Itagüí","Línea A",310), ("La Estrella","Línea A",280),
 ("Estadio","Línea B",330), ("San Javier","Línea B",420)]

def generar(n=5000, semilla=42):
    if n < 30: raise ValueError("Se requieren al menos 30 escenarios")
    rng=np.random.default_rng(semilla); rows=[]
    for _ in range(n):
        estacion,linea,base=ESTACIONES[int(rng.integers(len(ESTACIONES)))]
        hora=int(rng.integers(5,22));dia=int(rng.integers(0,7))
        festivo=int(rng.random()<.06);lluvia=int(rng.random()<.25);evento=int(rng.random()<.05)
        laborable=dia<5 and not festivo
        pico=6<=hora<=8 or 17<=hora<=19
        f_hora=2.4 if pico and laborable else (1.2 if 10<=hora<=16 else .55)
        f_dia=1 if laborable else .70
        # Efectos hipotéticos, no calibrados ni causales. Ruido lognormal positivo.
        mu=base*f_hora*f_dia*(.86 if lluvia else 1)*(1.45 if evento else 1)
        pasajeros=max(20,int(round(mu*rng.lognormal(-.5*.22**2,.22))))
        nivel="baja" if pasajeros<=350 else "media" if pasajeros<=800 else "alta"
        rows.append([estacion,hora,dia,festivo,lluvia,evento,linea,pasajeros,nivel])
    return pd.DataFrame(rows,columns=["estacion","hora","dia_semana","es_festivo","lluvia","evento_especial","linea","pasajeros","nivel_ocupacion"])

def guardar(salida=BASE/"dataset_transporte.csv", n=5000, semilla=42):
    salida=Path(salida);salida.parent.mkdir(parents=True,exist_ok=True)
    generar(n,semilla).to_csv(salida,index=False,lineterminator="\n")
    meta={"tipo":"sintetico", "sistema":"Metro de Medellín", "unidad":"escenario de demanda por estación y franja de una hora",
          "filas":n,"semilla":semilla,"generador":"numpy.default_rng", "numpy":np.__version__,
          "sha256":hashlib.sha256(salida.read_bytes()).hexdigest(),
          "advertencia":"No contiene mediciones oficiales ni capacidad física de trenes. No usar para decisiones operativas.",
          "umbrales_academicos":{"baja":"0 a 350", "media":"351 a 800", "alta":"801 o más"},
          "referencia_estaciones":"https://github.com/Dumo04/actividad2-rutas-metro-medellin/blob/main/conocimiento/metro_medellin.kb"}
    salida.with_suffix(".metadata.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Datos simulados guardados: {salida}; filas={n}; semilla={semilla}")
    return meta
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--salida",type=Path,default=BASE/"dataset_transporte.csv");p.add_argument("--filas",type=int,default=5000);p.add_argument("--semilla",type=int,default=42);a=p.parse_args();guardar(a.salida,a.filas,a.semilla)
