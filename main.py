import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium

import variables as v

#---------------------------------------------------------------------#
#------------------------------[ HEAD ]-------------------------------#
#---------------------------------------------------------------------#

st.title("Les Notes Google Maps des Restautants de Strasborg - Partie I")

st.write("""
    Les données ont récolté avec l'API Google Places (lien).\n 
    L'objectif est de visualiser l'ensemble des notes récoltées sur Google Maps
""")




#---------------------------------------------------------------------#
#----------------------------[ Load DF ]------------------------------#
#---------------------------------------------------------------------#

df = pd.read_csv(v.data_csv)



#---------------------------------------------------------------------#
#---------------------------[ Side Bar ]------------------------------#
#---------------------------------------------------------------------#

st.sidebar.header('Recherche')

#---- Recherche par notes
st.sidebar.write("Recherche Par Note :")
note_min = st.sidebar.slider(label="note minimale :", 
                            min_value=v.note_min, 
                            max_value=v.note_max, 
                            step=v.note_step)

note_max = st.sidebar.slider(label="note maximale :", 
                            min_value=v.note_min, 
                            max_value=v.note_max, 
                            step=v.note_step)

#---- Recherche par nombre de review
st.sidebar.write("Recherche Par Nombre de Review :")
nombre_min = st.sidebar.text_input('nombre minimum', 1)

nombre_max = st.sidebar.text_input('nombre maximum', 1000)

#---- Recherche par rue



#---------------------------------------------------------------------#
#------------------------------[ M A P ]------------------------------#
#---------------------------------------------------------------------#

#init
carte = folium.Map(location=v.strasbourg_loc, zoom_start=v.zoom_start)

def generate_carte_rating(carte, df, rating_min, rating_max):
    
    #range selection
    df_rating_min = df.loc[df['rating']>=rating_min]
    df_rating_min_max = df_rating_min.loc[df_rating_min['rating']<=rating_max]

    for index, row in df_rating_min_max.iterrows():
        lat = row['lat']
        lon = row['lon']
        name = row['name']
        rating = row['rating']
        n_rating = row['user_ratings_total']
        txt_tooltip = f"{name} | {rating} * | {n_rating} évaluation(s)"
        txt_popup = f"{name} {rating} * {n_rating} évaluation(s)"

        folium.Marker([lat, lon], tooltip=txt_tooltip, popup=txt_popup).add_to(carte)


    return carte

carte = generate_carte_rating(carte, df, note_min, note_max)

#affichage statique
folium_static(carte)


