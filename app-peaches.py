import streamlit as st
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
# ----- e chart option
from streamlit_echarts import st_echarts
# Demo here: https://echarts.streamlit.app/
# ----- Map import
import pandas as pd
import numpy as np
# ---- Emoji rain import
from streamlit_extras.let_it_rain import rain

st.set_page_config(page_title="Peaches App", page_icon=":peach:", layout="wide")

# ----- LLM config
if "responses" not in st.session_state:
    st.session_state.responses = ["How can I assist you?"]
if "requests" not in st.session_state:
    st.session_state["requests"] = []
if "buffer_memory" not in st.session_state:
    st.session_state.buffer_memory = new_memory()
if "model" not in st.session_state:
    st.session_state.model = "gpt-3.5-turbo"
if "top_k" not in st.session_state:
    st.session_state.top_k = 2
if "system_message" not in st.session_state:
    st.session_state.system_message = "Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, say 'I don't know'"

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
options = {
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

# ----- Basic table
data_table = pd.DataFrame(
   np.random.randn(10, 2),
   columns=['Référence lot', 'Adresse lot'])

# ----- Map with dot
data_map = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['LAT', 'LON'])



# ----- Header ------
with st.sidebar:
    st.title("I am your PAIDA, Personnal AI Data Analyst.")
    st.subheader("You can ask me any statistics you would like to get from your data.")
    st.write("I was created by true princesses : The Peaches :peach:")
    st.write("---")
    st.header("You ask :")
    asked_question1 = st.button("Quel est mon taux de vacance aujourd’hui ?")
    asked_question2 = st.button("Peux-tu me vendre du rêve ?")

# ----- Graph ------
with response_container:
    if asked_question1:
        st.header("I deliver :")
        st_echarts(options=options, height="500px")
        st.table(data_table)
        st.map(data_map)
    if asked_question2:
        rain(
            emoji="🍑",
            font_size=80,
            falling_speed=10,
            animation_length="10s",
        )