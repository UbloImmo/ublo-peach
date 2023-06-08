import streamlit as st

from app.embeds import embed
from app.indexer import find_matches
from app.refine import refine_query


def search_context(input, top_k=2):
    input_em = embed(input)
    results = find_matches(input_em, top_k=top_k)

    return "\n".join(results)


def query_refiner(conversation, query):
    return refine_query(conversation, query)


def get_conversation_string():
    conversation_string = ""
    for i in range(len(st.session_state["responses"]) - 1):
        conversation_string += "Human: " + st.session_state["requests"][i] + "\n"
        conversation_string += "Bot: " + st.session_state["responses"][i + 1] + "\n"
    return conversation_string
