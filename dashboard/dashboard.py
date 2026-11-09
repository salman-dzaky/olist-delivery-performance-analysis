import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Logistics Delay Dashboard 2018", layout="wide")

# Header
st.title("📦 E-Commerce Logistics Delay Analysis (2018)")
st.markdown("Dashboard pemantauan keterlambatan pengiriman pesanan melebihi 3 hari dari estimasi.")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

df_2018 = load_data()

# Sidebar Filter
st.sidebar.header("Filter Data")
selected_states = st.sidebar.multiselect(
    "Pilih Negara Bagian (Customer State):",
    options=df_2018['customer_state'].unique(),
    default=df_2018['customer_state'].unique()
)

filtered_df = df_2018[df_2018['customer_state'].isin(selected_states)]

# Metric Section
total_orders = len(filtered_df)
delayed_orders = filtered_df['is_delayed_3d'].sum()
delay_rate = (delayed_orders / total_orders * 100) if total_orders > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Pesanan Terkirim", f"{total_orders:,}")
col2.metric("Pesanan Terlambat >3 Hari", f"{delayed_orders:,}")
col3.metric("Tingkat Keterlambatan", f"{delay_rate:.2f}%")

st.divider()

# Visualization Section
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Proporsi Keterlambatan Pengiriman")
    fig, ax = plt.subplots(figsize=(5, 5))
    sizes = [total_orders - delayed_orders, delayed_orders]
    labels = ['Tepat Waktu / <3 Hari', 'Terlambat >3 Hari']
    colors = ['#4CAF50', '#FF5722']
    ax.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=90, colors=colors, wedgeprops={'width': 0.4})
    st.pyplot(fig)

with col_right:
    st.subheader("Top Negara Bagian Terlambat")
    state_delay = (
        filtered_df.groupby('customer_state')
        .agg(total=('order_id', 'count'), delayed=('is_delayed_3d', 'sum'))
        .assign(pct=lambda x: (x['delayed'] / x['total']) * 100)
        .sort_values(by='pct', ascending=False)
        .head(10)
        .reset_index()
    )
    
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(data=state_delay, x='pct', y='customer_state', hue='customer_state', palette='Reds_r', legend=False, ax=ax)
    ax.set_xlabel("Persentase Terlambat (%)")
    ax.set_ylabel("State")
    for index, row in state_delay.iterrows():
        ax.text(row['pct'] + 0.2, index, f"{row['pct']:.1f}%", va='center', fontsize=9)
    st.pyplot(fig)