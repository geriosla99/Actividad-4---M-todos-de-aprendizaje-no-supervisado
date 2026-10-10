"""Aprendizaje no supervisado: demanda del Metro con K-Means y agrupamiento jerárquico."""
from pathlib import Path
import argparse,json,platform
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from scipy.cluster.hierarchy import dendrogram,linkage
from sklearn.cluster import AgglomerativeClustering,KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score,adjusted_rand_score
from sklearn.preprocessing import StandardScaler
from datos import cargar_datos
BASE=Path(__file__).resolve().parent
COLUMNAS=["hora","no_laborable","pasajeros"]

def preparar(df):
    tabla=df.copy()
    tabla["no_laborable"]=((tabla.dia_semana>=5)|(tabla.es_festivo==1)).astype(int)
    escalador=StandardScaler();X=escalador.fit_transform(tabla[COLUMNAS])
    if len(np.unique(X,axis=0)) < 9:raise ValueError("Se requieren al menos nueve escenarios distintos para evaluar k=2..8")
    return tabla,X,escalador

def perfiles_estacion(df):
    lab=df[(df.dia_semana<5)&(df.es_festivo==0)]
    pico=lab.hora.between(6,8)|lab.hora.between(17,19)
    lluvia=df.groupby(["estacion","lluvia"]).pasajeros.mean().unstack().reindex(columns=[0,1])
    est=pd.DataFrame({"pasajeros_pico":lab[pico].groupby("estacion").pasajeros.mean(),
        "pasajeros_valle":lab[~pico].groupby("estacion").pasajeros.mean(),
        "pasajeros_finde":df[df.dia_semana>=5].groupby("estacion").pasajeros.mean(),
        "razon_lluvia":lluvia[1]/lluvia[0]})
    if len(est)<3 or not np.isfinite(est.to_numpy()).all():
        raise ValueError("Perfiles incompletos: cada estación requiere muestras pico, valle, fin de semana, con y sin lluvia")
    return est

def ejecutar(dataset=BASE/"dataset_transporte.csv",salida=BASE/"docs/resultados"):
    salida=Path(salida);salida.mkdir(parents=True,exist_ok=True)
    datos,audit=cargar_datos(dataset, exigir_etiqueta=False);df,X,escalador=preparar(datos)
    tabla=[]
    for k in range(2,9):
        km=KMeans(n_clusters=k,n_init=10,random_state=42).fit(X)
        tabla.append({"k":k,"inercia":km.inertia_,"silueta":silhouette_score(X,km.labels_,sample_size=min(3000,len(X)),random_state=42)})
    evaluacion=pd.DataFrame(tabla);evaluacion.to_csv(salida/"seleccion_k.csv",index=False)
    k=int(evaluacion.loc[evaluacion.silueta.idxmax(),"k"])
    final=KMeans(n_clusters=k,n_init=10,random_state=42).fit(X);df["cluster"]=final.labels_
    perfil=df.groupby("cluster")[COLUMNAS].mean();perfil["registros"]=df.cluster.value_counts().sort_index();perfil.to_csv(salida/"perfil_clusters.csv")
    df.to_csv(salida/"registros_agrupados.csv",index=False)
    estabilidad=[]
    for seed in [7,21,84]:
        otro=KMeans(n_clusters=k,n_init=10,random_state=seed).fit_predict(X)
        estabilidad.append({"semilla":seed,"ari":adjusted_rand_score(final.labels_,otro)})
    fig,ax=plt.subplots(1,2,figsize=(11,4));ax[0].plot(evaluacion.k,evaluacion.inercia,"o-");ax[0].set_title("Método del codo");ax[1].plot(evaluacion.k,evaluacion.silueta,"o-");ax[1].set_title("Silueta (muestra hasta 3000)")
    for a in ax:a.set_xlabel("k")
    plt.tight_layout();plt.savefig(salida/"codo_silueta.png",dpi=150);plt.close()
    pca=PCA(n_components=2,random_state=42);Z=pca.fit_transform(X)
    plt.figure(figsize=(8,5));plt.scatter(Z[:,0],Z[:,1],c=final.labels_,s=8,alpha=.5,cmap="tab10");plt.xlabel("PC1");plt.ylabel("PC2");plt.title(f"K-Means k={k}; PCA retiene {pca.explained_variance_ratio_.sum():.1%}");plt.tight_layout();plt.savefig(salida/"clusters_pca.png",dpi=150);plt.close()
    est=perfiles_estacion(df);Xe=StandardScaler().fit_transform(est)
    # Tres grupos como decisión exploratoria, no óptimo demostrado.
    est["grupo"]=AgglomerativeClustering(n_clusters=3,linkage="ward").fit_predict(Xe)
    est.to_csv(salida/"grupos_estaciones.csv")
    plt.figure(figsize=(9,5));dendrogram(linkage(Xe,method="ward"),labels=est.index.tolist(),leaf_rotation=35);plt.title("Perfiles de estaciones: enlace Ward");plt.tight_layout();plt.savefig(salida/"dendrograma_estaciones.png",dpi=150);plt.close()
    informe={"auditoria":audit,"python":platform.python_version(),"sklearn":sklearn.__version__,"semilla":42,
      "variables":COLUMNAS,"etiqueta_excluida":True,"k_elegido":k,"evaluacion_k":tabla,
      "silueta":float(evaluacion.silueta.max()),"estabilidad":estabilidad,
      "pca_varianza_explicada":float(pca.explained_variance_ratio_.sum()),"grupos_jerarquicos":3,
      "perfiles":perfil.reset_index().to_dict("records"),"estaciones":est.reset_index().to_dict("records"),
      "escala_media":escalador.mean_.tolist(),"escala_desviacion":escalador.scale_.tolist()}
    (salida/"metricas.json").write_text(json.dumps(informe,ensure_ascii=False,indent=2),encoding="utf-8")
    print(evaluacion.to_string(index=False));print(f"k elegido por silueta: {k}");print(perfil.to_string());print(est.to_string());return informe
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--datos",type=Path,default=BASE/"dataset_transporte.csv");p.add_argument("--salida",type=Path,default=BASE/"docs/resultados");a=p.parse_args();ejecutar(a.datos,a.salida)
