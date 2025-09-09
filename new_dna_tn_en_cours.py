# This script creates a Streamlit application to visualize the Tunisian diaspora
# on a world map and display it in an interactive table.

# -----------------
# 1. Imports
# -----------------
import pandas as pd
import streamlit as st
import plotly.express as px

# Set the page configuration for the Streamlit app
st.set_page_config(layout="wide")
st.title("Tunisian Diaspora: A Global View")
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
        'Japan', 'China', # Real countries with valid ISO codes
        'Rest of Arab Countries', 'Sub-Saharan Africa', 'Indonesia' # Entries without valid ISO codes
    ],
    'iso_alpha': [
        'FRA', 'ITA', 'DEU', 'USA', 'CAN', 'BEL', 'CHE', 'GBR', 'NLD', 'SWE', 'AUT',
        'ESP', 'NOR', 'DNK', 'LBY', 'SAU', 'DZA', 'ARE', 'QAT', 'MAR', 'OMN', 'SYR',
        'JPN', 'CHN', # Valid ISO codes
        None, None, 'IDN'  # 'IDN' is valid, but we will filter for the map to be safe
    ],
    'diaspora_population_2000': [
        400000, 100000, 60000, 5000, 10000, 20000, 15000, 5000, 3000, 5000, 2000, 1000,
        500, 50000, 15000, 5000, 10000, 10000, 2000, 1000, 1000, 1500,
        50, 100, # Values for real countries
        500, 500, 100 # Values for the problem entries
    ],
    'diaspora_population_2009': [
        577998, 141907, 82635, 13377, 14202, 19441, 12318, 6526, 8222, 7593, 5870,
        2512, 1242, 1191, 83633, 20017, 15898, 12420, 5926, 3035, 2478, 2250,
        624, 198, # Values for real countries
        7296, 1057, 329 # Values for the problem entries
    ],
    'diaspora_population_2014': [
        728094, 197160, 94536, 16654, 27427, 28809, 18847, 10444, 9474, 9231, 3722,
        1803, 1420, 68952, 39238, 17750, 21086, 21420, 5693, 4570, 3413, 3500,
        1323, 642, # Values for real countries
        1723, 1605, 950 # Values for the problem entries
    ],
    'diaspora_population_2020': [
        950000, 250000, 120000, 20000, 30000, 35000, 25000, 15000, 12000, 11000, 4000,
        2000, 1500, 70000, 40000, 20000, 25000, 25000, 6000, 5000, 4000, 4000,
        800, 400, # Values for real countries
        2000, 2000, 800 # Values for the problem entries
    ],
    'diaspora_population_2023': [
        1100000, 280000, 150000, 25000, 35000, 40000, 30000, 18000, 15000, 14000,
        5000, 2500, 2000, 75000, 45000, 22000, 28000, 30000, 7000, 6000, 5000, 5000,
        1000, 500, # Values for real countries
        2500, 2500, 1000 # Values for the problem entries
    ]
}
df = pd.DataFrame(data)

# Create a copy for the choropleth map (only rows with valid ISO codes)
# This filters out 'Rest of Arab Countries', 'Sub-Saharan Africa'
df_for_map = df[df['iso_alpha'].notnull()].copy()

# Reshape the FULL data for the table
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

# Reshape the MAP data (only valid countries)
df_for_map_melted = df_for_map.melt(id_vars=['country', 'iso_alpha'],
                                    value_vars=[
                                        'diaspora_population_2000',
                                        'diaspora_population_2009',
                                        'diaspora_population_2014',
                                        'diaspora_population_2020',
                                        'diaspora_population_2023'
                                    ],
                                    var_name='year',
                                    value_name='diaspora_population')
df_for_map_melted['year'] = df_for_map_melted['year'].str.replace('diaspora_population_', '')

# -----------------
# Dashboard Logic
# -----------------

year_selected = st.select_slider(
    "Select Year",
    options=['2000', '2009', '2014', '2020', '2023'],
    value='2023'
)

# Filter the data based on the selected year
filtered_df = df_melted[df_melted['year'] == year_selected] # For the table
filtered_map_df = df_for_map_melted[df_for_map_melted['year'] == year_selected] # For the map

# Create the choropleth map (ONLY with valid countries)
fig = px.choropleth(
    filtered_map_df,
    locations='iso_alpha',
    color='diaspora_population',
    hover_name='country',
    hover_data={'diaspora_population': True, 'iso_alpha': False},
    projection='natural earth',
    title=f"Tunisian Diaspora Population in {year_selected}",
    color_continuous_scale=px.colors.sequential.Plasma,
    labels={'diaspora_population': 'Population Estimate'}
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

# FIX: Update the layout to make the color bar title explicit
fig.update_layout(
    coloraxis_colorbar=dict(
        title="Number of People", # Clear, simple title for the legend
        title_side="right",
    ),
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    geo=dict(bgcolor='rgba(0,0,0,0)')
)

# Display the map in the Streamlit app
st.plotly_chart(fig, use_container_width=True)

# -----------------
# Interactive Table (Shows ALL data)
# -----------------

st.subheader("Data Table")
st.dataframe(filtered_df[['country', 'diaspora_population']].sort_values(by='diaspora_population', ascending=False).reset_index(drop=True))
