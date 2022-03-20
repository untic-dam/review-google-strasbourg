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

def creation_df_rue(df):

    #groupby
    s_rue_rating_count = df.groupby(['rue'])['rating'].count()
    s_rue_rating_mean = df.groupby(['rue'])['rating'].mean()
    s_rue_rating_nreview = df.groupby(['rue'])['user_ratings_total'].sum()
    s_rue_rating_median = df.groupby(['rue'])['rating'].median()
    s_rue_rating_max = df.groupby(['rue'])['rating'].max()
    s_rue_rating_min = df.groupby(['rue'])['rating'].min()

    #Series to dataframe
    cols = [s_rue_rating_count, s_rue_rating_mean, s_rue_rating_nreview,
            s_rue_rating_median, s_rue_rating_max, s_rue_rating_min]
    df_rue = pd.concat(cols, axis=1)

    #rename cols
    df_rue.columns.values[0] = 'restaurants_par_rue'
    df_rue.columns.values[1] = 'moyenne_par_rue'
    df_rue.columns.values[2] = 'nreview_par_rue'
    df_rue.columns.values[3] = 'mediane_par_rue'
    df_rue.columns.values[4] = 'max_par_rue'
    df_rue.columns.values[5] = 'min_par_rue'


    df_rue.sort_values(by=['restaurants_par_rue'], ascending=False, inplace=True)
    
    return df_rue

df_resto_par_rue = creation_df_rue(df)

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
def creation_list_resto_sidebar(df_resto_par_rue):

    list_resto = []
    list_resto.append('aucune rue')

    for index, row in df_resto_par_rue.iterrows():
        name = index
        n_resto = row['restaurants_par_rue']
        moy = row['moyenne_par_rue']

        txt = "{:.0f} resto(s) | {:.2f} * | {}".format(n_resto, moy, name)

        list_resto.append(txt)

    return list_resto

list_resto = creation_list_resto_sidebar(df_resto_par_rue)

rue_selected = st.sidebar.selectbox('rue :', list_resto)
rue = rue_selected.split(' | ')[-1]


#---------------------------------------------------------------------#
#------------------------------[ M A P ]------------------------------#
#---------------------------------------------------------------------#

#fonction pour générer la carte
def creation_df_carte(df, note_min, note_max, nombre_min, nombre_max, rue):
    df_min_max = df.copy()

    #par note
    df_min_max = df_min_max.loc[df_min_max['rating']>=note_min]
    df_min_max = df_min_max.loc[df_min_max['rating']<=note_max]

    #par nombre
    df_min_max = df_min_max.loc[df_min_max['user_ratings_total']>=nombre_min]
    df_min_max = df_min_max.loc[df_min_max['user_ratings_total']<=nombre_max]

    #par rue
    try:
        if len(list(rue))>1:
            if rue != 'aucune rue':
                df_min_max = df_min_max[df_min_max['rue']==rue]
    except:
        pass
    
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

df_carte = creation_df_carte(df, note_min, note_max, nombre_min, nombre_max, rue)

carte = generate_carte(carte, df_carte)

#affichage statique
folium_static(carte)


