import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium

import variables as v


st.title("Les Notes Google Maps des Restautants de Strasborg - Partie I")

st.write("""
    Les données ont récolté avec l'API Google Places (lien).\n 
    L'objectif est de visualiser l'ensemble des notes récoltées sur Google Maps
""")

#---------------------------------------------------------------------#
#----------------------------[ Load DF ]------------------------------#
#---------------------------------------------------------------------#

df = pd.read_csv(v.data_csv)
st.dataframe(df)

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

#---- Recherche par rue


#---------------------------------------------------------------------#
#------------------------------[ M A P ]------------------------------#
#---------------------------------------------------------------------#

#init
carte = folium.Map(location=v.strasbourg_loc, zoom_start=v.zoom_start)

#affichage statique
folium_static(carte)


