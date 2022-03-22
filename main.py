from operator import ge
from tkinter import N
import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium
from plotly.offline import iplot

import variables as v

#---------------------------------------------------------------------#
#------------------------------[ HEAD ]-------------------------------#
#---------------------------------------------------------------------#

st.title("Les Notes Google Maps 🗺️ des Restautants 🍽️ de Strasbourg")

st.markdown("""
    **L'objectif** est de pouvoir visualiser l'ensemble des reviews Google Maps afin d'aider les fins gourmets à trouver un bon restaurant (et aider les restaurateurs à voir comment se positionne leurs voisins).
    \nLes données ont été récolté avec l'API [Google Places](https://developers.google.com/maps/documentation/places/web-service/overview).
    \n Le projet est dans sa phase n°1 : visualiser les notes des différents restaurants à partir des fichiers JSON fournis par l'API Google Places.
    \nLa phase n°2 proposera un enrichissement de la base de données à l'aide d'une exploration des sites web des différents restuarants afin de trouver le type de cuisine.
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

#---- Recherche par classement ---------------------------------------#
st.sidebar.write("-----")
n_resto = df.shape[0]
st.sidebar.write(f"Recherche Par classement :")
rang_min = int(st.sidebar.text_input('top', v.param_values['rang_min']))
rang_max = int(st.sidebar.text_input('', v.param_values['rang_max']))


#---- Recherche par notes ---------------------------------------------#
st.sidebar.write("-----")
st.sidebar.write("Recherche Par Note :")
note_min = st.sidebar.slider(label="note minimale :", 
                            min_value=v.note_min, max_value=v.note_max, 
                            value=v.param_values['note_min'],
                            step=v.note_step)

note_max = st.sidebar.slider(label="note maximale :", 
                            min_value=v.note_min, max_value=v.note_max, 
                            value=v.param_values['note_max'], 
                            step=v.note_step)


#---- Recherche par nombre de review ---------------------------------#
st.sidebar.write("-----")
st.sidebar.write("Recherche Par Nombre de Review :")
nombre_min = int(st.sidebar.text_input('nombre minimum', v.param_values['nombre_min']))

nombre_max = int(st.sidebar.text_input('nombre maximum', v.param_values['nombre_max']))


#---- Recherche par rue -----------------------------------------------#
st.sidebar.write("-----")
st.sidebar.write("Recherche Par Rue :")

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
st.header('Carte 🗺️ :')

def reset_parametres(df):
    """
    Reinit les paramètres afficher dans le sidebar 
    en fonction du df_carte 

    Args:
        df (DataFrame): DataFrame contenant tous les restaurants
                        selon les paramètres du sidebar

    Returns:
        ditc : dict contenat tous les paramètres de la sidebar
    """

    value_reseted = {
        'rang_min': df['ranking'].min(),
        'rang_max': df['ranking'].max(),

        'note_min': df['rating'].min(),
        'note_max': df['rating'].max(),

        'nombre_min': df['user_ratings_total'].min(),
        'nombre_max': df['user_ratings_total'].max()
    }

    return value_reseted
    


#fonction pour générer la carte
def creation_df_carte(df, rang_min, rang_max,
                    note_min, note_max, 
                    nombre_min, nombre_max, 
                    rue):

    df_min_max = df.copy()

    #par rang
    df_min_max = df_min_max.loc[df_min_max['ranking']>=rang_min]
    df_min_max = df_min_max.loc[df_min_max['ranking']<=rang_max]

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

df_carte = creation_df_carte(df, rang_min, rang_max, note_min, note_max, nombre_min, nombre_max, rue)

carte = generate_carte(carte, df_carte)

#affichage statique
folium_static(carte, width=800, height=400)




#---------------------------------------------------------------------#
#----------------------------[ Txt Stat ]-----------------------------#
#---------------------------------------------------------------------#
st.header('Quelques infos ℹ️ :')

#affiche quelques info de la carte
def format_millier_avec_espace(nombre):
    return "{:,}".format(nombre).replace(',', ' ')

#nombre de restaurants
carte_n_resto = df_carte.shape[0]
carte_n_resto_str = format_millier_avec_espace(carte_n_resto)
carte_sum_review = df_carte['user_ratings_total'].sum()
carte_sum_review_str = format_millier_avec_espace(carte_sum_review)
carte_note_moy = df_carte['rating'].mean()
st.markdown("""
                il y a **{}** 🍽️ restaurants affiché sur la carte.\n
                Pour un total de **{}** 👥 review et une note moyenne de **{:.2f}** ⭐.
            """.format(carte_n_resto_str, carte_sum_review_str, carte_note_moy)) 

#moyenne et nombre de review
carte_note_min = df_carte['rating'].min()
carte_note_max = df_carte['rating'].max()
carte_nombre_min = df_carte['user_ratings_total'].min()
carte_nombre_max = df_carte['user_ratings_total'].max()
#mise en forme pour éviter 1,637 et avoir plutôt 1 637 (avec un espace)
carte_nombre_min_str = "{:,}".format(carte_nombre_min).replace(',', ' ')
carte_nombre_max_str = "{:,}".format(carte_nombre_max).replace(',', ' ')

st.markdown("""
                Les notes moyennes sont comprises entre **{}** et **{}** ⭐. \n
                pour un nombre de review oscillant entre **{}** et **{}** 👥.
            """.format(carte_note_min, carte_note_max, carte_nombre_min_str, carte_nombre_max_str))





#---------------------------------------------------------------------#
#------------------------------[ V I Z ]------------------------------#
#---------------------------------------------------------------------#
st.header('Regardons ça de plus prés 👓 📈 :')

st.markdown("Voici les données utilisées pour la carte.")
st.dataframe(df_carte)

#df_carte.iplot()




#---------------------------------------------------------------------#
#---------------------------[ A propos ]------------------------------#
#---------------------------------------------------------------------#
st.markdown("""
    Réalisé par [Damien Jacob](https://twitter.com/Jaco_bDamien).
    \nGithub du projet : [https://github.com/untic-dam/review-google-strasbourg](https://github.com/untic-dam/review-google-strasbourg)
    """)

st.header("**Et Bon Appétit**")