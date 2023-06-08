import streamlit as st
import time
# ----- LLM
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from app.memory import new_memory
from app.utils import *
# ----- e chart option
from streamlit_echarts import st_echarts
# Demo here: https://echarts.streamlit.app/
# ----- Map import
import pandas as pd
import numpy as np
import pydeck as pdk
# ---- Emoji rain import
from streamlit_extras.let_it_rain import rain

# ----- LLM config
if "query_input" not in st.session_state:
    st.session_state.query_input = ""
if "response" not in st.session_state:
    st.session_state.response = ""
if "requests" not in st.session_state:
    st.session_state["requests"] = []
if "buffer_memory" not in st.session_state:
    st.session_state.buffer_memory = new_memory()
if "model" not in st.session_state:
    st.session_state.model = "gpt-3.5-turbo"
if "top_k" not in st.session_state:
    st.session_state.top_k = 2
if "system_message" not in st.session_state:
    st.session_state.system_message = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, say 'I don't know'
Today, we are the 9 th of June 2023
You will be answering questions from property managers who will be handling apartments, houses, and various types of properties. They will have inquiries regarding their tenants, rents, lease agreements, and more

Here is a dataset about the locations :
| id_appartment | date_entree | date_sortie |
|----------------|--------------|--------------|
| APT001 | 05/01/2022 | 15/02/2022 |
| APT002 | 10/03/2022 | 20/04/2022 |
| APT003 | 02/06/2022 | 30/06/2022 |
| APT004 | 17/08/2022 | 25/09/2022 |
| APT005 | 08/10/2022 | 12/11/2022 |
| APT006 | 02/01/2023 | 20/02/2023 |
| APT007 | 15/03/2023 | 30/04/2023 |
| APT008 | 10/05/2023 | 18/06/2023 |
| APT009 | 01/07/2023 | 10/08/2023 |
| APT010 | 05/09/2023 | 22/10/2023 |
| APT011 | 15/11/2023 | 31/12/2023 |
| APT012 | 08/02/2024 | 25/03/2024 |

Here is a dataset about the appartements :
| id_appartment | appartment_name | appartment_address | rent | payment_delay | status|
|---------------|--------------------|--------------------|------|---------------|
| APT001 | Appartement Harmonie | 10 Rue du Château | 1057 | 729 | occupied|
| APT002 | Résidence Serenity | 22 Avenue des Lilas | 1276 | 182 | unoccupied|
| APT003 | Studio Élégance | 15 Rue de la Gare | 1814 | 555 | unoccupied |
| APT004 | Cozy Haven | 5 Park Lane | 950 | 390 | occupied |
| APT005 | Tranquil Retreat | 8 Meadow Street | 1320 | 920 | occupied |
| APT006 | Urban Oasis | 17 High Rise Avenue | 1785 | 632 | occupied |
| APT007 | Sunny Heights | 25 Sunshine Boulevard | 990 | 165 | unoccupied |
| APT008 | Garden View | 12 Rose Lane | 1450 | 245 | unoccupied |
| APT009 | City Loft | 9 Downtown Street | 1250 | 790 | occupied |
| APT010 | Sea Breeze | 3 Ocean Avenue | 1890 | 420 | unoccupied |
| APT011 | Mountain Retreat | 14 Alpine Drive | 1625 | 315 | unoccupied |
| APT012 | Riverside Haven | 6 River Road | 1075 | 520 | occupied |
| APT013 | Cosmopolitan Living | 21 City Center Square | 1360 | 270 | unoccupied |
| APT014 | Quiet Hideaway | 11 Serene Lane | 1180 | 850 | occupied |
| APT015 | Charming Cottage | 19 Elm Street | 950 | 120 | unoccupied |
| APT016 | Lakeside Retreat | 7 Lakeview Avenue | 1740 | 410 | occupied |
| APT017 | Modern Loft | 16 Urban Street | 1425 | 695 | occupied |
| APT018 | Green Acres | 4 Meadow Lane | 1200 | 235 | unoccupied |
| APT019 | Hilltop Haven | 13 Summit Drive | 1590 | 560 | occupied |
| APT020 | Stylish Condo | 2 Chic Avenue | 1325 | 180 | unoccupied |
| APT021 | Beachfront Paradise | 1 Shoreline Road | 1950 | 760 | occupied |
| APT022 | Quaint Village House | 18 Cottage Lane | 1050 | 350 | unoccupied |
| APT023 | Skyline View | 20 Tower Street | 1280 | 495 | occupied |
you can link this two databases thanks to 'id_appartment"

Here is a dataset about the tenants :
| id_appartment | id_tenants|tenant_name | age | gender| family situation|
|---------------|--------------------|--------------------|------|---------------|
| APT001 | T001 | Pierre | 57 | man | married|
| APT002 | T002|Paul | 22 | man | single |
| APT003 | T003|Marie | 45 | woman | married |
"""

llm = ChatOpenAI(model_name="gpt-3.5-turbo")

system_msg_template = SystemMessagePromptTemplate.from_template(template=st.session_state.system_message)

human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

prompt_template = ChatPromptTemplate.from_messages(
    [
        system_msg_template,
        MessagesPlaceholder(variable_name="history"),
        human_msg_template,
    ]
)

conversation = ConversationChain(
    memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True
)

response_container = st.container()

# ----- Pie
options_pie = {
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "name": "Taux de vacance actuel",
            "type": "pie",
            "radius": ["40%", "70%"],
            "avoidLabelOverlap": False,
            "itemStyle": {
                "borderRadius": 10,
                "borderColor": "#fff",
                "borderWidth": 2,
            },
            "label": {"show": False, "position": "center"},
            "emphasis": {
                "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
            },
            "labelLine": {"show": False},
            "data": [
                {"value": 1048, "name": "Lots occupés"},
                {"value": 735, "name": "Lots vacants"},
            ],
        }
    ],
}
options_pie_fake = {
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "type": "pie",
            "radius": ["40%", "70%"],
            "avoidLabelOverlap": False,
            "itemStyle": {
                "borderRadius": 10,
                "borderColor": "#fff",
                "borderWidth": 2,
            },
            "label": {"show": False, "position": "center"},
            "emphasis": {
                "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
            },
            "labelLine": {"show": False},
            "data": [
                {"value": 1048, "name": "Lots occupés"},
                {"value": 735, "name": "Lots vacants"},
            ],
        }
    ],
}

# ----- Basic table
option_table = np.random.randn(10, 2)
data_table = pd.DataFrame(
   option_table,
   columns=['Référence lot', 'Adresse lot'])

# ----- Map with dot
option_map = np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4]
data_map = pd.DataFrame(
    option_map,
    columns=['LAT', 'LON'])

# ----- 3D Map with heat
option_3d_map = np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4]
data_3d_map = pd.DataFrame(
   option_3d_map,
   columns=['lat', 'lon'])


# ----- Header ------
with st.sidebar:
    st.title("I am your PAIDA, Personnal AI Data Analyst.")
    st.subheader("You can ask me any statistics you would like to get from your data.")
    st.write("I was created by true princesses : The Peaches :peach:")
    st.header("You ask :")
    recorded_prompt1 = st.button("Quand se termine le contrat de l'appartement 22 Avenue des Lilas ?")
    recorded_prompt2 = st.button("Quel est mon taux de vacance aujourd’hui ?")
    fake_prompt1 = st.button("Fake: Quel est mon taux de vacance aujourd’hui ?")
    asked_question = st.button("Peux-tu me vendre du rêve ?")

# ----- Graph ------
with response_container:
    if recorded_prompt1:
        st.session_state.query_input = "What is the end date date associated with the apartment at 22 Avenue des Lilas ?"
        with st.spinner():
            response = conversation.predict(
                input=f"Query:\n{st.session_state.query_input}"
            )
            st.session_state.response = response
            st.title(st.session_state.response)
    
    if recorded_prompt2:
        st.session_state.query_input = "How many appartments are occupied and unoccupied, answer simply with just a table."
        with st.spinner():
            response = conversation.predict(
                input=f"Query:\n{st.session_state.query_input}"
            )
            st.session_state.response = response
            st.title(st.session_state.response)
    
    if fake_prompt1:
        with st.spinner():
            time.sleep(3)
            st.success("Voici le taux de vacance de votre patrimoine aujourd'hui", icon="✅")
            st_echarts(options=options_pie_fake, height="500px")
        
    if asked_question:
        st.pydeck_chart(pdk.Deck(
            map_style=None,
            initial_view_state=pdk.ViewState(
                latitude=37.76,
                longitude=-122.4,
                zoom=11,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                'HexagonLayer',
                data=data_3d_map,
                get_position='[lon, lat]',
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=data_3d_map,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=200,
                ),
            ],
        ))
        st_echarts(options=options_pie, height="500px")
        st.table(data_table)
        st.map(data_map)
        rain(
            emoji="🍑",
            font_size=80,
            falling_speed=10,
            animation_length="10s",
        )