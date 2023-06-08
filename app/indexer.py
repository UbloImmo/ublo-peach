import logging
import pinecone
import os
import streamlit as st


def create_index():
    if os.getenv("PINECONE_INDEX") not in pinecone.list_indexes():
        logging.info("[Indexer] Creating index")
        pinecone.create_index(
            os.getenv("PINECONE_INDEX"), metric="cosine", shards=1, dimension=1536
        )


def drop_index():
    if os.getenv("PINECONE_INDEX") in pinecone.list_indexes():
        logging.info("[Indexer] Dropping index")
        pinecone.delete_index(os.getenv("PINECONE_INDEX"))


def reset_index():
    drop_index()
    create_index()


@st.cache_resource
def init_pinecone():
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV")
    )
    create_index()


@st.cache_resource
def get_index():
    return pinecone.Index(os.getenv("PINECONE_INDEX"))


def find_matches(embed, top_k=2):
    logging.info(f"[Indexer] Finding top {top_k} matches")
    result = get_index().query(embed, top_k=top_k, includeMetadata=True)
    return [match["metadata"]["text"] for match in result["matches"]]


def index_document(text, embed):
    logging.info(f"[Indexer] Indexing document")
    get_index().upsert(embed, metadata={"text": text})


init_pinecone()
