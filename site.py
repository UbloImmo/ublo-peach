from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)
import streamlit as st
from streamlit_chat import message
from app.memory import new_memory
from app.utils import *
from app.csv_loaders import load_csv_to_sqlite
from app.schema_functions import print_db_schema
from app.schema_functions import get_table_db_schema
import re


############## DB PART BEGINNING #########################

import pandas as pd
import os

data_dir = './data'  # Directory relative to the current script

# Check if the directory does not exist
if not os.path.exists(data_dir):
    # Create the directory
    os.makedirs(data_dir)

# DB Mgmt
import sqlite3
# conn = sqlite3.connect('data/world.sqlite')
load_csv_to_sqlite('data/DATA2_Appartement.csv', 'appartement')
conn = load_csv_to_sqlite('data/DATA2_Location.csv', 'location')
c = conn.cursor()


# Rename the SQLite Table
# ALTER TABLE student
#       ADD CONSTRAINT fk_student_city_id
#       FOREIGN KEY (city_id) REFERENCES city(id)

# renameTable = '''ALTER TABLE location
#     ADD CONSTRAINT id_appartement
#       FOREIGN KEY (id_appartement) REFERENCES appartement(id)'''



# c.execute(renameTable)

# Fxn Make Execution
def sql_executor(raw_code):
	c.execute(raw_code)
	data = c.fetchall()
	return data


city = ['ID,', 'Name,', 'CountryCode,', 'District,', 'Population']
country = ['Code,', 'Name,', 'Continent,', 'Region,', 'SurfaceArea,', 'IndepYear,', 'Population,', 'LifeExpectancy,', 'GNP,', 'GNPOld,', 'LocalName,', 'GovernmentForm,', 'HeadOfState,', 'Capital,', 'Code2']
countrylanguage = ['CountryCode,', 'Language,', 'IsOfficial,', 'Percentage']

############## DB PART END #########################

st.subheader("Langchain playground")

if "responses" not in st.session_state:
    st.session_state.responses = ["Ublo sait tout !"]
if "requests" not in st.session_state:
    st.session_state["requests"] = []
if "buffer_memory" not in st.session_state:
    st.session_state.buffer_memory = new_memory()
if "model" not in st.session_state:
    st.session_state.model = "gpt-3.5-turbo"
if "top_k" not in st.session_state:
    st.session_state.top_k = 2
if "system_message" not in st.session_state:
    st.session_state.system_message ="""
        Today is: Thursday. June 8, 2023.
        `id_appartement` is a foreign key between the two tables.
        `surface_appartement` is the living area of an appartment in square meter.
        `loyer_appartement` is the monthly rent in euros.
        `nombre_locataires` is the number of renters for the corresponding appartement.
        `date_debut` is the lease starting date.
        `date_fin` is the lease end date.
        If `vacant` is true, the appartment is occupied and available for new renters otherwise it is currently rented.
        `impaye_locataire` is the current tenant debt in euros.
        Answer the question as truthfully as possible, and if the answer is not contained within the text below, say 'I don't know'.
    """

with st.sidebar:
    model_select_value = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4"], key="model")
    top_k = st.number_input(
        "Number of fetched results", key="top_k", step=1, min_value=1, max_value=10
    )
    system_message = st.text_area("System Message", key="system_message", height=600)

llm = ChatOpenAI(model_name=model_select_value) # type: ignore

table_data = get_table_db_schema('data/demo.db', conn)
formatted_string = "\n\n".join([
    f"Table: {item['table']}\ncolumns: {', '.join(item['columns'])}"
    for item in table_data
])
st.write(formatted_string)

templateSystem=f"""
    You're a SQL developer able to generate all sql queries based only on this table, you should only send sql queries when possible, otherwise send null as message in all other cases.
    You must enclose your sql script in a span tag
    {formatted_string}
"""


# Générer la représentation en chaîne de caractères



system_msg_template = SystemMessagePromptTemplate.from_template(template=templateSystem)

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
query_explorer_container = st.container()

with text_container:
    query = st.text_input("Query: ", key="input")
    if query:
        with st.spinner("typing..."):
            conversation_string = get_conversation_string()
            response = conversation.predict(
                input=f"Query:\n{query}"
            )

            result = re.search('<span>(.*?)</span>', response)
            if result:
                query_results = sql_executor(result.group(1))
                st.write(query_results)

        st.session_state.requests.append(query)
        st.session_state.responses.append(response)

# with response_container:
#     if st.session_state["responses"]:
#         for i in range(len(st.session_state["responses"])):
#             message(st.session_state["responses"][i], key=str(i))
#             if i < len(st.session_state["requests"]):
#                 message(
#                     st.session_state["requests"][i], is_user=True, key=str(i) + "_user"
#                 )

with query_explorer_container:
    st.subheader("HomePage")

    # st.write(print_db_schema('data/demo.db', conn, st))
    print_db_schema('data/demo.db', conn, st)
    # Columns/Layout
    col1,col2 = st.columns(2)
    with col1:
        with st.form(key='query_form'):
            raw_code = st.text_area("SQL Code Here")
            submit_code = st.form_submit_button("Execute")

    # Table of Info

    with st.expander("Table Info"):
        table_info = {'city':city,'country':country,'countrylanguage':countrylanguage}
        st.json(get_table_db_schema('data/demo.db', conn))
        # st.json(table_info)


    # Results Layouts
    with col2:
        if submit_code:
            st.info("Query Submitted")
            st.code(raw_code)

            # Results
            query_results = sql_executor(raw_code)
            with st.expander("Results"):
                st.write(query_results)

            with st.expander("Pretty Table"):
                query_df = pd.DataFrame(query_results)
                st.dataframe(query_df)

                # nombre total d'appartement
                # l'adresse de l'appartement avec le loyer le plus élevé