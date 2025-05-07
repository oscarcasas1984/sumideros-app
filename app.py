# Archivo: app.py corregido y optimizado

import streamlit as st
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import io

# --- CONFIGURAR PÁGINA ---
st.set_page_config(
    page_title="Sumideros Naturales de Carbono",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TÍTULO DE CONTROL ---
st.title("🧪 Laboratorio de Pruebas")

# --- INICIALIZAR VARIABLES ---
resultados = []
df_resultados = pd.DataFrame()
flujo_total = np.zeros(30)

# --- ESTILOS ---
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

# --- ENCABEZADO ---
st.markdown("""
<div style="background-color: #F8F9FA; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
    <div style="font-size: 28px; font-weight: bold; color: #003366;">📊 Sumideros Naturales de Carbono</div>
    <div style="font-size: 16px; color: #666666;">Modelo financiero para análisis de SNC`s</div>
</div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "soluciones" not in st.session_state:
    st.session_state["soluciones"] = []

# --- CONFIGURACIÓN GENERAL ---
st.sidebar.header("Parámetros Generales del Proyecto")
n_anios_default = 30
precio_carbono = st.sidebar.number_input("Precio del carbono (USD/ton CO2)", min_value=0.0, value=15.0, step=1.0)
# NUEVO: crecimiento anual del precio del carbono
crecimiento_precio_carbono = st.sidebar.slider(
    "Crecimiento Anual del Precio del Carbono (%)",
    min_value=0.0,
    max_value=20.0,
    value=0.0,
    step=0.5,
    help="Porcentaje de incremento anual del precio del carbono aplicado cada año"
) / 100
tasa_descuento = st.sidebar.slider("Tasa de descuento (%)", 1.0, 15.0, 5.0) / 100
#Crecimiento Anual del Ingreso por Encademiento Productivo
#st.sidebar.header("Crecimiento anual (sensibilidad)")

crecimiento_ingreso_encadenado = st.sidebar.slider(
    "Crecimiento anual de ingresos por encadenamientos productivos regionales (%)",
    min_value=0,
    max_value=100,
    value=0,
    step=1
) / 100

st.sidebar.header("Ajustes de Escenarios")
multiplicador_area = st.sidebar.slider("Multiplicador de Área (%)", 50, 150, 100, 10) / 100
multiplicador_precio_carbono = st.sidebar.slider("Multiplicador Precio Carbono (%)", 50, 150, 100, 10) / 100
multiplicador_tasa_descuento = st.sidebar.slider("Multiplicador Tasa Descuento (%)", 50, 150, 100, 10) / 100

# --- CARGA O FORMULARIO de SNC del Estudio ---
st.sidebar.header("Modelación de SNCs")
if st.sidebar.button("Resetear Modelo"):
    st.session_state.soluciones = []
    st.rerun()
opcion_fuente = st.sidebar.radio("Ingreso de soluciones", ("Subir archivo Excel", "Modelación Interactiva"))

if opcion_fuente.strip().lower() == "subir archivo excel":
    archivo = st.sidebar.file_uploader("Sube archivo .xlsx", type=["xlsx"])
    df_soluciones = pd.read_excel(archivo) if archivo else pd.DataFrame()

else:
    # Diccionario base de soluciones
    soluciones_predeterminadas = {
        # Restauración (captura constante o especial)
        "Pastos Marinos": {"captura": 7.5, "costo": 70, "duracion": 30, "capex": 500, "tipo_captura": "constante", "tipo_sn": "restauracion"},
        "Manglares": {"captura": 10, "costo": 90, "duracion": 30, "capex": 800, "tipo_captura": "constante", "tipo_sn": "restauracion"},
        "Bosque Seco Tropical": {"captura": 6, "costo": 55, "duracion": 25, "capex": 400, "tipo_captura": "constante", "tipo_sn": "restauracion"},
        "Corales": {"captura": 3, "costo": 100, "duracion": 20, "capex": 1500, "tipo_captura": "constante", "tipo_sn": "restauracion"},
        "Agroforestería con Cacao": {"captura": 5, "costo": 50, "duracion": 20, "capex": 300, "tipo_captura": "constante", "tipo_sn": "restauracion"},
        "Bosque de Galería": {"captura": 8, "costo": 65, "duracion": 30, "capex": 600, "tipo_captura": "constante", "tipo_sn": "restauracion"},
        "Turberas Andinas": {"captura": 5, "costo": 70, "duracion": 30, "capex": 750, "tipo_captura": "constante", "tipo_sn": "restauracion"},

        # Restauración especial
        "Restauración de Pastos Degradados": {
            "tipo_captura": "lineal", "captura_inicial": 2.0, "captura_final": 6.0,
            "costo": 40, "duracion": 30, "capex": 300, "tipo_sn": "restauracion"
        },
        "Reforestación Productiva Zonas ECP": {
            "tipo_captura": "lineal", "captura_inicial": 1.5, "captura_final": 5.5,
            "costo": 60, "duracion": 30, "capex": 350, "tipo_sn": "restauracion"
        },
        "Restauración de Manglares Caribe (Esp.)": {
            "tipo_captura": "sigmoidal", "captura_max": 8.0, "velocidad": 0.3, "punto_medio": 15,
            "costo": 80, "duracion": 30, "capex": 900, "tipo_sn": "restauracion"
        },

        # Degradación Evitada (NUEVOS)
        "Manglar Degradación Evitada": {"captura": 8.0, "costo": 60, "duracion": 30, "capex": 400, "tipo_captura": "constante", "tipo_sn": "degradacion"},
        "Bosque Húmedo Degradación Evitada": {"captura": 7.0, "costo": 50, "duracion": 30, "capex": 350, "tipo_captura": "constante", "tipo_sn": "degradacion"},
        "Páramo Degradación Evitada": {"captura": 5.5, "costo": 55, "duracion": 30, "capex": 370, "tipo_captura": "constante", "tipo_sn": "degradacion"},
        "Humedal Degradación Evitada": {"captura": 6.5, "costo": 60, "duracion": 30, "capex": 390, "tipo_captura": "constante", "tipo_sn": "degradacion"},
        "Pastos Degradación Evitada": {"captura": 4.5, "costo": 40, "duracion": 30, "capex": 310, "tipo_captura": "constante", "tipo_sn": "degradacion"}
    }

    # Selector dinámico
    tipo_sol = st.sidebar.selectbox("Tipo de solución", list(soluciones_predeterminadas))
    base = soluciones_predeterminadas[tipo_sol]

    # Iniciar formulario
    with st.sidebar.form("form_solucion"):
        area = st.number_input("Área (ha)", 0.0, value=100.0)
        costo = st.number_input("Costo anual USD/ha", 0.0, value=float(base["costo"]))
        capex = st.number_input("CAPEX Total (USD)", 0.0, value=float(base["capex"]))
        duracion = st.number_input("Duración (años)", 1, 50, int(base["duracion"]))
        salvaguarda = st.number_input("Salvaguardas %", 0.0, 100.0, 0.0)
        ingreso_extra = st.number_input("Ingreso Encadenamiento Productivo USD/año", 0.0, value=0.0)

        # Asignar tipo de captura y tipo de solución dentro del formulario
        tipo_captura = base.get("tipo_captura", "constante")
        tipo_sn = base.get("tipo_sn", "restauracion")  # <-- AHORA SÍ SE ACTUALIZA CORRECTAMENTE

        # Campos personalizados para tipo de captura
        if tipo_captura == "constante":
            captura = st.number_input("Captura ó Emisión Evitada CO2eq. ha/año", 0.0, value=float(base["captura"]))
        elif tipo_captura == "lineal":
            captura_inicial = st.number_input("Captura Inicial CO2eq. ha/año", 0.0, value=float(base["captura_inicial"]))
            captura_final = st.number_input("Captura Final CO2eq. ha/año", 0.0, value=float(base["captura_final"]))
        elif tipo_captura == "sigmoidal":
            captura_max = st.number_input("Captura Máxima ha/año", 0.0, value=float(base["captura_max"]))
            velocidad = st.number_input("Velocidad de Captura", 0.01, 5.0, value=float(base["velocidad"]))
            punto_medio = st.number_input("Año Punto Medio", 1, 50, int(base["punto_medio"]))

        # Solo si es degradación
        if tipo_sn == "degradacion":
            perdida_evitada = st.number_input("% Pérdida Evitada", 0.0, 100.0, 3.5, help="Porcentaje anual de pérdida que se evita con el proyecto")
        else:
            perdida_evitada = 0.0

        # Botón para guardar solución
        submit = st.form_submit_button("Agregar Solución")

        if submit:
            nueva = {
                "Solución": tipo_sol,
                "Área (ha)": area,
                "Costo anual por ha (USD)": costo,
                "CAPEX Total (USD)": capex,
                "Duración (años)": duracion,
                "Salvaguardas (%)": salvaguarda,
                "Ingreso Encadenado (USD/año)": ingreso_extra,
                "Tipo Captura": tipo_captura,
                "Tipo SNC": tipo_sn,
                "% Pérdida Evitada": perdida_evitada
            }

            if tipo_captura == "constante":
                nueva["Captura por ha (tCO2e)"] = captura
            elif tipo_captura == "lineal":
                nueva["Captura Inicial"] = captura_inicial
                nueva["Captura Final"] = captura_final
            elif tipo_captura == "sigmoidal":
                nueva["Captura Máxima"] = captura_max
                nueva["Velocidad"] = velocidad
                nueva["Punto Medio"] = punto_medio

            st.session_state.soluciones.append(nueva)

    # Crear DataFrame desde session_state
    df_soluciones = pd.DataFrame(st.session_state.soluciones)

# --- MOSTRAR TABLA DE ENTRADA ---
st.subheader("Soluciones Climáticas Actuales")
if not df_soluciones.empty:
    st.dataframe(df_soluciones)
else:
    st.info("Agrega soluciones para comenzar.")

# --- CÁLCULO DE RESULTADOS ---
st.subheader("Resultados de Modelación")

if not df_soluciones.empty:
    resultados = []
    flujo_total = np.zeros(n_anios_default)

    for _, sol in df_soluciones.iterrows():
        dur = int(sol["Duración (años)"])
        area_ajustada = sol["Área (ha)"] * multiplicador_area
        tipo_captura = sol.get("Tipo Captura", "constante")
        tipo_sn = sol.get("Tipo SNC", "restauracion")  # <- CORRECTO para identificar degradación

        # Verificación temporal
        st.write(f"🔍 Verificación: {sol['Solución']} | Tipo SNC: {tipo_sn} | Captura: {tipo_captura} | % Pérdida Evitada: {sol.get('% Pérdida Evitada', 'NA')}")

        # === Cálculo de captura ===
        if tipo_captura == "lineal":
            cap_ini = soluciones_predeterminadas[sol["Solución"]]["captura_inicial"]
            cap_fin = soluciones_predeterminadas[sol["Solución"]]["captura_final"]
            captura_anual = np.linspace(cap_ini, cap_fin, dur)

        elif tipo_captura == "sigmoidal":
            cap_max = soluciones_predeterminadas[sol["Solución"]]["captura_max"]
            k = soluciones_predeterminadas[sol["Solución"]]["velocidad"]
            x0 = soluciones_predeterminadas[sol["Solución"]]["punto_medio"]
            x_vals = np.arange(dur)
            captura_anual = cap_max / (1 + np.exp(-k * (x_vals - x0)))

        elif tipo_sn == "degradacion":
            # Solo para degradación evitada
            porcentaje_perdida = sol.get("% Pérdida Evitada", 0.0) / 100
            base_captura = sol.get("Captura por ha (tCO2e)", 0.0)
            captura_base = base_captura * porcentaje_perdida
            captura_anual = np.full(dur, captura_base)

        else:
            # Constante estándar
            captura_anual = np.full(dur, sol.get("Captura por ha (tCO2e)", 0.0))

        # Ajustar por área y salvaguardas
        factor_salvaguarda = 1 - sol.get("Salvaguardas (%)", 0) / 100
        captura_anual *= area_ajustada * factor_salvaguarda
        captura_total = sum(captura_anual)

        # === Cálculo financiero ===
        costo = sol["Costo anual por ha (USD)"] * area_ajustada
        capex = sol["CAPEX Total (USD)"]
        ingreso_base = sol["Ingreso Encadenado (USD/año)"]

        precio_base = precio_carbono * multiplicador_precio_carbono
        ingreso_carbono = sum([
            captura_anual[anio] * (precio_base * ((1 + crecimiento_precio_carbono) ** anio))
            for anio in range(dur)
        ])
        ingreso_encadenado = sum([
            ingreso_base * ((1 + crecimiento_ingreso_encadenado) ** anio)
            for anio in range(dur)
        ])
        ingreso_total = ingreso_carbono + ingreso_encadenado

        flujo_anual = ingreso_total - (costo * dur)
        flujo_proyecto = np.zeros(n_anios_default)
        flujo_proyecto[0] = -capex
        flujo_proyecto[1:dur] = flujo_anual / dur

        flujo_total += flujo_proyecto
        tasa_desc = tasa_descuento * multiplicador_tasa_descuento
        vpn = sum([
            flujo_proyecto[i] / ((1 + tasa_desc) ** (i + 1))
            for i in range(n_anios_default)
        ])

        resultados.append({
            "Solución": sol["Solución"],
            "Área (ha)": area_ajustada,
            "Carbono Total (tCO2e)": captura_total,
            "Costo Total (USD)": costo * dur,
            "CAPEX Total (USD)": capex,
            "Ingreso Total (USD)": ingreso_total,
            "VPN (USD)": vpn
        })

    df_resultados = pd.DataFrame(resultados)

    # CÁLCULOS DE ESCENARIOS CON VARIACIÓN DEL PRECIO DEL CARBONO
    precios_escenarios = [precio_carbono * 0.8, precio_carbono, precio_carbono * 1.2]
    nombres_escenarios = ["Precio -20%", "Precio base", "Precio +20%"]
    df_escenarios_plot = []

    for nombre_escenario, precio_s in zip(nombres_escenarios, precios_escenarios):
        for _, sol in df_soluciones.iterrows():
            duracion = int(sol["Duración (años)"])
            area_ajustada = sol["Área (ha)"] * multiplicador_area
            captura_bruta = sol["Captura por ha (tCO2e)"] * area_ajustada
            factor_salvaguarda = 1 - (sol["Salvaguardas (%)"] / 100)
            captura_total_anual = captura_bruta * factor_salvaguarda
            costo_total_anual = sol["Costo anual por ha (USD)"] * area_ajustada
            capex_total = sol["CAPEX Total (USD)"]
            ingreso_carbono = captura_total_anual * precio_s * multiplicador_precio_carbono
            ingreso_encadenado = sol["Ingreso Encadenado (USD/año)"]
            ingreso_total = ingreso_carbono + ingreso_encadenado
            flujo_anual = ingreso_total - costo_total_anual

            flujo_proyecto = np.zeros(n_anios_default)
            flujo_proyecto[0] = -capex_total
            flujo_proyecto[1:duracion] = flujo_anual
            tasa_ajustada = tasa_descuento * multiplicador_tasa_descuento
            vpn = sum([
                flujo_proyecto[i] / ((1 + tasa_ajustada) ** (i + 1))
                for i in range(n_anios_default)
            ])
            df_escenarios_plot.append({
                "Escenario": nombre_escenario,
                "Solución": sol["Solución"],
                "VPN": vpn
            })

    df_escenarios_plot = pd.DataFrame(df_escenarios_plot)
    
    # DESPLIEGUE DEL MODELO INTERACTIVO - GRÁFICAS Y SENSIBILIDADES
    # --- Gráfico: Impacto del Precio del Carbono sobre el VPN ---
    st.markdown("### Potencial de Carbono por SNC")
    fig = px.bar(df_resultados, x="Solución", y="Carbono Total (tCO2e)", text="Carbono Total (tCO2e)", color="Solución")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Valor Presente Neto (VPN) por Solución Natural del Clima")

    fig_precio = px.bar(
        df_resultados,
        x="Solución",
        y="VPN (USD)",
        color="Solución",
        text="VPN (USD)",
        title=f"VPN según Precio del Carbono: {precio_carbono} USD/ton",
        labels={"VPN (USD)": "Valor Presente Neto (USD)"}
    )

    fig_precio.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig_precio.update_layout(
        xaxis_title=None,
        yaxis_title="Valor Presente Neto (USD)",
        showlegend=False,
        plot_bgcolor='white',
        margin=dict(t=50, b=50)
    )

    st.plotly_chart(fig_precio, use_container_width=True)
    
    # === Gráfico: Captura acumulada de carbono por solución + total ===
    #st.markdown("## 🌿 Captura Acumulada de Carbono por Solución y Total")

    data_acumulada = []

    for sol in st.session_state.soluciones:
        nombre = sol["Solución"]
        area = sol["Área (ha)"] * multiplicador_area
        dur = int(sol["Duración (años)"])
        tipo = soluciones_predeterminadas[nombre]["tipo_captura"]
        salvaguarda = 1 - sol.get("Salvaguardas (%)", 0) / 100

        acumulado = 0
        for anio in range(n_anios_default):
            if anio >= dur:
                captura_anual = 0
            elif tipo == "constante":
                captura_ha = sol["Captura por ha (tCO2e)"]
            elif tipo == "lineal":
                cap_ini = soluciones_predeterminadas[nombre]["captura_inicial"]
                cap_fin = soluciones_predeterminadas[nombre]["captura_final"]
                captura_ha = cap_ini + (cap_fin - cap_ini) * (anio / dur)
            elif tipo == "sigmoidal":
                cap_max = soluciones_predeterminadas[nombre]["captura_max"]
                velocidad = soluciones_predeterminadas[nombre]["velocidad"]
                p_medio = soluciones_predeterminadas[nombre]["punto_medio"]
                captura_ha = cap_max / (1 + np.exp(-velocidad * (anio - p_medio)))
            else:
                captura_ha = 0

            captura_anual = captura_ha * area * salvaguarda
            acumulado += captura_anual

            data_acumulada.append({
                "Año": anio + 1,
                "Solución": nombre,
                "Captura Acumulada": acumulado
            })

    # DataFrame base
    df_acumulada = pd.DataFrame(data_acumulada)

    # Total acumulado
    df_total_acum = df_acumulada.groupby("Año")["Captura Acumulada"].sum().reset_index()
    df_total_acum["Solución"] = "Total Portafolio"

    # Combinar
    df_graf = pd.concat([df_acumulada, df_total_acum])

    # Plot
    fig_acum = px.line(
        df_graf,
        x="Año",
        y="Captura Acumulada",
        color="Solución",
        title="📈 Captura de Carbono Acumulada por Solución y Total (SNCs Aditivas)",
        labels={"Captura Acumulada": "Toneladas CO₂e"}
    )

    fig_acum.update_layout(
        xaxis_title="Año del Proyecto",
        yaxis_title="Carbono Acumulado (tCO₂e)",
        plot_bgcolor="white",
        margin=dict(t=50, b=40),
        legend_title="Solución"
    )

    st.plotly_chart(fig_acum, use_container_width=True)

    # grafica 3d
    with st.expander("Visualización 3D: Área vs Carbono vs VPN", expanded=True):
        import plotly.express as px

        if not df_resultados.empty:
            fig_3d = px.scatter_3d(
                df_resultados,
                x="Área (ha)",
                y="Carbono Total (tCO2e)",
                z="VPN (USD)",
                color="Solución",
                size="Área (ha)",
                hover_name="Solución",
                title="Relación 3D entre Área, Carbono y VPN"
            )
            fig_3d.update_layout(margin=dict(l=0, r=0, b=0, t=40))
            st.plotly_chart(fig_3d, use_container_width=True)

    # --- Gráfico Plotly: Flujo de Caja Acumulado ---
    st.markdown("Flujo de Caja Acumulado del Proyecto")
    anios = np.arange(1, n_anios_default + 1)
    flujo_caja_acumulado = np.cumsum(flujo_total)

    fig_flujo = px.line(
        x=anios,
        y=flujo_caja_acumulado,
        markers=True,
        title=" Evolución del Flujo de Caja Acumulado",
        labels={"x": "Año", "y": "Flujo de Caja (USD)"}
    )
    fig_flujo.update_layout(
        xaxis_title="Año del Proyecto",
        yaxis_title="USD Acumulado",
        plot_bgcolor='white',
        margin=dict(t=50, b=50)
    )
    st.plotly_chart(fig_flujo, use_container_width=True)

    # --- Matriz Comparativa ---
    st.markdown("## Matriz Comparativa de Eficiencia por Solución")

    if not df_resultados.empty:
        df_comparativa = df_resultados.copy()
        df_comparativa["Eficiencia CO₂e/ha"] = df_comparativa["Carbono Total (tCO2e)"] / df_comparativa["Área (ha)"]
        df_comparativa["Eficiencia VPN/ha"] = df_comparativa["VPN (USD)"] / df_comparativa["Área (ha)"]

        # Redondear y ordenar columnas
        columnas_orden = [
            "Solución", "Área (ha)", "Carbono Total (tCO2e)", "VPN (USD)", "Costo Total (USD)",
            "Eficiencia CO₂e/ha", "Eficiencia VPN/ha"
        ]
        df_comparativa = df_comparativa[columnas_orden].copy()
        df_comparativa.iloc[:, 1:] = df_comparativa.iloc[:, 1:].round(2)

        # Aplicar formato estilo semáforo
        st.dataframe(
            df_comparativa.style.background_gradient(cmap="YlGnBu", subset=["Eficiencia CO₂e/ha", "Eficiencia VPN/ha"])
                        .format({col: "{:,.2f}" for col in df_comparativa.columns if col != "Solución"})
        )
    else:
        st.info("No hay resultados para mostrar en la matriz comparativa.")
        
    # === HEATMAP DE SENSIBILIDAD DE VPN ===
    #st.markdown("Análisis de Sensibilidad: Precio del Carbono vs Tasa de Descuento")

    # Rango de análisis
    rango_precio = np.arange(5, 51, 5)  # precios de carbono
    rango_descuento = np.arange(1, 22, 1)  # tasas de descuento en %

    # Crear matriz de sensibilidad
    matriz_vpn = np.zeros((len(rango_descuento), len(rango_precio)))

    for i, td in enumerate(rango_descuento):
        for j, pc in enumerate(rango_precio):
            flujo_total_sens = np.zeros(n_anios_default)
            for _, sol in df_soluciones.iterrows():
                duracion = int(sol.get("Duración (años)", n_anios_default))
                area_ajustada = sol["Área (ha)"] * multiplicador_area
                captura_bruta = sol["Captura por ha (tCO2e)"] * area_ajustada
                factor_salvaguarda = 1 - (sol.get("Salvaguardas (%)", 0) / 100)
                captura_total_anual = captura_bruta * factor_salvaguarda
                ingreso_carbono = captura_total_anual * pc
                ingreso_encadenado = sol.get("Ingreso Encadenado (USD/año)", 0)
                ingreso_anual_total = ingreso_carbono + ingreso_encadenado
                costo_total_anual = sol["Costo anual por ha (USD)"] * area_ajustada
                flujo_anual = ingreso_anual_total - costo_total_anual
                capex_total = sol["CAPEX Total (USD)"] * area_ajustada
                flujo_proyecto = np.zeros(n_anios_default)
                flujo_proyecto[0] = -capex_total
                flujo_proyecto[1:duracion] = flujo_anual
                flujo_total_sens += flujo_proyecto
            tasa = td / 100
            vpn_sens = sum([
                flujo_total_sens[k] / ((1 + tasa) ** (k + 1))
                for k in range(n_anios_default)
            ])
            matriz_vpn[i, j] = vpn_sens

    # Crear heatmap
    import plotly.graph_objects as go
    fig_heat = go.Figure(
        data=go.Heatmap(
            z=matriz_vpn,
            x=rango_precio,
            y=rango_descuento,
            colorscale='Viridis',
            colorbar=dict(title="VPN (USD)", tickformat=".0f")
        )
    )
    fig_heat.update_layout(
        title="Sensibilidad VPN, Portafolio Integrado SNC – Precio Carbono vs Tasa de Descuento",
        xaxis_title="Precio del Carbono (USD/tCO₂e)",
        yaxis_title="Tasa de Descuento (%)",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    
    # --- Animación Temporal del Flujo de Caja por Solución ---
    #st.markdown("###Animación: Flujo de Caja por Solución Año a Año")

    # Crear DataFrame largo para la animación
    data_animada = []

    for sol in st.session_state.soluciones:
        nombre = sol["Solución"]
        area = sol["Área (ha)"] * multiplicador_area
        tipo_captura = soluciones_predeterminadas.get(nombre, {}).get("tipo_captura", "constante")

        if tipo_captura == "constante":
            captura = sol["Captura por ha (tCO2e)"] * area
        elif tipo_captura == "lineal":
            captura_ini = soluciones_predeterminadas[nombre]["captura_inicial"]
            captura_fin = soluciones_predeterminadas[nombre]["captura_final"]
            captura = ((captura_ini + captura_fin) / 2) * area
        elif tipo_captura == "sigmoidal":
            cap_max = soluciones_predeterminadas[nombre]["captura_max"]
            captura = (cap_max / 2) * area  # estimación media
        else:
            captura = 0

        salvaguarda = 1 - sol.get("Salvaguardas (%)", 0) / 100
        carbono_anual = captura * salvaguarda
        ingreso_carbono = carbono_anual * (precio_carbono * multiplicador_precio_carbono)
        ingreso_extra = sol.get("Ingreso Encadenado (USD/año)", 0)
        ingreso_total = ingreso_carbono + ingreso_extra
        costo_anual = sol["Costo anual por ha (USD)"] * area
        flujo = ingreso_total - costo_anual
        capex = sol["CAPEX Total (USD)"] * area
        duracion = int(sol["Duración (años)"])

        for anio in range(n_anios_default):
            if anio == 0:
                valor = -capex
            elif anio < duracion:
                valor = flujo
            else:
                valor = 0
            data_animada.append({
                "Año": anio + 1,
                "Solución": nombre,
                "Flujo": valor
            })

    df_animada = pd.DataFrame(data_animada)

    # --- Gráfico animado, Se suspende temporalmente. Bloque full comentado ---
    #fig_anim = px.bar(
    #    df_animada,
    #    x="Solución",
    #    y="Flujo",
    #    animation_frame="Año",
    #    color="Solución",
    #    title="Evolución del Flujo de Caja por SNC",
    #    labels={"Flujo": "USD en el año"}
    #)
    #fig_anim.update_layout(yaxis_title="Flujo de Caja (USD)", xaxis_title=None)
    #st.plotly_chart(fig_anim, use_container_width=True, key="grafico_animado")

else:
    st.warning("No se han generado resultados.")

if not df_soluciones.empty:
    # --- COMPARACIÓN DE ESCENARIOS (VPN por Solución con diferentes precios de carbono) ---

    # Crear tres escenarios: bajo, medio, alto
    precios = [precio_carbono * 0.8, precio_carbono, precio_carbono * 1.2]
    etiquetas = ["Bajo", "Medio", "Alto"]

    df_escenarios_plot = []

    for i, p in enumerate(precios):
        resultados_tmp = []
        for _, sol in df_soluciones.iterrows():
            duracion = int(sol["Duración (años)"])
            area_ajustada = sol["Área (ha)"] * multiplicador_area
            captura_bruta = sol["Captura por ha (tCO2e)"] * area_ajustada
            factor_salvaguarda = 1 - (sol.get("Salvaguardas (%)", 0) / 100)
            captura_total_anual = captura_bruta * factor_salvaguarda

            costo_total_anual = sol["Costo anual por ha (USD)"] * area_ajustada
            capex_total = sol["CAPEX Total (USD)"]
            ingreso_carbono = captura_total_anual * (p * multiplicador_precio_carbono)
            ingreso_encadenado = sol.get("Ingreso Encadenado (USD/año)", 0)
            ingreso_anual_total = ingreso_carbono + ingreso_encadenado
            flujo_anual = ingreso_anual_total - costo_total_anual

            flujo_tmp = np.zeros(n_anios_default)
            flujo_tmp[0] = -capex_total
            flujo_tmp[1:duracion] = flujo_anual

            tasa_descuento_ajustada = tasa_descuento * multiplicador_tasa_descuento
            vpn = sum([
                flujo_tmp[i] / ((1 + tasa_descuento_ajustada) ** (i + 1))
                for i in range(n_anios_default)
            ])
            
            resultados_tmp.append({
                "Solución": sol["Solución"],
                "VPN": vpn,
                "Escenario": etiquetas[i]
            })
        
        df_escenarios_plot.extend(resultados_tmp)

    # Convertir a DataFrame para graficar
    df_escenarios_plot = pd.DataFrame(df_escenarios_plot)

    # Gráfico comparativo de VPN por escenario
    fig_escenarios = px.bar(
        df_escenarios_plot,
        x="Solución",
        y="VPN",
        color="Escenario",
        barmode="group",
        text="VPN",
        title="📊 VPN por Solución en Tres Escenarios de Precio del Carbono (+-20%)",
        labels={"VPN": "Valor Presente Neto (USD)"}
    )

    fig_escenarios.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig_escenarios.update_layout(
        xaxis_title=None,
        yaxis_title="VPN (USD)",
        plot_bgcolor='white',
        margin=dict(t=50, b=50)
    )

    st.plotly_chart(fig_escenarios, use_container_width=True)

# --- Gráfico 3D Interactivo de Soluciones ---

if not df_resultados.empty:
    fig3d = px.scatter_3d(
        df_resultados,
        x="Carbono Total (tCO2e)",
        y="VPN (USD)",
        z="Área (ha)",
        color="Solución",
        hover_name="Solución",
        size="Área (ha)",
        title="Análisis 3D: Carbono, Rentabilidad y Escala",
        labels={
            "Carbono Total (tCO2e)": "Carbono (tCO2e)",
            "VPN (USD)": "Valor Presente Neto (USD)",
            "Área (ha)": "Área (ha)"
        }
    )
    fig3d.update_layout(margin=dict(l=0, r=0, b=0, t=40))
    st.plotly_chart(fig3d, use_container_width=True)

#Exportación de Resultados a PDF
import streamlit.components.v1 as components

#st.markdown("Descargar la modelación como PDF")

components.html("""
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    </head>
    <body>
        <button onclick="exportarTodo()" style="padding:12px 24px; font-size:14px; background:#f8f9fa; color:grey; border:none; border-radius:8px;">
            📥 Descargar Modelación Completa en PDF
        </button>

        <script>
        async function exportarTodo() {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF('p', 'pt', 'a4');
            const body = document.body;

            await html2canvas(body, { scale: 2 }).then(canvas => {
                const imgData = canvas.toDataURL("image/png");
                const imgProps = doc.getImageProperties(imgData);
                const pdfWidth = doc.internal.pageSize.getWidth();
                const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

                doc.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
                doc.save("modelo_sumideros_completo.pdf");
            });
        }
        </script>
    </body>
    </html>
""", height=120)


#st.markdown("## 📘 Glosario de Modelo SNC")
with st.expander("📖 Términos clave del modelo", expanded=False):
    st.markdown("""
    **CAPEX**: Inversión de capital inicial en USD por hectárea. Se descuenta al inicio del proyecto.  
    **OPEX**: Costo operativo anual por hectárea (USD/año).  
    **Salvaguardas**: Porcentaje de reducción técnica del carbono proyectado por riesgos o incertidumbre.  
    **Ingreso por Encadenamiento**: Ingreso adicional constante por año (ej. agroindustria, turismo).  
    **Carbono Total**: Captura acumulada en toneladas de CO₂e durante la duración del proyecto.  
    **VPN**: Valor Presente Neto del flujo de caja (USD). Mide rentabilidad descontada al presente.  
    **Flujo de Caja Acumulado**: Evolución de ingresos menos costos netos año a año.
    **Otros Conceptos**: Nuevos Conceptos.            
    """)

# --- Exportar a Excel ---
import io
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_resultados.to_excel(writer, index=False)
output.seek(0)

#st.markdown("##Exportar Resultados del Modelo")
st.download_button(
    label="Descargar Excel",
    data=output,
    file_name="resultados_modelo_SNC.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# === PIE DE PÁGINA ===
st.markdown("""---""")
st.markdown("""
<div style='text-align: center; color: #888888; font-size: 12px;'>
    <p><strong>Sumideros Naturales de Carbono © 2025 (V3, 04.25) - Ger. Energías para la Transición </strong><br>
    Proyecto interno – Uso exclusivo para presentación ejecutiva</p>
</div>
""", unsafe_allow_html=True)

