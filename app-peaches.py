import streamlit as st
import time
import re
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

# from app
from app.csv_loaders import load_csv_to_sqlite
from app.schema_functions import print_db_schema
from app.schema_functions import get_table_db_schema

load_csv_to_sqlite('data/DATA2_Appartement.csv', 'appartement')
conn = load_csv_to_sqlite('data/DATA2_Location.csv', 'location')
c = conn.cursor()

table_data = get_table_db_schema('data/demo.db', conn)
formatted_string = "\n\n".join([
    f"Table: {item['table']}\ncolumns: {', '.join(item['columns'])}"
    for item in table_data
])

# ----- LLM config
if "query_input" not in st.session_state:
    st.session_state.query_input = ""
if "response" not in st.session_state:
    st.session_state.response = ""
if "responses" not in st.session_state:
    st.session_state.responses = ""
if "requests" not in st.session_state:
    st.session_state["requests"] = []
if "buffer_memory" not in st.session_state:
    st.session_state.buffer_memory = new_memory()
if "model" not in st.session_state:
    st.session_state.model = "gpt-3.5-turbo"
if "top_k" not in st.session_state:
    st.session_state.top_k = 2
if "system_message" not in st.session_state:
    st.session_state.system_message = f"""
    You're a SQL developer able to generate all sql queries based only on this table, you should only send sql queries when possible, otherwise send null as message in all other cases.
    You must enclose your sql script in a span tag
    {formatted_string}
"""

llm = ChatOpenAI(model_name="gpt-3.5-turbo") # type: ignore

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
text_container = st.container()

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
    recorded_prompt_input = st.button("Demander une statistique à l'IA ")
    recorded_prompt1 = st.button("Quand se termine le contrat de l'appartement 14 Rue Lecourbe ?")
    recorded_prompt2 = st.button("Quel est mon taux de vacance aujourd’hui ?")
    asked_question = st.button("Peux-tu me vendre du rêve ?")

# ----- Inout ------
# Fxn Make Execution
def sql_executor(raw_code):
	c.execute(raw_code)
	data = c.fetchall()
	return data
# Quel est le top 5 des appartements avec le loyer le plus élevé ?

def display_data(data):
    result = re.search('<span>(.*?)</span>', data)
    if result:
        query_results = sql_executor(result.group(1))
        st.header(f"La requête est isolée de la réponse:\n\n`{result.group(1)}`")
        st.write("---")
        st.header(f"La résultat de la requête sur la BDD")
        st.json(query_results)
        return query_results

with response_container:
    query = st.text_input("Rechercher dans Ublo: ", key="input_container")
    if query:
        with st.spinner("Recherche..."):
            response = conversation.predict(
                input=f"Query:\n{query}"
            )
            display_data(response)

# ----- Graph ------
with response_container:
    if recorded_prompt1:
        st.session_state.query_input = "Date_fin associated with the apartment that adresse_appartement is '14 Rue Lecourbe, 75015 Paris'"
        st.title("Quand se termine le contrat de l'appartement 14 Rue Lecourbe ?")
        with st.spinner():
            response = conversation.predict(
                input=f"Query:\n{st.session_state.query_input}"
            )
            st.session_state.response = response
            display_data(response)

    if recorded_prompt2:
        st.session_state.query_input = "How many appartments are vacant and how many appartments are not vacant"
        with st.spinner():
            response = conversation.predict(
                input=f"Query:\n{st.session_state.query_input}"
            )
            st.session_state.response = response
            st.title("Quel est mon taux de vacance aujourd’hui ?")
            results = display_data(response)
            if results :
                st.write("---")
                st.header("Graph: ")
                st_echarts({
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
                                {"value": results[0][1], "name": "Lots occupés"},
                                {"value": results[1][1], "name": "Lots vacants"},
                            ],
                        }
                    ],
                }  , height="500px")

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