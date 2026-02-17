import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Dashboard Transformación Digital",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .metric-card { background: white; padding: 10px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); border-left: 5px solid; margin: 10px 0; transition: transform 0.2s; }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 8px 12px rgba(0,0,0,0.15); }
    .metric-value { font-size: 1.5em; font-weight: 700; font-family: 'Poppins', sans-serif; margin: 10px 0; }
    .metric-label { font-size: 0.60em; color: #666; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }
    .metric-empresas { border-color: #667eea; } .metric-empresas .metric-value { color: #667eea; }
    .metric-municipio { border-color: #f093fb; } .metric-municipio .metric-value { color: #f093fb; }
    .metric-sector { border-color: #4facfe; } .metric-sector .metric-value { color: #4facfe; }
    .metric-horas { border-color: #43e97b; } .metric-horas .metric-value { color: #43e97b; }
    .metric-unique { border-color: #fa709a; } .metric-unique .metric-value { color: #fa709a; }
    h1, h2, h3 { font-family: 'Poppins', sans-serif; color: #2d3748; font-weight: 600; }
    .stMultiSelect label { font-weight: 600; color: #2d3748; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNCIÓN PARA CARGAR DATOS
# ============================================================================
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel('transformacion_completamente_dividido.xlsx')
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo 'transformacion_completamente_dividido.xlsx'")
        st.stop()
    
    df['No_horas_de_consultoría'] = pd.to_numeric(df['No_horas_de_consultoría'], errors='coerce')
    df['Indicador_satisfacción'] = pd.to_numeric(df['Indicador_satisfacción'], errors='coerce')
    df['Indicador_ventas'] = pd.to_numeric(df['Indicador_ventas'], errors='coerce')
    df['Indicador_procesos_tecnologicos'] = pd.to_numeric(df['Indicador_procesos_tecnologicos'], errors='coerce')
    df['Indicador_presencia_en_linea'] = pd.to_numeric(df['Indicador_presencia_en_linea'], errors='coerce')
    
    # Crear identificador único de empresa (prioridad: NIT > Nombre_empresa > Nombre)
    df['empresa_id'] = df['Nit'].fillna(df['Nombre_de_la_empresa']).fillna(df['Nombre'])
    
    return df

@st.cache_data
def cargar_talleres():
    try:
        df_tall = pd.read_excel('Horas_talleres.xlsx')
        df_tall['Fecha_dt'] = pd.to_datetime(df_tall['Fecha '], format='%d-%B-%Y', errors='coerce')
        df_tall['Año'] = df_tall['Fecha_dt'].dt.year
        return df_tall
    except FileNotFoundError:
        return None

df = cargar_datos()
df_talleres = cargar_talleres()

# ============================================================================
# SIDEBAR - FILTROS
# ============================================================================
st.sidebar.image("https://via.placeholder.com/300x100/667eea/ffffff?text=Transformación+Digital", use_container_width=True)
st.sidebar.title("🎯 Filtros")

programas_disponibles = ['Todos'] + sorted([p for p in df['Programa'].dropna().unique() if str(p) != 'NAN'])
programa_seleccionado = st.sidebar.multiselect("📊 Programa", programas_disponibles, ['Todos'])

# NUEVO FILTRO: Fase
fases_disponibles = ['Todos'] + sorted([f for f in df['Fase'].unique() if pd.notna(f) and str(f) != 'NAN'])
fase_seleccionada = st.sidebar.multiselect("🔄 Fase", fases_disponibles, ['Todos'])

cohortes_disponibles = ['Todos'] + sorted([c for c in df['Cohorte'].unique() if pd.notna(c)])
cohorte_seleccionada = st.sidebar.multiselect("📅 Cohorte", cohortes_disponibles, ['Todos'])

# NUEVO FILTRO: Año
años_disponibles = ['Todos'] + sorted([int(a) for a in df['Año_Ejecución'].dropna().unique()])
año_seleccionado = st.sidebar.multiselect("📆 Año", años_disponibles, ['Todos'])

municipios_disponibles = ['Todos'] + sorted([m for m in df['Municipio'].dropna().unique() if str(m) != 'NAN'])
municipio_seleccionado = st.sidebar.multiselect("📍 Municipio", municipios_disponibles, ['Todos'])

sectores_validos = df[(df['Sector'].notna()) & (df['Sector'] != 'NAN')]['Sector'].unique()
sectores_disponibles = ['Todos'] + sorted(sectores_validos.tolist())
sector_seleccionado = st.sidebar.multiselect("🏢 Sector", sectores_disponibles, ['Todos'])

generos_disponibles = ['Todos'] + sorted([g for g in df['Género'].dropna().unique() if str(g) != 'NAN'])
genero_seleccionado = st.sidebar.multiselect("👥 Género", generos_disponibles, ['Todos'])

# ============================================================================
# APLICAR FILTROS
# ============================================================================
df_filtrado = df.copy()

if programa_seleccionado and 'Todos' not in programa_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['Programa'].isin(programa_seleccionado)]
if fase_seleccionada and 'Todos' not in fase_seleccionada:
    df_filtrado = df_filtrado[(df_filtrado['Fase'].isin(fase_seleccionada)) | (df_filtrado['Fase'].isna())]
if cohorte_seleccionada and 'Todos' not in cohorte_seleccionada:
    df_filtrado = df_filtrado[(df_filtrado['Cohorte'].isin(cohorte_seleccionada)) | (df_filtrado['Cohorte'].isna())]
if año_seleccionado and 'Todos' not in año_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['Año_Ejecución'].isin(año_seleccionado)]
if municipio_seleccionado and 'Todos' not in municipio_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['Municipio'].isin(municipio_seleccionado)]
if sector_seleccionado and 'Todos' not in sector_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['Sector'].isin(sector_seleccionado)]
if genero_seleccionado and 'Todos' not in genero_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['Género'].isin(genero_seleccionado)]

# ============================================================================
# MÉTRICAS
# ============================================================================
total_intervenciones = len(df_filtrado)
empresas_unicas = df_filtrado['empresa_id'].nunique()

# Separar Municipios (12) y Corregimientos (1 - Barcelona)
municipios_count = df_filtrado[df_filtrado['Municipio'] != 'BARCELONA']['Municipio'].nunique()
corregimientos_count = 1 if 'BARCELONA' in df_filtrado['Municipio'].values else 0

sectores_atendidos = df_filtrado[(df_filtrado['Sector'].notna()) & (df_filtrado['Sector'] != 'NAN')]['Sector'].nunique()
total_horas = df_filtrado['No_horas_de_consultoría'].sum()

# ============================================================================
# HEADER
# ============================================================================
st.title("🚀 Dashboard Transformación Digital - Cámara de Comercio de Armenia y del Quindío")
st.markdown("---")

# ============================================================================
# MÉTRICAS PRINCIPALES (6 MÉTRICAS)
# ============================================================================
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f'<div class="metric-card metric-empresas"><div class="metric-label">Intervenciones</div><div class="metric-value">{total_intervenciones:,}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card metric-unique"><div class="metric-label">Empresas Únicas</div><div class="metric-value">{empresas_unicas:,}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card metric-municipio"><div class="metric-label">Municipios</div><div class="metric-value">{municipios_count}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card metric-sector"><div class="metric-label">Corregimientos</div><div class="metric-value">{corregimientos_count}</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="metric-card metric-sector"><div class="metric-label">Sectores</div><div class="metric-value">{sectores_atendidos}</div></div>', unsafe_allow_html=True)
with col6:
    st.markdown(f'<div class="metric-card metric-horas"><div class="metric-label">Horas Consultoría</div><div class="metric-value">{total_horas:,.0f}</div></div>', unsafe_allow_html=True)

if total_intervenciones == 0:
    st.warning("⚠️ No hay datos disponibles con los filtros seleccionados")
    st.stop()

st.markdown("---")

# ============================================================================
# SECCIÓN: RESULTADOS - GRÁFICAS
# ============================================================================
st.header("📊 Resultados y Análisis")

# FILA 1: Temas y Género
col1, col2 = st.columns(2)

with col1:
    st.subheader("📚 Fase alcanzada por las empresas")
    tema_data = df_filtrado['Tema'].value_counts()
    tema_pct = (tema_data / tema_data.sum() * 100).round(1)
    fig = go.Figure(go.Pie(labels=tema_data.index, values=tema_pct, customdata=tema_data.values,
                           hovertemplate='<b>%{label}</b><br>Porcentaje: %{value:.1f}%<br>Intervenciones: %{customdata:,}<extra></extra>',
                           textinfo='percent', marker=dict(colors=px.colors.qualitative.Set3, line=dict(color='white', width=2))))
    fig.update_layout(height=500, showlegend=True, font=dict(family="Poppins"), paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20,b=20,l=20,r=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("👥 Distribución por Género")
    genero_data = df_filtrado['Género'].value_counts().reset_index()
    genero_data.columns = ['Género', 'Cantidad']
    colores_genero = {'FEMENINO': '#f093fb', 'MASCULINO': '#4facfe', 'NO APLICA': '#a8edea'}
    fig = px.pie(genero_data, values='Cantidad', names='Género', hole=0.4, color='Género', color_discrete_map=colores_genero)
    fig.update_layout(height=500, font=dict(family="Poppins"), paper_bgcolor='rgba(0,0,0,0)', showlegend=True)
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
    st.plotly_chart(fig, use_container_width=True)

# FILA 2: Horas y Municipios (INTERVENCIONES)
col1, col2 = st.columns(2)

with col1:
    st.subheader("⏱️ Distribución de Horas de Consultoría")
    horas_por_tema = df_filtrado.groupby('Tema')['No_horas_de_consultoría'].sum()
    horas_pct = (horas_por_tema / horas_por_tema.sum() * 100).round(1)
    fig = go.Figure(go.Pie(labels=horas_por_tema.index, values=horas_pct, customdata=horas_por_tema.values,
                           hovertemplate='<b>%{label}</b><br>Porcentaje: %{value:.1f}%<br>Horas: %{customdata:,.0f}<extra></extra>',
                           textinfo='percent', marker=dict(colors=px.colors.qualitative.Pastel, line=dict(color='white', width=2))))
    fig.update_layout(height=500, showlegend=True, font=dict(family="Poppins"), paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20,b=20,l=20,r=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📍 Intervenciones por Municipio")
    municipio_data = df_filtrado['Municipio'].value_counts()
    municipio_pct = (municipio_data / municipio_data.sum() * 100).round(1)
    fig = go.Figure(go.Pie(labels=municipio_data.index, values=municipio_pct, customdata=municipio_data.values,
                           hovertemplate='<b>%{label}</b><br>Porcentaje: %{value:.1f}%<br>Intervenciones: %{customdata:,}<extra></extra>',
                           textinfo='percent', marker=dict(colors=px.colors.qualitative.Bold, line=dict(color='white', width=2))))
    fig.update_layout(height=500, showlegend=True, font=dict(family="Poppins"), paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20,b=20,l=20,r=20))
    st.plotly_chart(fig, use_container_width=True)

# FILA 3: Sectores y Programas (INTERVENCIONES)
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏢 Top 10 Sectores Atendidos")
    sector_data = df_filtrado[(df_filtrado['Sector'].notna()) & (df_filtrado['Sector'] != 'NAN')]['Sector'].value_counts().head(10)
    if len(sector_data) > 0:
        sector_pct = (sector_data / df_filtrado[(df_filtrado['Sector'].notna()) & (df_filtrado['Sector'] != 'NAN')]['Sector'].value_counts().sum() * 100).round(1)
        fig = go.Figure(go.Pie(labels=sector_data.index, values=sector_pct, customdata=sector_data.values,
                               hovertemplate='<b>%{label}</b><br>Porcentaje: %{value:.1f}%<br>Intervenciones: %{customdata:,}<extra></extra>',
                               textinfo='percent', marker=dict(colors=px.colors.qualitative.Vivid, line=dict(color='white', width=2))))
        fig.update_layout(height=500, showlegend=True, font=dict(family="Poppins"), paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📋 Distribución por Programa")
    programa_data = df_filtrado['Programa'].value_counts()
    programa_pct = (programa_data / programa_data.sum() * 100).round(1)
    fig = go.Figure(go.Pie(labels=programa_data.index, values=programa_pct, customdata=programa_data.values,
                           hovertemplate='<b>%{label}</b><br>Porcentaje: %{value:.1f}%<br>Intervenciones: %{customdata:,}<extra></extra>',
                           textinfo='percent', marker=dict(colors=px.colors.qualitative.Safe, line=dict(color='white', width=2))))
    fig.update_layout(height=500, showlegend=True, font=dict(family="Poppins"), paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20,b=20,l=20,r=20))
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# NUEVAS GRÁFICAS: EMPRESAS POR MUNICIPIO Y SECTOR
# ============================================================================
st.markdown("---")
st.header("🏢 Análisis de Empresas")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Empresas por Municipio")
    empresas_municipio = df_filtrado.groupby('Municipio')['empresa_id'].nunique().sort_values(ascending=True)
    
    fig = go.Figure(go.Bar(
        y=empresas_municipio.index,
        x=empresas_municipio.values,
        orientation='h',
        marker=dict(
            color=empresas_municipio.values,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Empresas")
        ),
        text=empresas_municipio.values,
        texttemplate='%{text:,}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Empresas únicas: %{x:,}<extra></extra>'
    ))
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Poppins"),
        xaxis=dict(title="Número de Empresas", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(title=""),
        margin=dict(t=20,b=20,l=20,r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏢 Empresas por Sector")
    empresas_sector = df_filtrado[(df_filtrado['Sector'].notna()) & (df_filtrado['Sector'] != 'NAN')].groupby('Sector')['empresa_id'].nunique().sort_values(ascending=True)
    
    fig = go.Figure(go.Bar(
        y=empresas_sector.index,
        x=empresas_sector.values,
        orientation='h',
        marker=dict(
            color=empresas_sector.values,
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Empresas")
        ),
        text=empresas_sector.values,
        texttemplate='%{text:,}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Empresas únicas: %{x:,}<extra></extra>'
    ))
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Poppins"),
        xaxis=dict(title="Número de Empresas", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(title=""),
        margin=dict(t=20,b=20,l=20,r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
# INTERVENCIONES POR EMPRESA
# ============================================================================
st.header("📊 Análisis de Intervenciones por Empresa")

# USAR empresa_id (que ya está creado en el dataset) para cálculos correctos
df_filtrado_empresas = df_filtrado.copy()

# Contar intervenciones por empresa_id (el identificador único correcto)
intervenciones_por_empresa_id = df_filtrado_empresas.groupby('empresa_id').size().sort_values(ascending=False)

# Para mostrar nombres en las gráficas, crear diccionario empresa_id -> nombre
df_filtrado_empresas['empresa_nombre'] = df_filtrado_empresas['Nombre_de_la_empresa'].fillna(df_filtrado_empresas['Nombre'])
empresa_id_to_nombre = df_filtrado_empresas.groupby('empresa_id')['empresa_nombre'].first()

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

total_empresas_con_interv = len(intervenciones_por_empresa_id)
promedio_interv = intervenciones_por_empresa_id.mean()
mediana_interv = intervenciones_por_empresa_id.median()
max_interv = intervenciones_por_empresa_id.max()

with col1:
    st.markdown(f'<div class="metric-card metric-empresas"><div class="metric-label">Empresas Analizadas</div><div class="metric-value">{total_empresas_con_interv:,}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card metric-unique"><div class="metric-label">Promedio Intervenciones</div><div class="metric-value">{promedio_interv:.1f}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card metric-municipio"><div class="metric-label">Mediana Intervenciones</div><div class="metric-value">{mediana_interv:.0f}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card metric-horas"><div class="metric-label">Máximo Intervenciones</div><div class="metric-value">{max_interv}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Gráficas
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Top 15 Empresas con Más Intervenciones")
    
    # Obtener top 15 por empresa_id
    top_15_ids = intervenciones_por_empresa_id.head(15)
    # Mapear a nombres para mostrar
    top_15_nombres = top_15_ids.index.map(lambda x: str(empresa_id_to_nombre.get(x, x))[:50])
    top_15_valores = top_15_ids.values
    
    # Ordenar de menor a mayor para gráfica horizontal
    orden = np.argsort(top_15_valores)
    top_15_nombres_ordenado = top_15_nombres[orden]
    top_15_valores_ordenado = top_15_valores[orden]
    
    fig = go.Figure(go.Bar(
        y=top_15_nombres_ordenado,
        x=top_15_valores_ordenado,
        orientation='h',
        marker=dict(
            color=top_15_valores_ordenado,
            colorscale='Teal',
            showscale=False
        ),
        text=top_15_valores_ordenado,
        texttemplate='%{text}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Intervenciones: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Poppins"),
        xaxis=dict(title="Número de Intervenciones", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(title="", tickfont=dict(size=10)),
        margin=dict(t=20,b=20,l=200,r=80)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 Distribución de Intervenciones por Empresa")
    
    # Crear rangos de distribución usando empresa_id
    bins = [1, 2, 5, 10, 20, 50, float('inf')]
    labels = ['1 intervención', '2-4 intervenciones', '5-9 intervenciones', '10-19 intervenciones', '20-49 intervenciones', '50+ intervenciones']
    rangos = pd.cut(intervenciones_por_empresa_id, bins=bins, labels=labels, right=False)
    distribucion = rangos.value_counts().sort_index()
    
    fig = go.Figure(data=[
        go.Bar(
            x=distribucion.index,
            y=distribucion.values,
            marker=dict(
                color=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a']
            ),
            text=distribucion.values,
            texttemplate='%{text:,}<br>empresas',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Empresas: %{y:,}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Poppins"),
        xaxis=dict(title="", tickangle=-45),
        yaxis=dict(title="Número de Empresas", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        showlegend=False,
        margin=dict(t=20,b=100,l=20,r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Información adicional en cards
col1, col2, col3 = st.columns(3)

empresas_1_interv = (intervenciones_por_empresa_id == 1).sum()
pct_1_interv = (empresas_1_interv / total_empresas_con_interv * 100)

empresas_10_mas = (intervenciones_por_empresa_id >= 10).sum()
pct_10_mas = (empresas_10_mas / total_empresas_con_interv * 100)

empresas_recurrentes = (intervenciones_por_empresa_id >= 5).sum()
pct_recurrentes = (empresas_recurrentes / total_empresas_con_interv * 100)

empresas_10_mas = (intervenciones_por_empresa_id >= 10).sum()
pct_10_mas = (empresas_10_mas / total_empresas_con_interv * 100)

empresas_recurrentes = (intervenciones_por_empresa_id >= 5).sum()
pct_recurrentes = (empresas_recurrentes / total_empresas_con_interv * 100)

with col1:
    st.markdown(f"""
    <div style='background:#fff3cd; padding:15px; border-radius:10px; border-left:5px solid #ffc107; margin-top:10px;'>
        <p style='margin:0; font-size:0.9em; color:#856404;'>
            <b>📌 Empresas con 1 intervención:</b><br>
            <span style='font-size:1.5em; font-weight:700; color:#d39e00;'>{empresas_1_interv:,}</span> 
            <span style='font-size:0.85em;'>({pct_1_interv:.1f}%)</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background:#d1ecf1; padding:15px; border-radius:10px; border-left:5px solid #17a2b8; margin-top:10px;'>
        <p style='margin:0; font-size:0.9em; color:#0c5460;'>
            <b>🔄 Empresas recurrentes (5+):</b><br>
            <span style='font-size:1.5em; font-weight:700; color:#117a8b;'>{empresas_recurrentes:,}</span> 
            <span style='font-size:0.85em;'>({pct_recurrentes:.1f}%)</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background:#d4edda; padding:15px; border-radius:10px; border-left:5px solid #28a745; margin-top:10px;'>
        <p style='margin:0; font-size:0.9em; color:#155724;'>
            <b>⭐ Empresas altamente activas (10+):</b><br>
            <span style='font-size:1.5em; font-weight:700; color:#28a745;'>{empresas_10_mas:,}</span> 
            <span style='font-size:0.85em;'>({pct_10_mas:.1f}%)</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================

# ============================================================================
# INDICADORES DE IMPACTO (2x2)
# ============================================================================
st.header("💯 Indicadores de Resultado e Impacto")

col1, col2 = st.columns(2)

with col1:
    st.subheader("😊 Satisfacción del Cliente")
    sat_data = df_filtrado['Indicador_satisfacción'].dropna()
    if len(sat_data) > 0:
        prom = sat_data.mean()
        emp = len(sat_data)
        emp_sat = (sat_data >= 75).sum()
        pct_sat = (emp_sat / emp * 100) if emp > 0 else 0
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=prom, domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Promedio", 'font': {'size': 24}},
            delta={'reference': 75, 'suffix': '%'},
            gauge={'axis': {'range': [0,100], 'ticksuffix': '%'}, 'bar': {'color': "#667eea"},
                   'steps': [{'range': [0,50], 'color': "#fee2e2"}, {'range': [50,75], 'color': "#fef3c7"}, {'range': [75,100], 'color': "#d1fae5"}],
                   'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 75}}))
        fig.update_layout(height=350, margin=dict(t=60,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Poppins"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f'<p style="text-align:center; background:#f9f9f9; padding:10px; border-radius:8px; font-size:0.95em;">📊 <b>{emp} empresas</b> evaluadas | ✅ <b>{pct_sat:.1f}%</b> altamente satisfechas (≥75%)</p>', unsafe_allow_html=True)
    else:
        st.info("No hay datos disponibles")

with col2:
    st.subheader("💰 Impacto en Ventas")
    vent_data = df_filtrado['Indicador_ventas'].dropna()
    if len(vent_data) > 0:
        mej = (vent_data > 0).sum()
        sin_c = (vent_data == 0).sum()
        dis = (vent_data < 0).sum()
        pct_mej = (vent_data[vent_data > 0].mean() * 100) if mej > 0 else 0
        
        # SOLO MOSTRAR MEJORARON Y SIN CAMBIO
        fig = go.Figure(go.Bar(x=['Mejoraron', 'Sin cambio'], y=[mej, sin_c],
                               text=[mej, sin_c], texttemplate='%{text}', textposition='outside',
                               marker=dict(color=['#10b981','#fbbf24']),
                               hovertemplate='%{x}: %{y} empresas<extra></extra>'))
        fig.update_layout(height=350, margin=dict(t=20,b=20,l=20,r=20), plot_bgcolor='rgba(0,0,0,0)',
                         paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Poppins"),
                         yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', title="Empresas"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f'<p style="text-align:center; background:#f9f9f9; padding:10px; border-radius:8px; font-size:0.95em;">📊 <b>{len(vent_data)} empresas</b> medidas | 📈 <b>{mej} mejoraron</b> (promedio +{pct_mej:.1f}%) | ➡️ <b>{sin_c} sin cambio</b></p>', unsafe_allow_html=True)
    else:
        st.info("No hay datos disponibles")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔧 Procesos Tecnológicos")
    proc_data = df_filtrado['Indicador_procesos_tecnologicos'].dropna()
    if len(proc_data) > 0:
        if proc_data.max() <= 1:
            proc_data = proc_data * 100
        prom_proc = proc_data.mean()
        emp_proc = len(proc_data)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=prom_proc, domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Adopción", 'font': {'size': 24}}, number={'suffix': '%'},
            gauge={'axis': {'range': [0,100], 'ticksuffix': '%'}, 'bar': {'color': "#43e97b"},
                   'steps': [{'range': [0,30], 'color': "#fee2e2"}, {'range': [30,60], 'color': "#fef3c7"}, {'range': [60,100], 'color': "#d1fae5"}]}))
        fig.update_layout(height=350, margin=dict(t=60,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Poppins"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f'<p style="text-align:center; background:#f9f9f9; padding:10px; border-radius:8px; font-size:0.95em;">De 100 empresas se evaluaron <b>{emp_proc}</b> - Zasca Tecnología</p>', unsafe_allow_html=True)
    else:
        st.info("No hay datos disponibles")

with col2:
    st.subheader("🌐 Presencia Digital")
    pres_data = df_filtrado['Indicador_presencia_en_linea'].dropna()
    if len(pres_data) > 0:
        if pres_data.max() <= 1:
            pres_data = pres_data * 100
        prom_pres = pres_data.mean()
        emp_pres = len(pres_data)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=prom_pres, domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Nivel", 'font': {'size': 24}}, number={'suffix': '%'},
            gauge={'axis': {'range': [0,100], 'ticksuffix': '%'}, 'bar': {'color': "#4facfe"},
                   'steps': [{'range': [0,30], 'color': "#fee2e2"}, {'range': [30,60], 'color': "#fef3c7"}, {'range': [60,100], 'color': "#d1fae5"}]}))
        fig.update_layout(height=350, margin=dict(t=60,b=20,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Poppins"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f'<p style="text-align:center; background:#f9f9f9; padding:10px; border-radius:8px; font-size:0.95em;">De 635 empresas se evaluaron <b>{emp_pres}</b> - Zasca Tecnología</p>', unsafe_allow_html=True)
    else:
        st.info("No hay datos disponibles")

st.markdown("---")

# ============================================================================
# ANÁLISIS ADICIONAL DE IMPACTO
# ============================================================================
st.header("💡 Análisis Adicional de Impacto")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Evolución por Año (Programas)")
    evol = df_filtrado.groupby('Año_Ejecución').size().reset_index()
    evol.columns = ['Año', 'Intervenciones']
    evol = evol.sort_values('Año')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=evol['Año'], y=evol['Intervenciones'], mode='lines+markers',
                             line=dict(color='#667eea', width=3), marker=dict(size=12, color='#667eea', line=dict(color='white', width=2)),
                             fill='tozeroy', fillcolor='rgba(102,126,234,0.1)',
                             text=evol['Intervenciones'], textposition='top center', texttemplate='%{text:,}',
                             hovertemplate='<b>Año %{x}</b><br>Intervenciones: %{y:,}<extra></extra>'))
    fig.update_layout(height=450, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Poppins"),
                     xaxis=dict(title="Año", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                     yaxis=dict(title="Número de Intervenciones", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                     hovermode='x unified', showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Promedio de Horas por Tema")
    horas_prom = df_filtrado.groupby('Tema')['No_horas_de_consultoría'].mean().sort_values(ascending=True)
    
    fig = go.Figure(go.Bar(y=horas_prom.index, x=horas_prom.values, orientation='h',
                           marker_color='#4facfe', text=horas_prom.values.round(1), texttemplate='%{text}', textposition='outside',
                           hovertemplate='<b>%{y}</b><br>Promedio: %{x:.1f} horas<extra></extra>'))
    fig.update_layout(height=450, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Poppins"),
                     xaxis=dict(title="Promedio de Horas", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                     yaxis=dict(title=""), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("💧 Matriz de Intervenciones: Sector x Género")

matriz_data = df_filtrado[(df_filtrado['Sector'].notna()) & (df_filtrado['Sector'] != 'NAN')].groupby(['Sector', 'Género']).size().unstack(fill_value=0)

fig = go.Figure(data=go.Heatmap(
    z=matriz_data.values, x=matriz_data.columns, y=matriz_data.index, colorscale='Blues',
    text=matriz_data.values, texttemplate='%{text}', textfont={"size": 12},
    hovertemplate='<b>Sector:</b> %{y}<br><b>Género:</b> %{x}<br><b>Intervenciones:</b> %{z}<extra></extra>',
    colorbar=dict(title="Intervenciones")))

fig.update_layout(height=600, xaxis_title="Género", yaxis_title="Sector",
                 font=dict(family="Poppins", size=12), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================================
# ANÁLISIS DE TALLERES
# ============================================================================
if df_talleres is not None:
    st.header("🎓 Análisis de Talleres")
    
    # Calcular métricas principales
    total_horas_talleres = df_talleres['Horas'].sum()
    total_participantes_talleres = df_talleres['Participantes'].sum()
    total_talleres_realizados = len(df_talleres)
    promedio_participantes_taller = df_talleres['Participantes'].mean()
    
    # MÉTRICAS PRINCIPALES
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="metric-card metric-empresas"><div class="metric-label">Total Talleres</div><div class="metric-value">{total_talleres_realizados}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card metric-horas"><div class="metric-label">Horas de Formación</div><div class="metric-value">{total_horas_talleres}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card metric-municipio"><div class="metric-label">Total Participantes</div><div class="metric-value">{total_participantes_talleres:,}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card metric-unique"><div class="metric-label">Promedio por Taller</div><div class="metric-value">{promedio_participantes_taller:.0f}</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # GRÁFICAS
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Participantes por Tema")
        
        # Agrupar por tema
        participantes_tema = df_talleres.groupby('Tema')['Participantes'].sum().sort_values(ascending=False)
        
        fig = go.Figure(data=[
            go.Bar(
                x=participantes_tema.values,
                y=participantes_tema.index,
                orientation='h',
                marker=dict(
                    color=participantes_tema.values,
                    colorscale='Teal',
                    showscale=False
                ),
                text=participantes_tema.values,
                texttemplate='%{text:,}',
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Participantes: %{x:,}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Poppins"),
            xaxis=dict(title="Número de Participantes", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(title=""),
            margin=dict(t=20,b=20,l=20,r=80)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📅 Evolución Mensual de Participantes")
        
        # Procesar fechas para análisis mensual - Método simplificado
        df_talleres_temp = df_talleres.copy()
        
        # Intentar convertir fechas de manera automática
        df_talleres_temp['Fecha_dt'] = pd.to_datetime(df_talleres_temp['Fecha '], errors='coerce')
        
        # Crear mes-año para agrupar
        df_talleres_temp['Mes_Año'] = df_talleres_temp['Fecha_dt'].dt.strftime('%Y-%m')
        
        # Filtrar solo registros con fecha válida
        df_talleres_validos = df_talleres_temp[df_talleres_temp['Fecha_dt'].notna()].copy()
        
        if len(df_talleres_validos) > 0:
            participantes_mes = df_talleres_validos.groupby('Mes_Año')['Participantes'].sum().sort_index()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=participantes_mes.index,
                y=participantes_mes.values,
                mode='lines+markers',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10, color='#667eea', line=dict(color='white', width=2)),
                fill='tozeroy',
                fillcolor='rgba(102,126,234,0.2)',
                text=participantes_mes.values,
                textposition='top center',
                texttemplate='%{text}',
                hovertemplate='<b>%{x}</b><br>Participantes: %{y:,}<extra></extra>'
            ))
            
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Poppins"),
                xaxis=dict(title="Mes", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                yaxis=dict(title="Participantes", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                hovermode='x unified',
                showlegend=False,
                margin=dict(t=20,b=20,l=20,r=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay fechas válidas para mostrar la evolución mensual")
    
    # Información adicional
    taller_max = df_talleres.loc[df_talleres['Participantes'].idxmax()]
    fecha_taller = taller_max['Fecha '] if isinstance(taller_max['Fecha '], str) else str(taller_max['Fecha '])
    st.markdown(f"""
    <div style='background:#f0f9ff; padding:15px; border-radius:10px; border-left:5px solid #4facfe; margin-top:20px;'>
        <p style='margin:0; font-size:0.95em;'>
            🏆 <b>Taller más concurrido:</b> {taller_max['Tema']} con <b>{taller_max['Participantes']} participantes</b> 
            ({fecha_taller})
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# DATOS DETALLADOS
# ============================================================================
st.header("📋 Datos Detallados")

with st.expander("👁️ Ver datos filtrados", expanded=False):
    st.markdown(f"**Total de registros:** {len(df_filtrado):,}")
    
    tab1, tab2 = st.tabs(["📊 Datos de Intervenciones", "🏢 Intervenciones por Empresa"])
    
    with tab1:
        columnas_mostrar = ['Programa', 'Cohorte', 'Municipio', 'Sector', 'Género', 'Tema', 
                           'No_horas_de_consultoría', 'Año_Ejecución', 'Indicador_satisfacción']
        
        df_mostrar = df_filtrado[columnas_mostrar].copy()
        df_mostrar = df_mostrar.rename(columns={
            'No_horas_de_consultoría': 'Horas',
            'Año_Ejecución': 'Año',
            'Indicador_satisfacción': 'Satisfacción (%)'
        })
        
        st.dataframe(df_mostrar, use_container_width=True, height=400)
        
        # Descargar como Excel
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Datos')
        excel_data = output.getvalue()
        
        st.download_button(
            label="⬇️ Descargar datos filtrados (Excel)",
            data=excel_data,
            file_name='datos_filtrados_transformacion_digital.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
    
    with tab2:
        st.markdown("### Top 50 Empresas con Más Intervenciones")
        
        # Crear dataframe de empresas usando empresa_id (el identificador correcto)
        df_filtrado_temp = df_filtrado.copy()
        
        # Contar intervenciones por empresa_id
        intervenciones_count = df_filtrado_temp.groupby('empresa_id').size().reset_index(name='Intervenciones')
        
        # Obtener información adicional por empresa_id
        empresa_info = df_filtrado_temp.groupby('empresa_id').agg({
            'Nombre_de_la_empresa': 'first',
            'Nombre': 'first',
            'Municipio': 'first',
            'Sector': 'first',
            'Programa': lambda x: ', '.join(x.unique()[:3]),  # Primeros 3 programas
            'No_horas_de_consultoría': 'sum'
        }).reset_index()
        
        # Combinar intervenciones con info
        tabla_empresas = intervenciones_count.merge(empresa_info, on='empresa_id')
        
        # Crear columna de nombre usando Nombre_de_la_empresa, si no existe usar Nombre
        tabla_empresas['Empresa'] = tabla_empresas['Nombre_de_la_empresa'].fillna(tabla_empresas['Nombre'])
        
        # Ordenar por intervenciones y tomar top 50
        tabla_empresas = tabla_empresas.sort_values('Intervenciones', ascending=False).head(50)
        
        # Seleccionar y renombrar columnas para mostrar
        tabla_empresas = tabla_empresas[['Empresa', 'Intervenciones', 'No_horas_de_consultoría', 'Municipio', 'Sector', 'Programa']]
        tabla_empresas = tabla_empresas.rename(columns={
            'No_horas_de_consultoría': 'Total Horas',
            'Programa': 'Programas'
        })
        
        # Resetear índice para numeración desde 1
        tabla_empresas.index = range(1, len(tabla_empresas) + 1)
        
        st.dataframe(tabla_empresas, use_container_width=True, height=400)
        
        # Botón de descarga para tabla de empresas en Excel
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            tabla_empresas.to_excel(writer, sheet_name='Top Empresas')
        excel_empresas = output.getvalue()
        
        st.download_button(
            label="⬇️ Descargar Top Empresas (Excel)",
            data=excel_empresas,
            file_name='top_empresas_intervenciones.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 20px; font-family: "Poppins", sans-serif;'>
    <p style='font-size: 1.1em; font-weight: 600;'><b>Dashboard de Transformación Digital</b></p>
    <p style='font-size: 0.95em;'>Cámara de Comercio de Armenia y del Quindío • 2019-2025</p>
    <p style='font-size: 0.8em; margin-top: 10px; color: #999;'>
        Total de registros: <b>{len(df):,}</b> | Empresas únicas: <b>{df['empresa_id'].nunique():,}</b> | Horas totales: <b>{df['No_horas_de_consultoría'].sum():,.0f}</b>
    </p>
</div>
""", unsafe_allow_html=True)
