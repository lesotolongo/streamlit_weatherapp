import streamlit as st
import requests
import plotly
import json


st.title("Weather and Air Quality Web App")
st.header("Streamlit and AirVisual API")

api_key = "your api key"


@st.cache_data
def map_creator(latitude, longitude):
    from streamlit_folium import folium_static
    import folium

    # center on the station
    m = folium.Map(location=[latitude, longitude], zoom_start=10)

    # add marker for the station
    folium.Marker([latitude, longitude], popup="Station", tooltip="Station").add_to(m)

    # call to render Folium map in Streamlit
    folium_static(m)


@st.cache_data
def generate_list_of_countries():
    countries_url = f"https://api.airvisual.com/v2/countries?key={api_key}"
    countries_dict = requests.get(countries_url).json()
    # st.write(countries_dict)
    return countries_dict


@st.cache_data
def generate_list_of_states(country_selected):
    states_url = f"https://api.airvisual.com/v2/states?country={country_selected}&key={api_key}"
    states_dict = requests.get(states_url).json()
    # st.write(states_dict)
    return states_dict


@st.cache_data
def generate_list_of_cities(state_selected, country_selected):
    cities_url = f"https://api.airvisual.com/v2/cities?state={state_selected}&country={country_selected}&key={api_key}"
    cities_dict = requests.get(cities_url).json()
    # st.write(cities_dict)
    return cities_dict


# TODO: Include a select box for the options: ["By City, State, and Country","By Nearest City (IP Address)","By Latitude and Longitude"]
# and save its selected option in a variable called category

category = st.sidebar.selectbox(
    "Select a location by category:",
    ("By City, State, and Country", "By Nearest City (IP Address)", "By Latitude and Longitude"),
    index=None,
    placeholder="Select a location...",
)
st.write(f"Location: {category}")

if category == "By City, State, and Country":
    countries_dict = generate_list_of_countries()
    if countries_dict["status"] == "success":
        countries_list = []
        for i in countries_dict["data"]:
            countries_list.append(i["country"])
        countries_list.insert(0, "")

        country_selected = st.selectbox("Select a country", options=countries_list)
        if country_selected:
            # TODO: Generate the list of states, and add a select box for the user to choose the state

            states_dict = generate_list_of_states(country_selected)
            if states_dict["status"] == "success":
                states_list = [""]
                states_list.extend([state["state"] for state in states_dict["data"]])
                state_selected = st.selectbox("Select a state", options=states_list)

            if state_selected:

                # TODO: Generate the list of cities, and add a select box for the user to choose the city

                cities_dict = generate_list_of_cities(state_selected, country_selected)
                if cities_dict["status"] == "success":
                    cities_list = [""]
                    cities_list.extend([city["city"] for city in cities_dict["data"]])
                    city_selected = st.selectbox("Select a city", options=cities_list)

                if city_selected:
                    aqi_data_url = f"https://api.airvisual.com/v2/city?city={city_selected}&state={state_selected}&country={country_selected}&key={api_key}"
                    aqi_data_dict = requests.get(aqi_data_url).json()

                    if aqi_data_dict["status"] == "success":

                        city_data = aqi_data_dict["data"]
                        temp_celsius = city_data['current']['weather']['tp']
                        temp_fahrenheit = (temp_celsius * 9 / 5) + 32
                        st.subheader(
                            f"Weather and Air Quality in {city_selected}, {state_selected}, {country_selected}")
                        col1, col2, col3, = st.columns(3)
                        col1.metric("Temperature", f"{temp_celsius} °C/ {temp_fahrenheit} °F")
                        col2.metric("Humidity", f"{city_data['current']['weather']['hu']}%")
                        col3.metric("Air Quality Index", f"{city_data['current']['pollution']['aqius']}")

                        map_creator(city_data["location"]["coordinates"][1], city_data["location"]["coordinates"][0])

                    else:
                        st.warning("No data available for this location.")

            else:
                st.warning("No stations available, please select another state.")
        else:
            st.warning("No stations available, please select another country.")
    else:
        st.error("Too many requests. Wait for a few minutes before your next API call.")

elif category == "By Nearest City (IP Address)":
    url = f"https://api.airvisual.com/v2/nearest_city?key={api_key}"
    aqi_data_dict = requests.get(url).json()

    if aqi_data_dict["status"] == "success":
        city_data = aqi_data_dict["data"]
        temp_celsius = city_data['current']['weather']['tp']
        temp_fahrenheit = (temp_celsius * 9 / 5) + 32
        city_name = city_data["city"]
        state_name = city_data["state"]
        country_name = city_data["country"]

        st.subheader(
            f"Weather and Air Quality in {city_name}, {state_name}, {country_name} (Nearest City)")
        col1, col2, col3, = st.columns(3)
        col1.metric("Temperature", f"{temp_celsius} °C/ {temp_fahrenheit} °F")
        col2.metric("Humidity", f"{city_data['current']['weather']['hu']}%")
        col3.metric("Air Quality Index", f"{city_data['current']['pollution']['aqius']}")

        map_creator(city_data["location"]["coordinates"][1], city_data["location"]["coordinates"][0])

    else:
        st.warning("No data available for this location.")

elif category == "By Latitude and Longitude":
    latitude = st.text_input("Enter Latitude, ex: 25.793449")
    longitude = st.text_input("Enter Longitude, ex: -80.139198")

    if latitude and longitude:
        url = f"https://api.airvisual.com/v2/nearest_city?lat={latitude}&lon={longitude}&key={api_key}"
        aqi_data_dict = requests.get(url).json()

        if aqi_data_dict["status"] == "success":
            city_data = aqi_data_dict["data"]
            temp_celsius = city_data['current']['weather']['tp']
            temp_fahrenheit = (temp_celsius * 9 / 5) + 32
            city_name = city_data["city"]
            state_name = city_data["state"]
            country_name = city_data["country"]

            st.subheader(f"Weather and Air Quality in {city_name}, {state_name}, {country_name} "
                         f"(Nearest to {latitude}, {longitude})")
            col1, col2, col3, = st.columns(3)
            col1.metric("Temperature", f"{temp_celsius} °C/ {temp_fahrenheit} °F")
            col2.metric("Humidity", f"{city_data['current']['weather']['hu']}%")
            col3.metric("Air Quality Index", f"{city_data['current']['pollution']['aqius']}")

            map_creator(latitude, longitude)

        else:
            st.warning("No data available for this location.")
