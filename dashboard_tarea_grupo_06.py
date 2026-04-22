import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ============================
# CARGA DE DATOS
# ============================
df = pd.read_csv("supermarket_sales.csv")
df["Date"] = pd.to_datetime(df["Date"])
df["Time"] = pd.to_datetime(df["Time"], format="mixed").dt.time
# df["Time"] = pd.to_datetime(df["Time"]).dt.time


# ============================
# CONFIGURACIÓN GENERAL
# ============================
st.set_page_config(page_title="Dashboard Supermarket Sales", layout="wide")
st.title("📊 Dashboard — Supermarket Sales")
st.markdown("Exploración interactiva del Supermarket Sales Dataset (enero–marzo 2019).")


# ============================
# ESTADO INICIAL DE LOS FILTROS
# ============================
if "branches" not in st.session_state:
    st.session_state.branches = list(df["Branch"].unique())

if "products" not in st.session_state:
    st.session_state.products = list(df["Product line"].unique())

if "customer_types" not in st.session_state:
    st.session_state.customer_types = list(df["Customer type"].unique())

if "genders" not in st.session_state:
    st.session_state.genders = list(df["Gender"].unique())

if "payments" not in st.session_state:
    st.session_state.payments = list(df["Payment"].unique())

if "date_range" not in st.session_state:
    st.session_state.date_range = (
        df["Date"].min().date(),
        df["Date"].max().date()
    )

if "metric" not in st.session_state:
    st.session_state.metric = "Total"


# ============================
# SIDEBAR — FILTROS
# ============================
st.sidebar.header("Filtros")

# Botón de reset: vuelve a poner los valores iniciales
if st.sidebar.button("Restablecer filtros"):
    st.session_state.branches = list(df["Branch"].unique())
    st.session_state.products = list(df["Product line"].unique())
    st.session_state.customer_types = list(df["Customer type"].unique())
    st.session_state.genders = list(df["Gender"].unique())
    st.session_state.payments = list(df["Payment"].unique())
    st.session_state.date_range = (df["Date"].min(), df["Date"].max())
    st.session_state.metric = "Total"

branches = st.sidebar.multiselect(
    "Sucursal (Branch):",
    options=df["Branch"].unique(),
    default=st.session_state.branches,
    key="branches"
)

products = st.sidebar.multiselect(
    "Línea de producto:",
    options=df["Product line"].unique(),
    default=st.session_state.products,
    key="products"
)

customer_types = st.sidebar.multiselect(
    "Tipo de cliente:",
    options=df["Customer type"].unique(),
    default=st.session_state.customer_types,
    key="customer_types"
)

genders = st.sidebar.multiselect(
    "Género:",
    options=df["Gender"].unique(),
    default=st.session_state.genders,
    key="genders"
)

payments = st.sidebar.multiselect(
    "Método de pago:",
    options=df["Payment"].unique(),
    default=st.session_state.payments,
    key="payments"
)

date_range = st.sidebar.date_input(
    "Rango de fechas:",
    value=st.session_state.date_range,
    key="date_range"
)

metric = st.sidebar.selectbox(
    "Métrica numérica:",
    ["Total", "Quantity", "Rating", "gross income"],
    index=["Total", "Quantity", "Rating", "gross income"].index(st.session_state.metric),
    key="metric"
)

bins = st.sidebar.slider(
    "Número de bins del histograma",
    min_value=5,
    max_value=40,
    value=15
)

# ============================
# APLICAR FILTROS
# ============================
df_filtered = df[
    (df["Branch"].isin(branches)) &
    (df["Product line"].isin(products)) &
    (df["Customer type"].isin(customer_types)) &
    (df["Gender"].isin(genders)) &
    (df["Payment"].isin(payments)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]


# ============================
# MÉTRICAS GENERALES
# ============================
st.markdown("### 📌 Métricas generales")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Registros",
    f"{len(df_filtered)}",
    help="Cantidad de transacciones que cumplen con los filtros aplicados."
)

col2.metric(
    "Ventas totales",
    f"${df_filtered['Total'].sum():,.0f}",
    help="Suma total de ventas (columna Total) dentro del rango filtrado."
)

col3.metric(
    "Ticket promedio",
    f"${df_filtered['Total'].mean():.2f}",
    help="Promedio del valor Total por transacción."
)

col4.metric(
    "Cantidad promedio",
    f"{df_filtered['Quantity'].mean():.2f}",
    help="Promedio de unidades compradas por transacción."
)

col5.metric(
    "Rating promedio",
    f"{df_filtered['Rating'].mean():.2f}",
    help="Promedio de satisfacción del cliente según el rating entregado."
)

col6.metric(
    "Ingreso bruto",
    f"${df_filtered['gross income'].sum():,.0f}",
    help="Ingreso bruto generado (5% del Total)."
)



# ============================
# SECCIÓN 1 — Evolución temporal
# ============================
st.subheader("📈 1.- Evolución temporal de ventas")

daily_sales = df_filtered.groupby("Date")["Total"].sum().reset_index()

fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(daily_sales["Date"], daily_sales["Total"], marker="o", linewidth=1.5)
ax1.set_title("Ventas diarias (monto total)")
ax1.set_xlabel("Fecha")
ax1.set_ylabel("Ventas (monto total)")
ax1.grid(alpha=0.3)

# 🔥 FORMATO DE FECHA DD-MM-YYYY
import matplotlib.dates as mdates
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))

plt.xticks(rotation=45)

st.pyplot(fig1)


# ============================
# SECCIÓN 2 — Comparación entre líneas de producto
# ============================
st.subheader("🏷️ 2.- Ventas por línea de producto")

# Agrupar por línea de producto usando la métrica Total
product_sales = df_filtered.groupby("Product line")["Total"].sum().sort_values()

# Crear figura para Streamlit
fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.barh(product_sales.index, product_sales.values, color="skyblue")
ax2.set_title("Monto total de ventas por línea de producto")
ax2.set_xlabel("Total de ventas (monto)")
ax2.set_ylabel("Línea de producto")
ax2.grid(axis="x", alpha=0.3)

st.pyplot(fig2)

# ============================
# SECCIÓN 3 — Distribución por segmento
# ============================
st.subheader("👥 3.- Distribución del monto total por tipo de cliente")

# Crear figura para Streamlit
fig3, ax3 = plt.subplots(figsize=(8, 4))
sns.boxplot(data=df_filtered, x="Customer type", y="Total", palette="pastel", ax=ax3)

ax3.set_title("Distribución del monto total por tipo de cliente")
ax3.set_xlabel("Tipo de cliente")
ax3.set_ylabel("Total de la compra (monto)")
ax3.grid(axis="y", alpha=0.3)

st.pyplot(fig3)


# ============================
# SECCIÓN 4 — Experiencia del cliente
# ============================
st.subheader("⭐ 4.- Distribución de Rating por línea de producto")

# Crear figura para Streamlit
fig4, ax4 = plt.subplots(figsize=(10, 4))
sns.boxplot(data=df_filtered, x="Product line", y="Rating", palette="Blues", ax=ax4)

ax4.set_title("Distribución de Rating por línea de producto")
ax4.set_xlabel("Línea de producto")
ax4.set_ylabel("Rating")
plt.xticks(rotation=45)
ax4.grid(axis="y", alpha=0.3)

st.pyplot(fig4)


# ============================
# SECCIÓN 5 — Radiografía multidimensional de las sucursales
# ============================
st.subheader("🏬 5.- Radiografía multidimensional de las sucursales")

# Métricas a comparar
metrics = ["Total", "Quantity", "Rating", "gross income"]

# Agrupar por sucursal
branch_stats = df_filtered.groupby("Branch")[metrics].mean()

# Normalizar para que todas las métricas estén en la misma escala
branch_norm = (branch_stats - branch_stats.min()) / (branch_stats.max() - branch_stats.min())

# Preparar datos para radar chart
labels = ["Total", "Quantity", "Rating", "Gross Income"]
num_vars = len(labels)

# Crear figura
fig5 = plt.figure(figsize=(8, 6))
ax5 = fig5.add_subplot(111, polar=True)

angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]  # cerrar el gráfico

# Graficar cada sucursal
for branch in branch_norm.index:
    values = branch_norm.loc[branch].tolist()
    values += values[:1]
    ax5.plot(angles, values, linewidth=2.5, label=f"Sucursal {branch}")
    ax5.fill(angles, values, alpha=0.15)

# Configuración estética
ax5.set_xticks(angles[:-1])
ax5.set_xticklabels(labels)
ax5.set_title("Comparación multidimensional de sucursales", fontsize=14)
ax5.grid(alpha=0.3)
ax5.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

st.pyplot(fig5)


# ============================
# SECCIÓN 6 — Medios de pago y segmentación 
# ============================
st.subheader("💳 6.- Preferencias de pago por tipo de cliente")

# Agrupar por Payment y Customer type
payment_segment = df_filtered.groupby(["Customer type", "Payment"]).size().reset_index(name="Count")

# Crear figura para Streamlit
fig6, ax6 = plt.subplots(figsize=(10, 4))
sns.barplot(
    data=payment_segment,
    x="Customer type",
    y="Count",
    hue="Payment",
    palette="Set2",
    ax=ax6
)

ax6.set_title("Preferencias de medios de pago según tipo de cliente")
ax6.set_xlabel("Tipo de cliente")
ax6.set_ylabel("Cantidad de transacciones")
ax6.grid(axis="y", alpha=0.3)

# Mover la leyenda fuera del gráfico
ax6.legend(
    title="Método de pago",
    loc="center left",
    bbox_to_anchor=(1.05, 0.5),
    frameon=False
)

st.pyplot(fig6)


# ============================
# SECCIÓN 7 — Relaciones entre variables numéricas 
# ============================
st.subheader("📊 7.- Matriz de correlación entre variables numéricas")

# Seleccionar variables numéricas relevantes
numeric_cols = ["Unit price", "Quantity", "Tax 5%", "Total", "gross income", "Rating"]

# Calcular matriz de correlación
corr_matrix = df_filtered[numeric_cols].corr()

# Renombrar solo para visualización (no afecta el dataframe)
corr_matrix = corr_matrix.rename(
    index={"gross income": "Gross Income"},
    columns={"gross income": "Gross Income"}
)

# Etiquetas corregidas para mostrar en el heatmap
display_labels = ["Unit price", "Quantity", "Tax 5%", "Total", "Gross Income", "Rating"]

# Crear figura para Streamlit
fig7, ax7 = plt.subplots(figsize=(8, 5))
sns.heatmap(
    corr_matrix,
    annot=True,
    cmap="Blues",
    linewidths=0.5,
    fmt=".2f",
    xticklabels=display_labels,
    yticklabels=display_labels,
    ax=ax7
)

ax7.set_title("Matriz de correlación entre variables numéricas")

st.pyplot(fig7)



# ============================
# SECCIÓN 8 — Visualización de síntesis
# ============================
st.subheader("🌟 8.- Distribución global del Rating (satisfacción del cliente)")

# Crear figura
fig8, ax8 = plt.subplots(figsize=(10, 4))
sns.histplot(
    data=df_filtered,
    x="Rating",
    bins=bins,
    kde=True,
    color="skyblue",
    ax=ax8
)

ax8.set_title("Distribución del Rating en todo el dataset")
ax8.set_xlabel("Rating")
ax8.set_ylabel("Frecuencia")
ax8.grid(axis="y", alpha=0.3)

st.pyplot(fig8)


# ============================
# FOOTER
# ============================
st.markdown("---")
st.markdown("Dashboard desarrollado por el equipo 06 para el trabajo en equipo del Curso Visualización de Información en la Era del Big Data " \
"del Diplomado de Machine Learning & Big Data.")
