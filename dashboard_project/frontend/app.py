import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Use IPv4 explicitly to avoid connection issues on localhost
API_URL = "https://ai-powered-interactive-dashboard-ap.vercel.app/"  # Update this to your deployed FastAPI URL if needed

st.set_page_config(page_title="AI Dashboard", layout="wide")
st.title("📊 Real-Time Interactive Analytics Dashboard")

# Sidebar - Add New Metric
st.sidebar.header("➕ Add New Data Metric")
category = st.sidebar.selectbox("Category", ["Sales", "Operations", "User Growth", "Performance"])
name = st.sidebar.text_input("Metric Name")
value = st.sidebar.number_input("Value", min_value=0.0, step=1.0)

if st.sidebar.button("Submit to API"):
    if name:
        payload = {
            "category": category,
            "name": name,
            "value": value,
            "status": "Active"
        }
        try:
            response = requests.post(f"{API_URL}/metrics", json=payload, timeout=5)
            if response.status_code == 201:
                st.sidebar.success(f"Added '{name}' successfully!")
                st.rerun()
            else:
                st.sidebar.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            st.sidebar.error("❌ Connection Refused! Check if FastAPI server is running on http://127.0.0.1:8000")
        except Exception as e:
            st.sidebar.error(f"❌ Unexpected Error: {e}")
    else:
        st.sidebar.warning("Please enter a metric name.")

# Main Dashboard View
st.subheader("Current Data Overview")

try:
    res = requests.get(f"{API_URL}/metrics", timeout=5)
    if res.status_code == 200 and res.json():
        data = res.json()
        df = pd.DataFrame(data)

        # Key Performance Indicators (KPIs)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Metrics Tracked", len(df))
        col2.metric("Total Value Aggregate", f"${df['value'].sum():,.2f}")
        col3.metric("Highest Single Value", f"${df['value'].max():,.2f}")

        st.markdown("---")

        # Layout: Chart + Data Table
        c1, c2 = st.columns([2, 1])

        with c1:
            st.subheader("Category Breakdown")
            fig = px.bar(df, x="name", y="value", color="category", barmode="group")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("Data Records")
            st.dataframe(df[["id", "category", "name", "value"]], hide_index=True)

        st.markdown("---")

        # AI / Analytics Forecast Section
        st.subheader("📈 AI Growth Forecast")
        selected_id = st.selectbox("Select metric to compute 15% growth projection:", df["id"].tolist())
        if st.button("Calculate Forecast"):
            forecast_res = requests.get(f"{API_URL}/analytics/forecast/{selected_id}")
            if forecast_res.status_code == 200:
                result = forecast_res.json()
                st.info(f"**{result['metric_name']}** — Current Value: **${result['current_value']}** → Forecasted Value: **${result['projected_growth_15pct']}**")

    else:
        st.info("No data found in database. Use the sidebar to add some records!")

except requests.exceptions.ConnectionError:
    st.error("⚠️ Cannot reach FastAPI server. Please check your backend terminal.")