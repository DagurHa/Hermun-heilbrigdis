import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pydeck as pdk

st.title("Graph Plotting with Streamlit")

x = np.linspace(-10, 10, 100)
y = np.sin(x)
 
display_graph = st.checkbox("Display Graph")

if display_graph:

    fig, ax = plt.subplots()

    ax.plot(x, y)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Sine Wave")

    st.pyplot(fig)

chart_data = pd.DataFrame(
     5*np.random.randn(100, 3),
     columns=['DH job', 'KR job', 'AÁK job'])

st.line_chart(chart_data)

chart_data = pd.DataFrame(
   np.random.randn(1000, 2) / [50, 50] + [64.14, -21.948],
   columns=['lat', 'lon'])

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=64.14,
        longitude=-21.948,
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
           'HexagonLayer',
           data=chart_data,
           get_position='[lon, lat]',
           radius=200,
           elevation_scale=4,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=chart_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))