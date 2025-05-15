import streamlit as st
import folium
from streamlit_folium import st_folium
import math

# Przykładowe miejscowości z współrzędnymi
miejscowosci = [
    {"nazwa": "Warszawa", "lat": 52.22977, "lon": 21.01178},
    {"nazwa": "Kraków", "lat": 50.06465, "lon": 19.94498},
    {"nazwa": "Gdańsk", "lat": 54.35205, "lon": 18.64637},
    {"nazwa": "Wrocław", "lat": 51.10789, "lon": 17.03854},
    {"nazwa": "Poznań", "lat": 52.40637, "lon": 16.92517},
]

def znajdz_miejscowosci(query, lista, limit=10):
    query = query.lower()
    wyniki = [m for m in lista if m["nazwa"].lower().startswith(query)]
    return wyniki[:limit]

def azymut(p1, p2):
    lat1 = math.radians(p1[0])
    lon1 = math.radians(p1[1])
    lat2 = math.radians(p2[0])
    lon2 = math.radians(p2[1])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dlon)
    brng = math.atan2(x, y)
    brng = math.degrees(brng)
    return (brng + 360) % 360

st.title("Mapa Polski - wybierz miejscowości")

input_z = st.text_input("Z (miejsce startowe)")
wyniki_z = znajdz_miejscowosci(input_z, miejscowosci) if input_z else []
wybor_z = None
if wyniki_z:
    nazwy_z = [m["nazwa"] for m in wyniki_z]
    wybor_z = st.selectbox("Wybierz miejscowość startową", nazwy_z)

input_do = st.text_input("Do (miejsce docelowe)")
wyniki_do = znajdz_miejscowosci(input_do, miejscowosci) if input_do else []
wybor_do = None
if wyniki_do:
    nazwy_do = [m["nazwa"] for m in wyniki_do]
    wybor_do = st.selectbox("Wybierz miejscowość docelową", nazwy_do)

if wybor_z and wybor_do:
    start = next(m for m in miejscowosci if m["nazwa"] == wybor_z)
    end = next(m for m in miejscowosci if m["nazwa"] == wybor_do)

    mapa = folium.Map(location=[(start["lat"] + end["lat"]) / 2, (start["lon"] + end["lon"]) / 2], zoom_start=6)

    folium.Marker([start["lat"], start["lon"]],
                  tooltip="Start: " + start["nazwa"],
                  icon=folium.Icon(color='green')).add_to(mapa)
    folium.Marker([end["lat"], end["lon"]],
                  tooltip="Cel: " + end["nazwa"],
                  icon=folium.Icon(color='red')).add_to(mapa)

    folium.PolyLine(locations=[[start["lat"], start["lon"]], [end["lat"], end["lon"]]],
                    color="blue", weight=5).add_to(mapa)

    # Oblicz środek linii
    mid_lat = (start["lat"] + end["lat"]) / 2
    mid_lon = (start["lon"] + end["lon"]) / 2

    # Dodajemy ikonę strzałki na środku trasy
    arrow_icon = folium.CustomIcon(
        icon_image="https://cdn-icons-png.flaticon.com/512/32/32195.png",
        icon_size=(30, 30)
    )
    folium.Marker(location=[mid_lat, mid_lon],
                  icon=arrow_icon,
                  tooltip="Kierunek trasy").add_to(mapa)

    st_folium(mapa, width=700, height=500)
else:
    st.write("Wpisz i wybierz miejscowości startową i docelową, aby zobaczyć trasę.")
