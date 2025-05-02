# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Modelo de Soluciones Climáticas", layout="wide")
# === ESTILOS VISUALES - PRIMERO EL ARTE===
st.markdown("""
<style>
body {
    background-color: #f4f4f4;
}
section.main > div {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
.css-18e3th9 {
    background-color: #ffffff;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# === ENCABEZADO :) ===
st.markdown("""
<style>
.header-container {
    background-color: #F8F9FA;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.header-title {
    font-size: 28px;
    font-weight: bold;
    color: #003366;
}
.subtitle {
    font-size: 16px;
    color: #666666;
}
</style>

<div class="header-container">
    <div class="header-title">📊 Sumideros Naturales de Carbono</div>
    <div class="subtitle">Modelo financiero para análisis de SNC`s</div>
</div>
""", unsafe_allow_html=True)

# --- Inicializar Session State ---
if "soluciones" not in st.session_state:
    st.session_state["soluciones"] = []

st.title("Modelo Interactivo de Soluciones Naturales del Clima")

# ----- CONFIGURACIONES GENERALES -----
st.sidebar.header("Parámetros Generales del Proyecto")

n_anios_default = 30
precio_carbono = st.sidebar.number_input("Precio del carbono (USD/ton CO2)", min_value=0.0, value=15.0, step=1.0)
tasa_descuento = st.sidebar.slider("Tasa de descuento (%)", 1.0, 15.0, 5.0) / 100
# --- Ajustes de Escenarios ---
st.sidebar.header("Ajustes de Escenarios")

multiplicador_area = st.sidebar.slider("Multiplicador de Área (%)", min_value=50, max_value=150, value=100, step=10) / 100
multiplicador_precio_carbono = st.sidebar.slider("Multiplicador de Precio de Carbono (%)", min_value=50, max_value=150, value=100, step=10) / 100
multiplicador_tasa_descuento = st.sidebar.slider("Multiplicador de Tasa de Descuento (%)", min_value=50, max_value=150, value=100, step=10) / 100


# ----- CARGA DE ARCHIVO O ENTRADA MANUAL -----
st.sidebar.header("Carga de Soluciones Climáticas")

opcion_fuente = st.sidebar.radio("¿Cómo deseas ingresar las soluciones?", ["Subir archivo Excel", "Formulario manual"])

if opcion_fuente == "Subir archivo Excel":
    archivo = st.sidebar.file_uploader("Sube un archivo .xlsx con tus soluciones", type=["xlsx"])

    if archivo:
        df_soluciones = pd.read_excel(archivo)
        st.success("Archivo cargado exitosamente.")
    else:
        df_soluciones = pd.DataFrame()
else:
    if "soluciones" not in st.session_state:
        st.session_state.soluciones = []

# --- Definir soluciones predeterminadas ---
soluciones_predeterminadas = {
    "Pastos Marinos": {"captura": 7.5, "costo": 70, "duracion": 30, "capex": 500},
    "Manglares Restaurados": {"captura": 10, "costo": 90, "duracion": 30, "capex": 800},
    "Restauración de Bosque Seco": {"captura": 6, "costo": 55, "duracion": 25, "capex": 400},
    "Restauración de Corales": {"captura": 3, "costo": 100, "duracion": 20, "capex": 1500},
    "Agroforestería con Cacao": {"captura": 5, "costo": 50, "duracion": 20, "capex": 300},
    # 👇 NUEVAS SOLUCIONES
    "Restauración de Bosque de Galería": {"captura": 8, "costo": 65, "duracion": 30, "capex": 600},
    "Restauración de Páramos y Turberas": {"captura": 5, "costo": 70, "duracion": 30, "capex": 750},
    "Restauración de Humedales": {"captura": 9, "costo": 85, "duracion": 25, "capex": 1000},
    "Restauración de Pastos": {"captura": 4, "costo": 45, "duracion": 20, "capex": 350}
}

# --- Formulario para agregar soluciones ---
with st.sidebar.form("form_solucion"):
    tipo_solucion = st.selectbox("Selecciona una solución natural del clima:", list(soluciones_predeterminadas.keys()))

    # Cargar valores por defecto según la solución
    base = soluciones_predeterminadas[tipo_solucion]

    area = st.number_input("Área (ha)", min_value=0.0, value=100.0)
    captura_ha = st.number_input("Captura por ha/año (tCO₂e)", min_value=0.0, value=float(base["captura"]))
    costo_ha = st.number_input("Costo operativo anual (USD/ha)", min_value=0.0, value=float(base["costo"]))
    capex_ha = st.number_input("CAPEX (USD/ha, aplicado solo en año 0)", min_value=0.0, value=float(base["capex"]))
    duracion = st.number_input("Duración del proyecto (años)", min_value=1, max_value=50, value=base["duracion"])
    salvaguarda = st.number_input("Salvaguardas (% descuento al carbono)", min_value=0.0, max_value=100.0, value=0.0, help="Porcentaje de reducción técnica del carbono anual")
    ingreso_encadenado = st.number_input("Ingreso Anual por Encadenamiento Productivo (USD/año)", min_value=0.0, value=0.0, help="Ingreso adicional que no depende del carbono")

    agregar = st.form_submit_button("Agregar solución")

    if agregar:
        st.success("Solución agregada exitosamente")
        st.session_state.soluciones.append({
            "Solución": tipo_solucion,
            "Área (ha)": area,
            "Captura por ha (tCO2e)": captura_ha,
            "Costo anual por ha (USD)": costo_ha,
            "CAPEX por ha (USD)": capex_ha,
            "Duración (años)": duracion, 
            "Salvaguardas (%)": salvaguarda,
            "Ingreso Encadenado (USD/año)": ingreso_encadenado 
        })
df_soluciones = pd.DataFrame(st.session_state.soluciones)

# Mostrar tabla cargada
st.subheader("Soluciones Climáticas Actuales")
if not df_soluciones.empty:
    st.dataframe(df_soluciones)
else:
    st.info("Agrega una solución o carga un archivo para comenzar.")

# ----- CÁLCULOS -----
st.subheader("Resultados del Modelo")

if not df_soluciones.empty:
    
    resultados = []
    flujo_total = np.zeros(n_anios_default)

    for _, sol in df_soluciones.iterrows():
        duracion = int(sol.get("Duración (años)", n_anios_default))
        area_ajustada = sol["Área (ha)"] * multiplicador_area

        # Variables por ha
        captura_bruta = sol["Captura por ha (tCO2e)"] * area_ajustada
        factor_salvaguarda = 1 - (sol.get("Salvaguardas (%)", 0) / 100)
        captura_total_anual = captura_bruta * factor_salvaguarda

        costo_total_anual = sol["Costo anual por ha (USD)"] * area_ajustada
        capex_total = sol["CAPEX por ha (USD)"] * area_ajustada

        # Ingreso y flujo
        ingreso_carbono = captura_total_anual * (precio_carbono * multiplicador_precio_carbono)
        ingreso_encadenado = sol.get("Ingreso Encadenado (USD/año)", 0)
        ingreso_anual_total = ingreso_carbono + ingreso_encadenado
        flujo_anual = ingreso_anual_total - costo_total_anual

        flujo_proyecto = np.zeros(n_anios_default)
        flujo_proyecto[0] = -capex_total  # inversión inicial en año 0
        flujo_proyecto[1:duracion] = flujo_anual

        flujo_total += flujo_proyecto

        tasa_descuento_ajustada = tasa_descuento * multiplicador_tasa_descuento
        vpn = sum([
            flujo_proyecto[i] / ((1 + tasa_descuento_ajustada) ** (i + 1))
            for i in range(n_anios_default)
        ])
        carbono_acumulado = captura_total_anual * duracion

        resultados.append({
        "Solución": sol["Solución"],
        "Área (ha)": area_ajustada,
        "Carbono Total (tCO2e)": carbono_acumulado,
        "Costo Total (USD)": costo_total_anual * duracion,
        "CAPEX Total (USD)": capex_total,
        "Ingreso Total (USD)": ingreso_anual_total * duracion,
        "VPN (USD)": vpn
        })

    flujo_total += flujo_proyecto

    df_resultados = pd.DataFrame(resultados)
    #st.dataframe(df_resultados.style.format("{:,.0f}"))
    columnas_numericas = [
    "Área (ha)", 
    "Carbono Total (tCO2e)", 
    "Costo Total (USD)", 
    "CAPEX Total (USD)",
    "Ingreso Total (USD)", 
    "VPN (USD)"
    ]
   
    import io

    st.dataframe(df_resultados.style.format({col: "{:,.0f}" for col in columnas_numericas}))
    import io

    st.markdown("### Exportar resultados")

    # Convertir DataFrame a Excel (en memoria)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_resultados.to_excel(writer, index=False, sheet_name="Resultados")

    # Rebobinar el buffer antes de pasarlo a descarga
    output.seek(0)

    # Botón de descarga
    st.download_button(
        label="📥 Descargar Excel",
        data=output,
        file_name="resultados_modelo_clima.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
  
    # --- Gráfico de Carbono Capturado por Solución ---
    st.markdown("## Comparativo de Carbono Capturado por Solución")

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8,5))
    ax.bar(df_resultados["Solución"], df_resultados["Carbono Total (tCO2e)"], color="seagreen")
    ax.set_xlabel("Solución Natural del Clima")
    ax.set_ylabel("Carbono Capturado Total (tCO₂e)")
    ax.set_title("Comparativo de Captura de Carbono entre Soluciones")
    plt.xticks(rotation=45, ha="right")
    with st.expander("📊 Comparativo de Carbono Capturado", expanded=True):
        st.pyplot(fig)
    
    st.markdown("---")
    st.markdown("## 📊 Resultados del Modelo Financiero y Climático")

    with st.expander("🧮 Ver tabla detallada de resultados por solución", expanded=True):
        st.dataframe(df_resultados.style.format({col: "{:,.0f}" for col in columnas_numericas}))

    # --- Gráfico de Flujo de Caja Anual Acumulado ---
    st.markdown("## Flujo de Caja Anual Acumulado del Proyecto")
    
    # Crear array de flujo de caja año a año
    años = list(range(1, len(flujo_total) + 1))
    flujo_caja_acumulado = [sum(flujo_total[:i+1]) for i in range(len(flujo_total))]

    fig2, ax2 = plt.subplots(figsize=(8,5))
    ax2.plot(años, flujo_caja_acumulado, marker='o', linestyle='-', color='royalblue')
    ax2.set_xlabel("Año del Proyecto")
    ax2.set_ylabel("Flujo de Caja Acumulado (USD)")
    ax2.set_title("Evolución del Flujo de Caja Acumulado")
    ax2.grid(True)

    st.pyplot(fig2)
    with st.expander("📈 Flujo de Caja Acumulado", expanded=False):
         st.pyplot(fig2)
    
    # --- Espacio ---
    st.markdown("---")
    st.markdown("## 🌿 Comparativo de Carbono Capturado")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.pyplot(fig)  # gráfico de barras de carbono

    # --- Exportación ---
    st.markdown("---")
    st.markdown("## 📥 Exportar Resultados")
    st.download_button(
        label="📥 Descargar Excel",
        data=output,
        file_name="resultados_modelo_SNC.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Carbono Total por Solución")
        fig1, ax1 = plt.subplots()
        ax1.bar(df_resultados["Solución"], df_resultados["Carbono Total (tCO2e)"], color="seagreen")
        st.pyplot(fig1)

    with col2:
        st.markdown("### VPN por Solución")
        fig2, ax2 = plt.subplots()
        ax2.bar(df_resultados["Solución"], df_resultados["VPN (USD)"], color="dodgerblue")
        st.pyplot(fig2)

    # Flujo total
    st.markdown("### Flujo de Caja Consolidado")
    anios = np.arange(1, n_anios_default + 1)
    fig3, ax3 = plt.subplots()
    ax3.plot(anios, flujo_total, marker='o')
    st.pyplot(fig3)

    if st.button("Guardar resultados como CSV"):
        df_resultados.to_csv("resultados_modelo.csv", index=False)
        st.success("Resultados guardados correctamente.")

else:
    st.warning("Por favor agrega una solución o carga un archivo válido.")

# === PIE DE PÁGINA ===
st.markdown("""---""")
st.markdown("""
<div style='text-align: center; color: #888888; font-size: 12px;'>
    <p><strong>Sumideros Naturales de Carbono © 2025 (V3, 04.25)</strong><br>
    Proyecto interno – Uso exclusivo para presentación ejecutiva</p>
</div>
""", unsafe_allow_html=True)

