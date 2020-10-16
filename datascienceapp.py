import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

#data_url = ("")
#use the directory where the dataset is located

st.title("Motor Vehicle Collisions in New York city") #dataset provided by NYPD
st.markdown("This application is a Streamlit Dashboard that can be used"
"to analyze motor vehicle collision in NYC")

@st.cache(persist=True) #only reruns if code or input has changed, so once slider is changed only cache is used
def load_data(rows): #large dataset so need to speciy number of rows to load
    data = pd.read_csv(data_url, nrows = rows, parse_dates = [['CRASH_DATE','CRASH_TIME']] ) #parse the dates and convert them into pandas date time format
    data.dropna(subset = ['LATITUDE', 'LONGITUDE'], inplace = True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis = 'columns', inplace = True)
    data.rename(columns = {'crash_date_crash_time': 'date/time'}, inplace = True) #long name, need to change
    return data

data = load_data(100000)
original_data = data

st.header("Where in NYC do most injuries take place?")
injuries = st.slider("Number of people injured in vehicle collisions", 0, 19) #max injuries at a given spot found out my investigation of data
st.map(data.query("injured_persons >= @injuries")[["latitude","longitude"]].dropna(how = "any")) #lowercase na dropped, whole row



if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)

st.header("How many collisions occured during a particular time in a day?")
hour = st.slider("Hour", 0,23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" %(hour, (hour+1)%24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers = [
        pdk.Layer(
        "HexagonLayer",
        data = data[['date/time','latitude','longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 100,
        extruded = True,
        pickable = True,
        elevation_scale = 4,
        elevation_range = [0,1000],
        ),
    ],
))

st.subheader("Breakdown of collisions by minute between %i:00 and %i:00" % (hour, (hour+1)%24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]

hist = np.histogram(filtered['date/time'].dt.minute, bins = 60, range = (0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'number of crashes': hist})
fig = px.bar(chart_data, x = 'minute', y='number of crashes', hover_data = ['minute', 'number of crashes'], height = 400)
st.write(fig)

st.header("5 most dangerous streets in New York by affected type")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])
if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=["injured_pedestrians"], ascending = False).dropna(how = 'any')[:5])
    #if pedestrians is selected, query unfiltered data and then look for injured pedestrians,
    #return stret names, sorted by injuries in descending for top 5

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=["injured_cyclists"], ascending = False).dropna(how = 'any')[:5])
else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=["injured_motorists"], ascending = False).dropna(how = 'any')[:5])
