import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# CONFIGURACIÓN GENERAL
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Análisis de Seguros Médicos",
    page_icon="🏥",
    layout="wide",
)

# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df = pd.read_excel("insurance_clean.xlsx")
    orden_segmento = {"Joven": 1, "Adulto": 2, "Senior": 3, "Mayor": 4}
    df["orden_segmento"] = df["segmento_edad"].map(orden_segmento)
    return df

df_original = cargar_datos()

COLORES = {
    "azul":    "#1F77B4",
    "naranja": "#FF7F0E",
    "verde":   "#2CA02C",
    "rojo":    "#D62728",
    "morado":  "#9467BD",
}
PALETA_REGION   = px.colors.qualitative.Set2
PALETA_SEGMENTO = [COLORES["azul"], COLORES["verde"], COLORES["naranja"], COLORES["rojo"]]
PALETA_NIVEL    = [COLORES["verde"], COLORES["naranja"], COLORES["rojo"]]

# ─────────────────────────────────────────────
# NAVEGACIÓN
# ─────────────────────────────────────────────
st.sidebar.title("Navegación")
pagina = st.sidebar.radio(
    "Ir a:",
    ["📊 Resumen del Negocio", "⚠️ Análisis de Riesgo"],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")

# ─────────────────────────────────────────────────────────────
# PÁGINA 1 — RESUMEN DEL NEGOCIO
# ─────────────────────────────────────────────────────────────
if pagina == "📊 Resumen del Negocio":

    st.title("📊 Resumen del Negocio")
    st.markdown("Visión general de la cartera de seguros médicos.")
    st.markdown("---")

    # ── Filtros ──────────────────────────────
    st.sidebar.subheader("Filtros")
    regiones    = sorted(df_original["region"].unique())
    sexos       = sorted(df_original["sex"].unique())
    sel_region  = st.sidebar.multiselect("Región",  regiones, default=regiones)
    sel_sexo    = st.sidebar.multiselect("Sexo",    sexos,    default=sexos)

    df = df_original[
        df_original["region"].isin(sel_region) &
        df_original["sex"].isin(sel_sexo)
    ]

    # ── KPIs ─────────────────────────────────
    total_primas  = df["charges"].sum()
    prima_media   = df["charges"].mean()
    n_clientes    = len(df)

    k1, k2, k3 = st.columns(3)
    k1.metric("💰 Total Primas",   f"${total_primas:,.0f}")
    k2.metric("📈 Prima Media",    f"${prima_media:,.0f}")
    k3.metric("👥 Nº Clientes",    f"{n_clientes:,}")

    st.markdown("---")

    # ── Fila de gráficos principales ─────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Prima Total por Región")
        df_region = (
            df.groupby("region")["charges"]
            .sum()
            .reset_index()
            .sort_values("charges", ascending=True)
        )
        fig_region = px.bar(
            df_region,
            x="charges", y="region",
            orientation="h",
            color="region",
            color_discrete_sequence=PALETA_REGION,
            labels={"charges": "Prima Total ($)", "region": "Región"},
            text=df_region["charges"].apply(lambda x: f"${x:,.0f}"),
        )
        fig_region.update_traces(textposition="outside")
        fig_region.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_region, use_container_width=True)

    with col2:
        st.subheader("Prima Media por Segmento de Edad")
        df_segmento = (
            df.groupby(["segmento_edad", "orden_segmento"])["charges"]
            .mean()
            .reset_index()
            .sort_values("orden_segmento")
        )
        fig_segmento = px.bar(
            df_segmento,
            x="segmento_edad", y="charges",
            color="segmento_edad",
            color_discrete_sequence=PALETA_SEGMENTO,
            labels={"charges": "Prima Media ($)", "segmento_edad": "Segmento"},
            text=df_segmento["charges"].apply(lambda x: f"${x:,.0f}"),
        )
        fig_segmento.update_traces(textposition="outside")
        fig_segmento.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_segmento, use_container_width=True)

    # ── Dona ─────────────────────────────────
    col3, col4 = st.columns([1, 2])

    with col3:
        st.subheader("Distribución por Nivel de Prima")
        df_nivel = (
            df.groupby("nivel_prima")
            .size()
            .reset_index(name="clientes")
        )
        orden_nivel = {"Baja": 0, "Media": 1, "Alta": 2}
        df_nivel["orden"] = df_nivel["nivel_prima"].map(orden_nivel)
        df_nivel = df_nivel.sort_values("orden")

        fig_dona = px.pie(
            df_nivel,
            names="nivel_prima", values="clientes",
            hole=0.45,
            color="nivel_prima",
            color_discrete_map={"Baja": COLORES["verde"], "Media": COLORES["naranja"], "Alta": COLORES["rojo"]},
        )
        fig_dona.update_traces(textposition="inside", textinfo="percent+label")
        fig_dona.update_layout(showlegend=True, height=350)
        st.plotly_chart(fig_dona, use_container_width=True)

    with col4:
        st.subheader("Detalle por Región y Nivel de Prima")
        df_detalle = (
            df.groupby(["region", "nivel_prima"])
            .agg(clientes=("charges", "count"), prima_media=("charges", "mean"))
            .reset_index()
        )
        df_detalle["prima_media"] = df_detalle["prima_media"].map("${:,.0f}".format)
        st.dataframe(df_detalle, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────
# PÁGINA 2 — ANÁLISIS DE RIESGO
# ─────────────────────────────────────────────────────────────
else:

    st.title("⚠️ Análisis de Riesgo")
    st.markdown("Impacto del tabaquismo en las primas y perfil de riesgo por región.")
    st.markdown("---")

    df = df_original.copy()

    # ── KPI Fumadores ────────────────────────
    pct_fumadores  = df["fumador_flag"].mean() * 100
    n_fumadores    = df["fumador_flag"].sum()
    prima_fum      = df[df["smoker"] == "yes"]["charges"].mean()
    prima_no_fum   = df[df["smoker"] == "no"]["charges"].mean()
    ratio          = prima_fum / prima_no_fum

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🚬 % Fumadores",         f"{pct_fumadores:.1f}%")
    k2.metric("🚬 Nº Fumadores",        f"{n_fumadores:,}")
    k3.metric("💰 Prima Media Fumador",  f"${prima_fum:,.0f}")
    k4.metric("📊 Ratio vs No Fumador",  f"{ratio:.1f}x")

    st.markdown("---")

    # ── Barras agrupadas ─────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Prima Media: Fumadores vs No Fumadores por Región")
        df_fum_region = (
            df.groupby(["region", "smoker"])["charges"]
            .mean()
            .reset_index()
        )
        df_fum_region["smoker_label"] = df_fum_region["smoker"].map({"yes": "Fumador", "no": "No Fumador"})
        fig_fum = px.bar(
            df_fum_region,
            x="region", y="charges",
            color="smoker_label",
            barmode="group",
            color_discrete_map={"Fumador": COLORES["rojo"], "No Fumador": COLORES["azul"]},
            labels={"charges": "Prima Media ($)", "region": "Región", "smoker_label": ""},
            text=df_fum_region["charges"].apply(lambda x: f"${x:,.0f}"),
        )
        fig_fum.update_traces(textposition="outside", textfont_size=10)
        fig_fum.update_layout(height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_fum, use_container_width=True)

    with col2:
        st.subheader("Edad vs Prima (por perfil fumador)")
        df_scatter = df.copy()
        df_scatter["Perfil"] = df_scatter["smoker"].map({"yes": "Fumador", "no": "No Fumador"})
        fig_scatter = px.scatter(
            df_scatter,
            x="age", y="charges",
            color="Perfil",
            color_discrete_map={"Fumador": COLORES["rojo"], "No Fumador": COLORES["azul"]},
            opacity=0.6,
            labels={"age": "Edad", "charges": "Prima ($)", "Perfil": ""},
            hover_data=["region", "bmi", "segmento_edad"],
        )
        fig_scatter.update_layout(height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ── Tabla resumen por región ──────────────
    st.subheader("Tabla Resumen por Región")
    df_tabla = df.groupby("region").agg(
        n_clientes   =("charges", "count"),
        prima_media  =("charges", "mean"),
        n_fumadores  =("fumador_flag", "sum"),
    ).reset_index()
    df_tabla["pct_fumadores"] = df_tabla["n_fumadores"] / df_tabla["n_clientes"] * 100

    df_tabla_display = df_tabla[["region", "n_clientes", "prima_media", "pct_fumadores"]].copy()
    df_tabla_display.columns = ["Región", "Nº Clientes", "Prima Media ($)", "% Fumadores"]
    df_tabla_display["Prima Media ($)"] = df_tabla_display["Prima Media ($)"].map("${:,.0f}".format)
    df_tabla_display["% Fumadores"]     = df_tabla_display["% Fumadores"].map("{:.1f}%".format)

    st.dataframe(df_tabla_display, use_container_width=True, hide_index=True)

    # ── Boxplot bonus ────────────────────────
    st.subheader("Distribución de Primas por Perfil Fumador y Región")
    df_box = df.copy()
    df_box["Perfil"] = df_box["smoker"].map({"yes": "Fumador", "no": "No Fumador"})
    fig_box = px.box(
        df_box,
        x="region", y="charges",
        color="Perfil",
        color_discrete_map={"Fumador": COLORES["rojo"], "No Fumador": COLORES["azul"]},
        labels={"charges": "Prima ($)", "region": "Región", "Perfil": ""},
        points="outliers",
    )
    fig_box.update_layout(height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_box, use_container_width=True)
