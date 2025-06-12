import pandas as pd
import os
import json

class Paciente:
    
    # Ruta del dataset JSON
    Dataset_hospital = os.path.join('Data', 'dataset_hospital 2.json')

    def __init__(self, id_paciente, nombre, fecha_nacimiento, edad, sexo, email, telefono, ciudad):
        self.id_paciente = id_paciente
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        self.edad = edad
        self.sexo = sexo
        self.email = email
        self.telefono = telefono
        self.ciudad = ciudad

    @classmethod
    def from_dict(cls, data):
        """Crear un objeto Paciente desde un diccionario JSON"""
        return cls(
            data.get('id_paciente'),
            data.get('nombre'),
            data.get('fecha_nacimiento'),
            data.get('edad'),
            data.get('sexo'),
            data.get('email'),
            data.get('telefono'),
            data.get('ciudad')
        )
    
    @classmethod
    def cargar_pacientes(cls):
        """Carga el archivo JSON y devuelve una lista de objetos Paciente y un DataFrame"""
        with open(cls.Dataset_hospital, 'r', encoding='utf-8') as file:
            data_json = json.load(file)
        lista_pacientes = [cls.from_dict(p) for p in data_json['pacientes']]
        df_pacientes = pd.DataFrame(data_json['pacientes'])
        return lista_pacientes, df_pacientes
    
    @staticmethod
    def corregir_fecha(fecha):
        """Corrige fechas no estándar como '02 de nov de 1977' a formato 'YYYY-MM-DD'"""
        meses = {
            'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
        }
        try:
            if '-' in fecha and fecha.count('-') == 2:  # formato normal
                return fecha
            else:
                partes = fecha.lower().replace('de', '').split()
                dia = partes[0].zfill(2) #rellena con ceros a la izquierda
                mes = meses.get(partes[1][:3], '01')  # toma las primeras 3 letras
                anio = partes[2]
                return f"{anio}-{mes}-{dia}"
        except Exception:
            return fecha  # si falla devuelve la original

    @staticmethod
    def calcular_edad(fecha_nacimiento):
        if pd.isna(fecha_nacimiento):
            return None
        fecha_nac = pd.to_datetime(fecha_nacimiento, errors='coerce')
        hoy = pd.to_datetime('today')
        if pd.isna(fecha_nac):
            return None
        return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))

    @classmethod
    def agregar_edad_al_df(cls, df):
        """Agrega columna 'edad_calculada' al DataFrame calculando la edad de cada paciente"""
        df['edad_calculada'] = df['fecha_nacimiento'].apply(cls.calcular_edad)
        return df

    @staticmethod
    def corregir_sexo(row):
        nombre = row['nombre']  # pasar todo a minúsculas
        
        nombres_masculinos = ['Carlos', 'Juan']   # agrega aquí todos los que quieras
        nombres_femeninos = ['Claudia', 'María', 'Andrea']     # agrega aquí los femeninos

        if any(n in nombre for n in nombres_masculinos):
            return 'Masculino'
        elif any(n in nombre for n in nombres_femeninos):
            return 'Femenino'
        else:
            return row['sexo']  # deja el sexo original si no coincide
        
    @staticmethod
    def limpiar_telefono(telefono):
        """Limpia el número de teléfono eliminando guiones, si no es None."""
        if isinstance(telefono, str):
            return telefono.replace('-', '')
        return telefono

