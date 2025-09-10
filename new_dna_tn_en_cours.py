# new_dna_tn_en_cours.py

import streamlit as st
import pandas as pd
import plotly.express as px
from pyngrok import ngrok, conf

# Set a title for the Streamlit app
st.set_page_config(layout="wide")
st.title("Tunisian Diaspora: A Global View")
st.markdown("Explore the geographic distribution of the Tunisian diaspora over different years.")

# -----------------
# Data Sources
# -----------------
st.header("Data Sources")
st.markdown("The data for the Tunisian diaspora population is compiled from a range of academic and institutional sources. This includes a comprehensive country fiche from the European Training Foundation (ETF), papers on migration dynamics from the Arab Planning Institute and DIAL, and analysis on irregular migration from Perceptions of the EU, providing a multi-faceted view from historical trends to recent data.")

# -----------------
# Consolidated Data (2000, 2009, 2014, 2020, and 2023)
# -----------------
# ISO-Alpha 3 codes are used for mapping countries.
data = {
    'country': [
        'France', 'Italy', 'Germany', 'USA', 'Canada', 'Belgium', 'Switzerland',
        'UK', 'Netherlands', 'Sweden', 'Austria', 'Spain', 'Norway', 'Denmark',
        'Libya', 'Saudi Arabia', 'Algeria', 'UAE', 'Qatar', 'Morocco', 'Oman', 'Syria',
        'Rest of Arab Countries', 'Sub-Saharan Africa',
        'Japan', 'Indonesia', 'China', 'Rest of Asia'
    ],
    'iso_alpha': [
        'FRA', 'ITA', 'DEU', 'USA', 'CAN', 'BEL', 'CHE', 'GBR', 'NLD', 'SWE', 'AUT',
        'ESP', 'NOR', 'DNK', 'LBY', 'SAU', 'DZA', 'ARE', 'QAT', 'MAR', 'OMN', 'SYR',
        'AR', 'AF', 'JPN', 'IDN', 'CHN', 'AS'
    ],
    'diaspora_population_2000': [
        400000, 100000, 60000, 5000, 10000, 20000, 15000, 5000, 3000, 5000, 2000, 1000,
        500, 50000, 15000, 5000, 10000, 10000, 2000, 1000, 1000, 1500, 500, 500, 50,
        100, 100, 100
    ],
    'diaspora_population_2009': [
        577998, 141907, 82635, 13377, 14202, 19441, 12318, 6526, 8222, 7593, 5870,
        2512, 1242, 1191, 83633, 20017, 15898, 12420, 5926, 3035, 2478, 2250, 7296,
        1057, 624, 329, 198, 682
    ],
    'diaspora_population_2014': [
        728094, 197160, 94536, 16654, 27427, 28809, 18847, 10444, 9474, 9231, 3722,
        1803, 1420, 68952, 39238, 17750, 21086, 21420, 5693, 4570, 3413, 3500, 1723,
        1605, 1323, 950, 642, 640
    ],
    'diaspora_population_2020': [
        950000, 250000, 120000, 20000, 30000, 35000, 25000, 15000, 12000, 11000, 4000,
        2000, 1500, 70000, 40000, 20000, 25000, 25000, 6000, 5000, 4000, 4000, 2000,
        2000, 800, 800, 400, 400
    ],
    'diaspora_population_2023': [
        1100000, 280000, 150000, 25000, 35000, 40000, 30000, 18000, 15000, 14000,
        5000, 2500, 2000, 75000, 45000, 22000, 28000, 30000, 7000, 6000, 5000, 5000,
        2500, 2500, 1000, 1000, 500, 500
    ]
}
df = pd.DataFrame(data)

# Reshape data for plotting
df_melted = df.melt(id_vars=['country', 'iso_alpha'],
                    value_vars=[
                        'diaspora_population_2000',
                        'diaspora_population_2009',
                        'diaspora_population_2014',
                        'diaspora_population_2020',
                        'diaspora_population_2023'
                    ],
                    var_name='year',
                    value_name='diaspora_population')

df_melted['year'] = df_melted['year'].str.replace('diaspora_population_', '')

# -----------------
# Dashboard Logic
# -----------------

# Use st.select_slider for the year selection to support 'options'
year_selected = st.select_slider(
    "Select Year",
    options=[2000, 2009, 2014, 2020, 2023],
    value=2023,
    help="Drag the slider to change the year."
)

# Filter the data based on the selected year
filtered_df = df_melted[df_melted['year'] == str(year_selected)]

# Create the choropleth map
fig = px.choropleth(
    filtered_df,
    locations='iso_alpha',
    color='diaspora_population',
    hover_name='country',
    hover_data={'diaspora_population': True, 'iso_alpha': False},
    projection='natural earth',
    title=f"Tunisian Diaspora Population in {year_selected}",
    color_continuous_scale=px.colors.sequential.Plasma,
    labels={'diaspora_population': 'Population'}
)

# Customize the map layout for a better visual experience
fig.update_geos(
    showcoastlines=True,
    coastlinecolor="black",
    showland=True,
    landcolor="lightgray",
    showocean=True,
    oceancolor="lightblue",
    showframe=False
)

fig.update_layout(
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    geo=dict(bgcolor='rgba(0,0,0,0)')
)

# Display the map in the Streamlit app
st.plotly_chart(fig, use_container_width=True)

# -----------------
# Interactive Table
# -----------------

st.subheader("Data Table")
st.dataframe(filtered_df.sort_values(by='diaspora_population', ascending=False).reset_index(drop=True))

# -----------------
# ngrok Tunnel (using session state to run only once)
# -----------------
if "public_url" not in st.session_state:
    try:
        # Get the ngrok token from secrets.toml
        ngrok_token = st.secrets["NGROK_TOKEN"]

        # Set the auth token using the configuration object
        conf.get_default().auth_token = ngrok_token

        # Kill any ngrok tunnels already running
        ngrok.kill()
        
        # Start a streamlit tunnel on port 8501
        public_url = ngrok.connect(addr="8501")
        
        # Store the URL in session state so it is not created again
        st.session_state.public_url = public_url

    except Exception as e:
        st.error(f"An error occurred while connecting to ngrok. Please check your token and internet connection.")
        st.error(f"Full error details: {e}")

# If a public URL was successfully created, display it
if "public_url" in st.session_state:
    print(f"URL: {st.session_state.public_url}")
