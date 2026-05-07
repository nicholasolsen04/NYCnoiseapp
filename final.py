'''
Name: Nick Olsen
CS230: Section 8
Data: Noise complaints in NYC
URL:
Description:

This program creates a interactive web based python application using NYC noise complaint data.
'''

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# [ST4] Customized page design features
st.set_page_config(page_title="NYC Noise Complaints", layout="wide")

# [PY1] A function with two or more parameters, one default value
def top_counts(data, column, n=10):
    return data[column].value_counts().head(n)

# [PY2] A function that returns more than one value
def summary_stats(data):
    total = len(data)

    if total > 0:
        top_borough = data["Borough"].value_counts().idxmax()
        top_type = data["Problem (formerly Complaint Type)"].value_counts().idxmax()
    else:
        top_borough = "No data"
        top_type = "No data"

    return total, top_borough, top_type

# Function for hour slider
def format_hour(hour):
    if hour == 0:
        return "12 AM"
    elif hour < 12:
        return f"{hour} AM"
    elif hour == 12:
        return "12 PM"
    else:
        return f"{hour - 12} PM"

# [PY3] Error checking with try/except
try:
    df = pd.read_csv("311_Noise_Complaints_20260403.csv")
except FileNotFoundError:
    st.error("No data found. Please try again.")
    st.stop()

# [DA1] Clean or Manipulate data
df = df.dropna(subset=["Borough", "Latitude", "Longitude", "Created Date"])
df["Created Date"] = pd.to_datetime(df["Created Date"], errors="coerce")
df = df.dropna(subset=["Created Date"])

# [DA7] Create new columns
df["Hour"] = df["Created Date"].dt.hour
df["Date"] = df["Created Date"].dt.date


# [PY5] Dictionary were you write code to access its keys, values, or items
borough_names = {
    "BRONX": "Bronx",
    "BROOKLYN": "Brooklyn",
    "MANHATTAN": "Manhattan",
    "QUEENS": "Queens",
    "STATEN ISLAND": "Staten Island"
}

# [PY4] list comprehension
borough_options = ["All"] + [b for b in sorted(df["Borough"].dropna().unique())]

st.title("NYC 311 Noise Complaint Explorer")
st.write("Explore where, when, and what types of noise complaints happen in NYC.")

st.sidebar.header("Filters")

# [ST1] At least three Streamlit different widgets
selected_borough = st.sidebar.selectbox(
    "Choose a borough",
    borough_options,
    format_func=lambda borough: borough_names.get(borough, borough)
)

# [ST2]
complaint_options = sorted(df["Problem (formerly Complaint Type)"].dropna().unique())
selected_types = st.sidebar.multiselect("Choose complaint type(s)", complaint_options)

# [ST3]
hour_range = st.sidebar.slider(
    "Choose hour range:",
    0,
    23,
    (0, 23)
)

st.sidebar.write(
    f"Selected time range: **{format_hour(hour_range[0])} to {format_hour(hour_range[1])}**"
)

st.sidebar.markdown("---")


# [DA4] Filter data by one condition
filtered_df = df.copy()
if selected_borough != "All":
    filtered_df = df[df["Borough"] == selected_borough]

# [DA5] Filter data by two or more conditions with AND or OR
filtered_df = filtered_df[
    (filtered_df["Hour"] >= hour_range[0]) &
    (filtered_df["Hour"] <= hour_range[1])
]

if selected_types:
    filtered_df = filtered_df[
        filtered_df["Problem (formerly Complaint Type)"].isin(selected_types)
    ]

# Summary Statistics
total, top_borough, top_type = summary_stats(filtered_df)

# [PY5] Access dictionary items
top_borough_display = borough_names.get(top_borough, top_borough)
col1, col2, col3 = st.columns(3)
col1.metric("Total Complaints", total)
col2.metric("Top Borough", top_borough)
col3.metric("Most Common Noise Complaint Type", top_type)

st.markdown("---")

if len(filtered_df) == 0:
    st.warning("No data matches the selected filters.")
    st.stop()

# [DA2] Sort data
borough_counts = filtered_df["Borough"].value_counts().sort_values(ascending=False)

# [DA3] Find top largest values of a column
# [PY1] Function call with a default value
top_zip_codes = top_counts(filtered_df, "Incident Zip")

# [PY1] Funciton call without using default value
top_complaint_types = top_counts(filtered_df, "Problem (formerly Complaint Type)", 8)

# Visualizations

st.subheader("Complaints by Borough")

# [VIZ1] Bar chart
fig1, ax1 = plt.subplots()
borough_counts.plot(kind="bar", ax=ax1, color="blue")
ax1.set_title("Noise Complaints by Borough")
ax1.set_xlabel("Borough")
ax1.set_ylabel("Number of Complaints")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
st.pyplot(fig1)

st.markdown("---")


st.subheader("Top Complaint Types")

#[VIZ2] Bar chart
fig2, ax2 = plt.subplots()
top_complaint_types.plot(kind="bar", ax=ax2, color="green")
ax2.set_title("Top Noise Complaint Types")
ax2.set_xlabel("Complaint Type")
ax2.set_ylabel("Number of Complaints")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
st.pyplot(fig2)

st.markdown("---")

st.subheader("Complaints by Hour")
hour_counts = filtered_df["Hour"].value_counts().sort_index()

# [VIZ3] Line chart
fig3, ax3 = plt.subplots()
hour_counts.plot(kind="line", marker="o", ax=ax3, color="red")
ax3.set_title("Noise Complaints by Hour of the Day")
ax3.set_xlabel("Hour of the Day")
ax3.set_ylabel("Number of Complaints")
ax3.set_xticks(range(0, 24))
ax3.set_xticklabels(
    [format_hour(hour) for hour in range(0, 24)],
    rotation=45,
     ha="right"
)
ax3.grid(True)
plt.tight_layout()
st.pyplot(fig3)

st.markdown("---")

# [VIZ4] Line chart
st.subheader("Complaints by Date")
daily_counts = filtered_df.groupby("Date").size().sort_index()
fig4, ax4 = plt.subplots()
daily_counts.plot(kind="line", marker="o", ax=ax4, color="purple")
ax4.set_title("Noise Complaints by Date")
ax4.set_xlabel("Date")
ax4.set_ylabel("Number of Complaints")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
st.pyplot(fig4)

st.subheader("Top ZIP Codes")
top_zip_df = top_zip_codes.reset_index()
top_zip_df.columns = ["Zip Code", "Complaint Count"]
st.dataframe(top_zip_df, use_container_width=True)

st.markdown("---")




# [MAP]
st.subheader("Complaints Heatmap")
map_df = filtered_df.dropna(subset=["Latitude", "Longitude"])[["Latitude", "Longitude"]].copy()

if len(map_df) > 5000:
    map_df = map_df.sample(5000, random_state=1)

layer = pdk.Layer(
    "HeatmapLayer",
    data=map_df,
    get_position="[Longitude, Latitude]",
    aggregation="SUM",
    get_weight=1,
    radius_pixels=50,
    opacity=0.7
)

view_state = pdk.ViewState(
    latitude=map_df["Latitude"].mean(),
    longitude=map_df["Longitude"].mean(),
    zoom=10,
    pitch=0
)

st.pydeck_chart(
    pdk.Deck(
        layers=[layer],
        initial_view_state=view_state
    )
)

st.markdown("---")

# [DA6] Analyze data with pivot tables
st.subheader("Pivot Table: Complaint Types by Street")

top_n_streets = st.slider(
    "Number of streets to show:",
    5,
    30,
    10
)

top_street_names = filtered_df["Street Name"].value_counts().head(top_n_streets).index
street_df = filtered_df[filtered_df["Street Name"].isin(top_street_names)]

pivot = pd.pivot_table(
    street_df,
    index="Street Name",
    columns="Problem (formerly Complaint Type)",
    values="Unique Key",
    aggfunc="count",
    fill_value=0
)

st.dataframe(pivot, use_container_width=True)



