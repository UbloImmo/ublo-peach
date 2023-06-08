import inspect
import logging
import openai


def embed(text):
    logging.warn(f"Embedding text: {text}")
    result = openai.Embedding.create(model="text-embedding-ada-002", input=text)
    return result["data"][0]["embedding"]
