import streamlit as st
import airbnb_class as ac
import pandas as pd
import numpy as np 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import folium
from streamlit_folium import st_folium
import os

abs_path = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="Airbn Price Predictor", page_icon="🏨")

check_prediction_pressed = False

# Store data in Streamlit caché

@st.cache(allow_output_mutation=True)
def load_ci_madrid_barcelona():
    return city_instance_mb.load_model_joblib(os.path.join(abs_path, "..", "resources", "models", "model_madrid_barcelona.gz"))

@st.cache(allow_output_mutation=True)
def load_ci_london():
    return city_instance_london.load_model_joblib(os.path.join(abs_path, "..", "resources", "models", "model_london.gz"))

@st.cache(allow_output_mutation=True)
def load_madrid_csv():
    return os.path.join(abs_path, "..", "resources", "datasets", "madrid.csv")

@st.cache(allow_output_mutation=True)
def load_barcelona_csv():
    return os.path.join(abs_path, "..", "resources", "datasets", "barcelona.csv")

@st.cache(allow_output_mutation=True)
def load_london_csv():
    return os.path.join(abs_path, "..", "resources", "datasets", "london.csv")

@st.cache(allow_output_mutation=True)
def create_instance_mb():
    d_csvs, d_names = dict(), dict()
    d_csvs["csvs1"] = [madrid, barcelona]
    d_names["names1"] = ["madrid","barcelona"]

    return ac.airbnb(d_csvs["csvs1"], d_names["names1"], "csv")

@st.cache(allow_output_mutation=True)
def create_instance_london():
    d_csvs, d_names = dict(), dict()
    d_csvs["csvs2"] = [london]
    d_names["names2"] = ["london"]

    return ac.airbnb(d_csvs["csvs2"], d_names["names2"], "csv")

madrid = load_madrid_csv()
barcelona = load_barcelona_csv()
london = load_london_csv()

city_instance_mb = create_instance_mb()
city_instance_london = create_instance_london()

model_madrid_barcelona = load_ci_madrid_barcelona()
model_london = load_ci_london()


X_scaler_madrid_barcelona = city_instance_mb.load_model_pickle(os.path.join(abs_path, "..", "resources", "models", "x_scaler_mb"), "pkl")
y_scaler_madrid_barcelona = city_instance_mb.load_model_pickle(os.path.join(abs_path, "..", "resources", "models", "y_scaler_mb"), "pkl")
city_encoder_madrid_barcelona = city_instance_mb.load_model_pickle(os.path.join(abs_path, "..", "resources", "models", "city_encoder_mb"), "pkl")
neighbourhood_encoder_madrid_barcelona = city_instance_mb.load_model_pickle(os.path.join(abs_path, "..", "resources", "models", "neighbourhood_encoder_mb"), "pkl")
X_scaler_london = city_instance_london.load_model_pickle(os.path.join(abs_path, "..", "resources", "models", "x_scaler_london"), "pkl")
y_scaler_london = city_instance_london.load_model_pickle(os.path.join(abs_path, "..", "resources", "models", "y_scaler_london"), "pkl")
city_encoder_london = city_instance_london.load_model_pickle(os.path.join(abs_path, "..", "resources", "models", "city_encoder_london"), "pkl")
neighbourhood_encoder_london = city_instance_london.load_model_pickle(os.path.join(abs_path, "..", "resources", "models", "neighbourhood_encoder_london"), "pkl")


tab_model, tab_mapas = st.tabs(["Predictive model","Map of your neighbourhood"])


with tab_model:

    st.title('Predictive model')


# Asking the user the features of their space

    city = st.selectbox('Select your city', options = ["Madrid", "Barcelona", "London"])

    if city == "Madrid" or city == "Barcelona":

        df_city = city_instance_mb.return_initial_df()

    else: 

        df_city = city_instance_london.return_initial_df()

    house_type = st.selectbox('Select your kind of Airbnb', options = ['Entire home/apt', 'Private room', 'Shared room'])

    d_room_type = {'Entire home/apt': 0 , 'Private room': 0, 'Shared room' : 0}

    d_room_type[house_type] = 1

    neighbourhood = st.selectbox('Select the neighbourhood', options = df_city[df_city["city"]==city.lower()]["neighbourhood_cleansed"].sort_values().unique())

    host_total_listings_count = st.slider("Select your listings count", 0, 100)

    accommodates =st.slider("Select the number of accommodates", 0, 15)

    bathrooms_text = st.slider("Select the number of bathrooms", 0, 5)

    bedrooms = st.slider("Select number of bedrooms", 0, 10)

    beds = st.slider("Select number of beds", 0, 20)

    minimum_nights = st.slider("Select minimum nights", 0, 365)

    maximum_nights = st.slider("Select maximum nights", 0, 365)

    availability_365 = st.slider("Select the days it will be avaliable in a year", 0, 365)

    number_of_reviews = st.slider("Select the number of reviews you have in Airbnb", 0, 10000)

    reviews_per_month = st.slider("Select the number of reviews per month you have in Airbnb", 0, 50)

    
    st.subheader("Amenities")

    col_1, col_2 = st.columns(2)

    check_amenitie0 = col_1.checkbox("Long term stays allowed",help="")
    check_amenitie1 = col_1.checkbox("Cooking basics",help="")
    check_amenitie2 = col_1.checkbox("Dishes and silverware",help="")
    check_amenitie3 = col_1.checkbox("Essentials",help="")
    check_amenitie4 = col_1.checkbox("Coffee maker",help="")

    check_amenitie5 = col_2.checkbox("Hair dryer",help="")
    check_amenitie6 = col_2.checkbox("Microwave",help="")
    check_amenitie7 = col_2.checkbox("Refrigerator",help="")
    check_amenitie8 = col_2.checkbox("Heating",help="")
    check_amenitie9 = col_2.checkbox("Air conditioning",help="")


    l_amenities = [check_amenitie0, check_amenitie1, check_amenitie2,check_amenitie3 , check_amenitie4,check_amenitie5 , check_amenitie6, check_amenitie7, check_amenitie8,  check_amenitie9 ]

    for enum,i in enumerate(l_amenities):
        if i ==True:
            l_amenities[enum] = 1
        else:
            l_amenities[enum] = 0

    # User DataFrame

    d_columns = {'neighbourhood_cleansed': neighbourhood, 'city':city.lower(), 'accommodates': accommodates, 'availability_365': availability_365, 'bathrooms_text': bathrooms_text, 'bedrooms': bedrooms, 'beds': beds, 'minimum_nights':minimum_nights, 
                'maximum_nights':maximum_nights, 'number_of_reviews': number_of_reviews, 'reviews_per_month':reviews_per_month, 'host_total_listings_count':host_total_listings_count, 'Long term stays allowed':l_amenities[0], 'Cooking basics':l_amenities[1], 
                'Dishes and silverware':l_amenities[2], 'Essentials':l_amenities[3], 'Coffee maker':l_amenities[4], 'Hair dryer':l_amenities[5], 'Microwave':l_amenities[6], 'Refrigerator':l_amenities[7], 'Heating':l_amenities[8], 
                'Air conditioning':l_amenities[9], 'Entire home/apt':d_room_type["Entire home/apt"], 'Private room':d_room_type["Private room"], 'Shared room':d_room_type["Shared room"]}

    df_user = pd.DataFrame(d_columns.items())
    df_user = df_user.T
    df_user = df_user.rename(columns=df_user.iloc[0])

    if df_user.shape[0]>1:
        df_user.drop(df_user.index[0], inplace=True)


    # Working with the user´s data to get the prediction array


    if city == "Madrid" or city == "Barcelona":

        df_user = city_instance_mb.norm_enc_prediction([city_encoder_madrid_barcelona, neighbourhood_encoder_madrid_barcelona], X_scaler_madrid_barcelona, df_user, ["city", "neighbourhood_cleansed"])


    else:

        df_user = city_instance_london.norm_enc_prediction([city_encoder_london, neighbourhood_encoder_london], X_scaler_london, df_user, ["city", "neighbourhood_cleansed"])


    nparr_prediction = df_user


    # Prediction

    check_prediction = st.button("Ready, give me the prediction!!",help="")

    if check_prediction:

        # Final prediction

        if city == "Madrid" or city == "Barcelona":

            city_instance_mb.predict_price(nparr_prediction, model_madrid_barcelona, y_scaler_madrid_barcelona)                                                  

            prediction = city_instance_mb.return_prediction()

            st.header(f"The predicted price is: {round(prediction[0][0])}.00 euros")

        else: 

            city_instance_london.predict_price(nparr_prediction, model_london, y_scaler_london)                                                  

            prediction = city_instance_london.return_prediction()

            st.header(f"The predicted price is: {round(prediction[0][0])}.00 euros")



with tab_mapas:


    st.header("Air BNB in your neighbourhood")

    st.write(f"City: {city}")

    st.write(f"Neighbourhood: {neighbourhood}")

    df_group_neighbourhood = df_city.groupby("neighbourhood_cleansed", as_index=False).mean()

    lat = df_group_neighbourhood[df_group_neighbourhood["neighbourhood_cleansed"] == neighbourhood]["latitude"]
    long = df_group_neighbourhood[df_group_neighbourhood["neighbourhood_cleansed"] == neighbourhood]["longitude"]
    
    df_neighbourhood = df_city[df_city["neighbourhood_cleansed"] == neighbourhood].head(20)

    mapa = folium.Map(location = [lat, long], zoom_start = 15)

    airbnb_map = folium.map.FeatureGroup()

    for lat, lng,  price in zip(df_neighbourhood["latitude"], df_neighbourhood["longitude"], df_neighbourhood['price']):

        airbnb_map.add_child(folium.Marker(location        = [lat, lng],
                                            popup          = [f"Precio airbnb: {price}"],
                                            icon           = folium.Icon(icon = "fa-building-o",
                                                             icon_color       = "white",
                                                             color            = "black",
                                                             prefix           = "fa")))  


    mapa.add_child(airbnb_map)

    st_folium(mapa, width=900, height=550)