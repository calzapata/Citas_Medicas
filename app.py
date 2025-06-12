import streamlit as st
import pandas as pd
import plotly.express as px
from Models.pacientes import Paciente

def main():

    # TÍTULO DE LA APP
    st.title("Visualización y Procesamiento de Datos de Pacientes")

    # CARGA DE DATOS
    _, df_pacientes_original = Paciente.cargar_pacientes()

    # Procesamiento de datos corregidos
    df_pacientes = df_pacientes_original.copy()

    if 'edad' in df_pacientes.columns:
        df_pacientes = df_pacientes.drop(columns=['edad'])

    df_pacientes['sexo'] = df_pacientes.apply(Paciente.corregir_sexo, axis=1)
    df_pacientes['telefono'] = df_pacientes['telefono'].apply(Paciente.limpiar_telefono)
    df_pacientes['fecha_nacimiento'] = df_pacientes['fecha_nacimiento'].apply(Paciente.corregir_fecha)
    df_pacientes = Paciente.agregar_edad_al_df(df_pacientes)

    # ___________SIDEBAR__________________________
    st.sidebar.title("Opciones de Filtro")

    opcion_df = st.sidebar.radio("¿Con qué tabla deseas trabajar?", ('Original', 'Corregida'))
    df_para_metricas = df_pacientes_original if opcion_df == 'Original' else df_pacientes

    # Filtros
    ciudades_disponibles = df_para_metricas['ciudad'].dropna().unique().tolist()
    ciudad_seleccionada = st.sidebar.multiselect("Filtrar por Ciudad:", ciudades_disponibles, default=ciudades_disponibles)

    if 'sexo' in df_para_metricas.columns:
        sexos_disponibles = df_para_metricas['sexo'].dropna().unique().tolist()
        sexo_seleccionado = st.sidebar.multiselect("Filtrar por Sexo:", sexos_disponibles, default=sexos_disponibles)
    else:
        sexo_seleccionado = []

    if 'edad_calculada' in df_para_metricas.columns:
        edad_min = int(df_para_metricas['edad_calculada'].min())
        edad_max = int(df_para_metricas['edad_calculada'].max())
        rango_edad = st.sidebar.slider("Rango de Edad:", edad_min, edad_max, (edad_min, edad_max))
    else:
        rango_edad = (0, 200)

    # APLICAR FILTROS
    df_filtrado = df_para_metricas[
        (df_para_metricas['ciudad'].isin(ciudad_seleccionada)) &
        (df_para_metricas['sexo'].isin(sexo_seleccionado))
    ]

    if 'edad_calculada' in df_filtrado.columns:
        df_filtrado = df_filtrado[
            (df_filtrado['edad_calculada'] >= rango_edad[0]) &
            (df_filtrado['edad_calculada'] <= rango_edad[1])
        ]

    # MOSTRAR DATOS FILTRADOS
    st.subheader("Datos Filtrados:")
    st.dataframe(df_filtrado)

    st.subheader("Resumen General de Datos:")
    total_pacientes_df = len(df_para_metricas)
    col1, _, _ = st.columns(3)
    with col1:
        st.metric(label="Total Pacientes (Tabla Seleccionada)", value=total_pacientes_df)

    # ____________VISUALIZACIONES CON PLOTLY____________
    st.subheader("Métricas de los Pacientes:")

    # Pacientes por Ciudad
    ciudad_counts = df_filtrado['ciudad'].value_counts().reset_index()
    ciudad_counts.columns = ['ciudad', 'count']
    fig_ciudad = px.bar(ciudad_counts, x='ciudad', y='count', labels={'ciudad': 'Ciudad', 'count': 'Número de Pacientes'}, title='Número de Pacientes por Ciudad')
    st.plotly_chart(fig_ciudad)

    # Distribución por Sexo
    if 'sexo' in df_filtrado.columns:
        sexo_counts = df_filtrado['sexo'].value_counts().reset_index()
        sexo_counts.columns = ['sexo', 'count']
        fig_sexo = px.pie(sexo_counts, names='sexo', values='count', title='Distribución de Pacientes por Sexo')
        st.plotly_chart(fig_sexo)

    # Distribución de Edades
    if 'edad_calculada' in df_filtrado.columns:
        fig_edad = px.histogram(df_filtrado, x='edad_calculada', nbins=10, title='Distribución de Edades de Pacientes', labels={'edad_calculada': 'Edad'})
        st.plotly_chart(fig_edad)

    # ____________MAPA DE CALOR POR CIUDAD (NUEVO)____________
    st.subheader("Mapa de Citas Médicas por Ciudad (Colombia)")

    # Coordenadas de ciudades principales
    coordenadas_ciudades = {
        'Bogotá': {'lat': 4.7110, 'lon': -74.0721},
        'Medellín': {'lat': 6.2442, 'lon': -75.5812},
        'Cali': {'lat': 3.4516, 'lon': -76.5320},
        'Barranquilla': {'lat': 10.9685, 'lon': -74.7813},
        'Cartagena': {'lat': 10.3910, 'lon': -75.4794},
        # Agrega más si es necesario
    }

    ciudad_counts['lat'] = ciudad_counts['ciudad'].apply(lambda x: coordenadas_ciudades.get(x, {}).get('lat', None))
    ciudad_counts['lon'] = ciudad_counts['ciudad'].apply(lambda x: coordenadas_ciudades.get(x, {}).get('lon', None))
    ciudad_counts = ciudad_counts.dropna(subset=['lat', 'lon'])  # eliminamos ciudades sin coordenadas

    # Mapa
    fig_mapa = px.scatter_mapbox(
        ciudad_counts,
        lat='lat',
        lon='lon',
        size='count',
        color='count',
        hover_name='ciudad',
        size_max=30,
        zoom=4,
        mapbox_style="carto-positron",
        title="Mapa de Citas Médicas por Ciudad en Colombia"
    )
    st.plotly_chart(fig_mapa)

    # DESCARGA DEL RESULTADO
    st.subheader("Descargar Datos Filtrados:")
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(label="Descargar CSV Filtrado", data=csv, file_name='pacientes_filtrados.csv', mime='text/csv')

if __name__ == "__main__":
    main()
