import tempfile,unittest
from pathlib import Path
import numpy as np
import pandas as pd
from datos import cargar_datos,ENTRADAS
from generar_dataset import generar
class DatosTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/"datos.csv";self.df=generar(200)
    def tearDown(self):self.tmp.cleanup()
    def cargar(self,df):df.to_csv(self.path,index=False);return cargar_datos(self.path)
    def test_semilla_reproducible(self):pd.testing.assert_frame_equal(generar(200),generar(200))
    def test_semilla_distinta(self):self.assertFalse(generar(200,42).equals(generar(200,43)))
    def test_umbral_clases(self):
        d=generar(1000);e=np.where(d.pasajeros<=350,"baja",np.where(d.pasajeros<=800,"media","alta"));self.assertTrue((d.nivel_ocupacion==e).all())
    def test_duplicados(self):
        d=pd.concat([self.df,self.df.iloc[:1]],ignore_index=True);_,a=self.cargar(d);self.assertGreaterEqual(a["duplicados_eliminados"],1)
    def test_columna_faltante(self):
        with self.assertRaisesRegex(ValueError,"Faltan columnas"):self.cargar(self.df.drop(columns="hora"))
    def test_nulos(self):
        self.df.loc[0,"hora"]=float("nan")
        with self.assertRaisesRegex(ValueError,"faltantes"):self.cargar(self.df)
    def test_rango(self):
        self.df.loc[0,"hora"]=24
        with self.assertRaisesRegex(ValueError,"fuera de rango"):self.cargar(self.df)
    def test_etiqueta_incoherente(self):
        self.df.loc[0,"pasajeros"]=0;self.df.loc[0,"nivel_ocupacion"]="alta"
        with self.assertRaisesRegex(ValueError,"incoherente"):self.cargar(self.df)
    def test_sin_fuga_pasajeros(self):self.assertNotIn("pasajeros",ENTRADAS);self.assertNotIn("nivel_ocupacion",ENTRADAS)

from clustering import preparar,perfiles_estacion,COLUMNAS
class AgrupamientoTest(unittest.TestCase):
    def test_carga_sin_variable_objetivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"sin_etiqueta.csv";generar(500).drop(columns="nivel_ocupacion").to_csv(p,index=False)
            d,a=cargar_datos(p,exigir_etiqueta=False);self.assertNotIn("nivel_ocupacion",d.columns);self.assertGreater(len(d),0)

    def test_etiquetas_no_cambian_matriz(self):
        d=generar(500);_,a,_=preparar(d);d["nivel_ocupacion"]="etiqueta ignorada";_,b,_=preparar(d);np.testing.assert_array_equal(a,b);self.assertNotIn("nivel_ocupacion",COLUMNAS)
    def test_escalado(self):
        _,a,_=preparar(generar(500));np.testing.assert_allclose(a.mean(axis=0),0,atol=1e-12);np.testing.assert_allclose(a.std(axis=0),1,atol=1e-12)
    def test_perfiles_incompletos(self):
        d=generar(500);d["lluvia"]=0
        with self.assertRaisesRegex(ValueError,"incompletos"):perfiles_estacion(d)
    def test_escenarios_insuficientes(self):
        d=pd.concat([generar(30).iloc[:1]]*40,ignore_index=True)
        with self.assertRaisesRegex(ValueError,"nueve escenarios"):preparar(d)
