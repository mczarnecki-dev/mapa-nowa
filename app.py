import streamlit as st
import pandas as pd
import folium
from folium.plugins import PolyLineDecorator
from streamlit_folium import st_folium

# --- Przykładowa lista miejscowości ---
miejscowosci = [
    {"nazwa": "Warszawa", "lat": 52.22977, "lon": 21.01178},
    {"nazwa": "Kraków", "lat": 50.06465, "lon": 19.94498},
    {"nazwa": "Gdańsk", "lat": 54.35205, "lon": 18.64637},
    {"nazwa": "Wrocław", "lat": 51.10789, "lon": 17.03854},
    {"nazwa": "Poznań", "lat": 52.40637, "lon": 16.92517},
    # dopisz więcej lub wczytaj z pliku CSV
]

# Lista nazw miejscowości do selectboxów
nazwy_miejscowosci = [m["nazwa"] for m in miejscowosci]

st.title("Mapa Polski - wybierz miejscowości")

wybor_z = st.selectbox("Z (miejsce startowe)", nazwy_miejscowosci)
wybor_do = st.selectbox("Do (miejsce docelowe)", nazwy_miejscowosci)

if wybor_z and wybor_do:
    start = next(m for m in miejscowosci if m["nazwa"] == wybor_z)
    end = next(m for m in miejscowosci if m["nazwa"] == wybor_do)

    mapa = folium.Map(location=[(start["lat"]+end["lat"])/2, (start["lon"]+end["lon"])/2], zoom_start=6)

    folium.Marker([start["lat"], start["lon"]], tooltip="Start: " + start["nazwa"], icon=folium.Icon(color='green')).add_to(mapa)
    folium.Marker([end["lat"], end["lon"]], tooltip="Cel: " + end["nazwa"], icon=folium.Icon(color='red')).add_to(mapa)

    # Rysujemy linię między punktami
    linia = folium.PolyLine(locations=[[start["lat"], start["lon"]], [end["lat"], end["lon"]]], color="blue", weight=5).add_to(mapa)

    # Dodajemy strzałkę pokazującą kierunek (od start do celu)
    dekorator = PolyLineDecorator(linia, patterns=[dict(offset='100%', repeat='100%', symbol=folium.Symbol.arrowHead(color='blue', size=15))])
    mapa.add_child(dekorator)

    st_folium(mapa, width=700, height=500)
