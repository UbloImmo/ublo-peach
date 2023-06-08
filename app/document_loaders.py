# DO NOT USE AS PART OF A CHAIN
# EXECUTE THIS SCRIPT INDEPENDENTLY
# Check https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/pinecone.html

# You can reset your index by running app.indexer.reset_index()

import os

from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone

load_dotenv("./.streamlit/secrets.toml")

# Use the required loader
loader = TextLoader("../../../state_of_the_union.txt")

documents = loader.load()
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1536, chunk_overlap=0
)
embeddings = OpenAIEmbeddings()
docs = text_splitter.split_documents(documents)
Pinecone.from_documents(docs, embeddings, index_name=os.getenv("PINECONE_INDEX"))
