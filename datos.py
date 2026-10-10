"""Carga y validación compartidas por los dos componentes académicos."""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

CATEGORICAS = ["estacion", "linea"]
NUMERICAS = ["hora", "dia_semana", "es_festivo", "lluvia", "evento_especial"]
ENTRADAS = CATEGORICAS + NUMERICAS
CLASES = ["baja", "media", "alta"]

def cargar_datos(ruta, exigir_etiqueta=True):
    ruta = Path(ruta)
    df = pd.read_csv(ruta).rename(columns={"troncal": "linea"})
    requeridas = ENTRADAS + ["pasajeros"] + (["nivel_ocupacion"] if exigir_etiqueta else [])
    faltan = set(requeridas) - set(df.columns)
    if faltan:
        raise ValueError(f"Faltan columnas: {sorted(faltan)}")
    if df[requeridas].isna().any().any():
        raise ValueError("Hay valores faltantes; corregir la fuente antes de entrenar.")
    for col in CATEGORICAS:
        if not df[col].map(lambda x: isinstance(x, str) and bool(x.strip())).all():
            raise ValueError(f"Categoría vacía o inválida en {col}")
    for col in NUMERICAS + ["pasajeros"]:
        values = pd.to_numeric(df[col], errors="coerce")
        if not np.isfinite(values).all() or not (values % 1 == 0).all():
            raise ValueError(f"{col} debe contener enteros finitos")
        df[col] = values.astype(int)
    for col, lo, hi in [("hora", 0, 23), ("dia_semana", 0, 6),
                        ("es_festivo", 0, 1), ("lluvia", 0, 1), ("evento_especial", 0, 1)]:
        if not df[col].between(lo, hi).all():
            raise ValueError(f"Valores fuera de rango en {col}")
    if (df.pasajeros < 0).any():
        raise ValueError("Pasajeros no puede ser negativo")
    if exigir_etiqueta and not df.nivel_ocupacion.isin(CLASES).all():
        raise ValueError("Etiqueta fuera de baja/media/alta")
    # Reglas académicas; no representan aforos oficiales.
    esperado = np.where(df.pasajeros <= 350, "baja", np.where(df.pasajeros <= 800, "media", "alta"))
    if exigir_etiqueta and not (df.nivel_ocupacion == esperado).all():
        raise ValueError("Etiqueta incoherente con los umbrales académicos 350 y 800")
    originales = len(df)
    df = df.drop_duplicates(subset=requeridas).reset_index(drop=True)
    if len(df) < 30:
        raise ValueError("Se requieren al menos 30 escenarios válidos")
    auditoria = {"sha256": hashlib.sha256(ruta.read_bytes()).hexdigest(), "filas_originales": originales,
                 "duplicados_eliminados": originales-len(df), "filas_utilizadas": len(df),
                 "estaciones": sorted(df.estacion.unique().tolist()),
                 "clases": df.nivel_ocupacion.value_counts().to_dict() if exigir_etiqueta else {}}
    return df, auditoria
