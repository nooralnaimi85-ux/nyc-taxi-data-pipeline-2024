"""Interactive dashboard for verified 2024 NYC TLC Yellow Taxi data."""
import duckdb
import streamlit as st
from src.config import DB
st.set_page_config(page_title='NYC Taxi Trip Data Analytics', layout='wide')
st.title('NYC Taxi Trip Data Analytics — 2024')
if not DB.exists():
    st.error('Database not found. Run the pipeline before opening the dashboard.')
    st.stop()
with duckdb.connect(str(DB), read_only=True) as con:
    monthly = con.execute('SELECT * FROM monthly_summary').df()
    hourly = con.execute('SELECT * FROM hourly_summary').df()
    payments = con.execute('SELECT * FROM payment_summary').df()
    locations = con.execute('SELECT * FROM location_summary').df()
if monthly.empty:
    st.warning('No valid records were retained for the selected 2024 months.')
    st.stop()
st.metric('Retained trips', f"{int(monthly['trips'].sum()):,}")
st.caption(f"Loaded {len(monthly)} month(s) of 2024. This is not a full-year analysis unless all 12 months are loaded.")
st.subheader('Monthly trip volume')
st.bar_chart(monthly.set_index('trip_month')['trips'])
a, b = st.columns(2)
with a:
    st.subheader('Trips by pickup hour')
    st.bar_chart(hourly.set_index('pickup_hour')['trips'])
with b:
    st.subheader('Trips by payment type (source codes)')
    st.bar_chart(payments.set_index('payment_type')['trips'])
st.subheader('Top 15 pickup location IDs')
st.bar_chart(locations.set_index('pickup_location_id')['trips'])
st.caption('Source: NYC TLC Yellow Taxi records. Exclusion and deduplication rules are documented in the README.')
