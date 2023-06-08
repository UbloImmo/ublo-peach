from langchain.chains.conversation.memory import ConversationBufferWindowMemory


def new_memory():
    return ConversationBufferWindowMemory(k=3, return_messages=True)
