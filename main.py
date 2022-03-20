from operator import ge
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
nombre_min = int(st.sidebar.text_input('nombre minimum', 1))

nombre_max = int(st.sidebar.text_input('nombre maximum', 1000))

#---- Recherche par rue



#---------------------------------------------------------------------#
#------------------------------[ M A P ]------------------------------#
#---------------------------------------------------------------------#

def creation_df_carte(df, note_min, note_max, nombre_min, nombre_max, rue):
    df_min_max = df.copy()

    #par note
    df_min_max = df_min_max.loc[df_min_max['rating']>=note_min]
    df_min_max = df_min_max.loc[df_min_max['rating']<=note_max]

    #par nombre
    df_min_max = df_min_max.loc[df_min_max['user_ratings_total']>=nombre_min]
    df_min_max = df_min_max.loc[df_min_max['user_ratings_total']<=nombre_max]

    #par rue
    if len(list(rue))>1:
        df_min_max = df_min_max[df_min_max['rue']==rue]
    
    return df_min_max

def generate_carte(carte, df):

    for index, row in df.iterrows():
        lat = row['lat']
        lon = row['lon']
        name = row['name']
        rating = row['rating']
        n_rating = row['user_ratings_total']
        txt_tooltip = f"{name} | {rating} * | {n_rating} évaluation(s)"
        txt_popup = f"{name} {rating} * {n_rating} évaluation(s)"

        folium.Marker([lat, lon], tooltip=txt_tooltip, popup=txt_popup).add_to(carte)

    return carte

#init
carte = folium.Map(location=v.strasbourg_loc, zoom_start=v.zoom_start)

df_carte = creation_df_carte(df, note_min, note_max, nombre_min, nombre_max, rue='')

carte = generate_carte(carte, df_carte)


#affichage statique
folium_static(carte)


