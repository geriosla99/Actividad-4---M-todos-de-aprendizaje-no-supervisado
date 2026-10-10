"""Aprendizaje NO supervisado: segmentación de la demanda en transporte masivo.
1) K-Means sobre registros (estación-hora-día) para encontrar patrones de demanda.
2) Clustering jerárquico sobre perfiles por estación (dendrograma).
Sin variable objetivo: no se usa 'nivel_ocupacion'."""
import os
import matplotlib
matplotlib.use("Agg")
os.makedirs("docs", exist_ok=True)
os.makedirs("data", exist_ok=True)
import matplotlib.pyplot as plt
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# 1. Carga ---------------------------------------------------------------------
df = pd.read_csv("dataset_transporte.csv").dropna().drop_duplicates()
print(df.shape); print(df.describe())

# 2. Variables numéricas y escalado (K-Means es sensible a la escala) ----------
# Se combinan día/festivo en una sola variable y se excluyen las binarias raras
# (evento_especial): con ellas K-Means solo separa el 5 % de registros con evento.
df["no_laborable"] = ((df["dia_semana"] >= 5) | (df["es_festivo"] == 1)).astype(int)
cols = ["hora", "no_laborable", "pasajeros"]
X = StandardScaler().fit_transform(df[cols])

# 3. Elegir k: método del codo + coeficiente de silueta ------------------------
ks = range(3, 9)  # k>=3 para obtener segmentos con sentido
inercia, sil = [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    inercia.append(km.inertia_)
    sil.append(silhouette_score(X, km.labels_, sample_size=3000, random_state=42))
    print(f"k={k}  inercia={km.inertia_:.0f}  silueta={sil[-1]:.3f}")

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(list(ks), inercia, "o-"); ax[0].set_title("Método del codo"); ax[0].set_xlabel("k")
ax[1].plot(list(ks), sil, "o-"); ax[1].set_title("Silueta"); ax[1].set_xlabel("k")
plt.tight_layout(); plt.savefig("docs/codo_silueta.png", dpi=150); plt.close()

K = list(ks)[sil.index(max(sil))]   # k con mejor silueta (pueden ajustarlo con el codo)
print(f"\nk elegido: {K}")

# 4. Modelo final y perfil de cada cluster --------------------------------------
df["cluster"] = KMeans(n_clusters=K, n_init=10, random_state=42).fit_predict(X)
perfil = df.groupby("cluster")[cols].mean().round(2)
perfil["registros"] = df["cluster"].value_counts().sort_index()
print("\nPerfil de clusters:\n", perfil)
perfil.to_csv("docs/perfil_clusters.csv")

# 5. Visualización en 2D con PCA ------------------------------------------------
pca = PCA(n_components=2, random_state=42)
Z = pca.fit_transform(X)
plt.figure(figsize=(7, 5))
plt.scatter(Z[:, 0], Z[:, 1], c=df["cluster"], cmap="tab10", s=8, alpha=0.6)
plt.title(f"K-Means (k={K}) en 2D con PCA — var. explicada {pca.explained_variance_ratio_.sum():.0%}")
plt.xlabel("PC1"); plt.ylabel("PC2"); plt.tight_layout()
plt.savefig("docs/clusters_pca.png", dpi=150); plt.close()

# 6. Clustering jerárquico: perfil por estación ---------------------------------
laborable = df[(df["dia_semana"] < 5) & (df["es_festivo"] == 0)]
pico = laborable["hora"].between(6, 8) | laborable["hora"].between(17, 19)
est = pd.DataFrame({
    "pasajeros_pico": laborable[pico].groupby("estacion")["pasajeros"].mean(),
    "pasajeros_valle": laborable[~pico].groupby("estacion")["pasajeros"].mean(),
    "pasajeros_finde": df[df["dia_semana"] >= 5].groupby("estacion")["pasajeros"].mean(),
    "efecto_lluvia": df.groupby(["estacion", "lluvia"])["pasajeros"].mean().unstack().pipe(lambda t: t[1] / t[0]),
})
Xe = StandardScaler().fit_transform(est)
est["grupo"] = AgglomerativeClustering(n_clusters=3, linkage="ward").fit_predict(Xe)
print("\nGrupos de estaciones:\n", est.round(2))
est.round(2).to_csv("docs/grupos_estaciones.csv")

plt.figure(figsize=(8, 4))
dendrogram(linkage(Xe, method="ward"), labels=est.index.tolist(), leaf_rotation=45)
plt.title("Dendrograma de estaciones (Ward)"); plt.tight_layout()
plt.savefig("docs/dendrograma_estaciones.png", dpi=150)