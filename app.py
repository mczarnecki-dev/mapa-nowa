import streamlit as st
import pandas as pd
import folium
from folium.plugins import PolyLineDecorator
from streamlit_folium import st_folium
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import math

# --- Funkcje pomocnicze ---

def azymut(p1, p2):
    """Oblicza azymut w stopniach między dwoma punktami (lat, lon)."""
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dLon = lon2 - lon1
    x = math.sin(dLon) * math.cos(lat2)
    y = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon)
    brng = math.atan2(x, y)
    brng = math.degrees(brng)
    return (brng + 360) % 360

def podobny_kierunek(az1, az2, prog=30):
    diff = abs(az1 - az2)
    return diff <= prog or diff >= 360 - prog

def odleglosc_km(p1, p2):
    return geodesic(p1, p2).km

# --- Inicjalizacja geokodera ---
geolocator = Nominatim(user_agent="mapa_polski_app")

# --- Wczytanie tras istniejących ---
@st.cache_data
def wczytaj_trasy(sciezka):
    df = pd.read_csv(sciezka)
    return df

# --- Funkcja do geokodowania nazwy miejscowości ---
@st.cache_data
def geokoduj(nazwa):
    try:
        lokalizacja = geolocator.geocode(f"{nazwa}, Polska")
        if lokalizacja:
            return (lokalizacja.latitude, lokalizacja.longitude)
    except:
        return None

# --- Interfejs ---

st.title("Mapa Polski - Wybór trasy i porównanie z istniejącymi trasami")

# Wczytaj istniejące trasy
trasy_df = wczytaj_trasy("trasy.csv")

input_z = st.text_input("Z (miejsce startowe):")
input_do = st.text_input("Do (miejsce docelowe):")

if input_z and input_do:
    start_coords = geokoduj(input_z)
    end_coords = geokoduj(input_do)

    if not start_coords or not end_coords:
        st.error("Nie udało się znaleźć współrzędnych dla podanych miejscowości.")
    else:
        # Oblicz azymut nowej trasy
        nowy_azymut = azymut(start_coords, end_coords)

        # Filtruj trasy istniejące według warunków
        trasy_pasujace = []
        for _, row in trasy_df.iterrows():
            start_exist = (row["lat_z"], row["lon_z"])
            end_exist = (row["lat_do"], row["lon_do"])
            az_exist = azymut(start_exist, end_exist)
            dist = odleglosc_km(end_exist, end_coords)

            if podobny_kierunek(nowy_azymut, az_exist) and dist <= 50:
                trasy_pasujace.append(row)

        # Rysowanie mapy
        srodek_mapy = [(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2]
        mapa = folium.Map(location=srodek_mapy, zoom_start=6)

        # Nowa trasa - linia z strzałką
        linia_nowa = folium.PolyLine(locations=[start_coords, end_coords], color="blue", weight=5).add_to(mapa)
        arrow_nowa = PolyLineDecorator(linia_nowa, patterns=[dict(offset='100%', repeat='100%', symbol=folium.Symbol.arrowHead(color='blue', size=15))])
        mapa.add_child(arrow_nowa)

        folium.Marker(start_coords, tooltip="Start nowej trasy: " + input_z, icon=folium.Icon(color='green')).add_to(mapa)
        folium.Marker(end_coords, tooltip="Cel nowej trasy: " + input_do, icon=folium.Icon(color='red')).add_to(mapa)

        # Istniejące pasujące trasy (czerwone)
        for t in trasy_pasujace:
            start_exist = (t["lat_z"], t["lon_z"])
            end_exist = (t["lat_do"], t["lon_do"])
            linia_exist = folium.PolyLine(locations=[start_exist, end_exist], color="orange", weight=4, opacity=0.7).add_to(mapa)
            arrow_exist = PolyLineDecorator(linia_exist, patterns=[dict(offset='100%', repeat='100%', symbol=folium.Symbol.arrowHead(color='orange', size=12))])
            mapa.add_child(arrow_exist)
            folium.Marker(start_exist, tooltip="Start istniejącej trasy", icon=folium.Icon(color='darkred', icon='info-sign')).add_to(mapa)
            folium.Marker(end_exist, tooltip="Cel istniejącej trasy", icon=folium.Icon(color='darkred', icon='info-sign')).add_to(mapa)

        st_folium(mapa, width=800, height=600)
else:
    st.info("Proszę wpisz miejscowości Z i Do, aby zobaczyć mapę tras.")
