import streamlit as st

st.set_page_config(
    page_title="Soccer Analytics Hub",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Soccer Analytics Hub")
st.sidebar.success("Select a Competition above.")

st.markdown("""
Welcome to the Data Hub
Select a league from the sidebar to view detailed analytics.

**Available Dashboards:**
* **🇪🇸 La Liga:** Full season analysis, decisive goals, and MVP race.
* **🇬🇧 Premier League:** (Coming Soon)
* **🏆 Champions League:** Group stage and knockout tree analysis.
""")

# You can add a cool image or overall stats here later