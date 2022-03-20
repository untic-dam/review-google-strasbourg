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
#------------------------------[ M A P ]------------------------------#
#---------------------------------------------------------------------#

#init
carte = folium.Map(location=v.strasbourg_loc, zoom_start=v.zoom_start)

#affichage statique
folium_static(carte)
