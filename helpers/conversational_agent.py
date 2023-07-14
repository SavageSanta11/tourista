from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import RetrievalQA


def init_conversational_agent(vectorstore):
    llm = ChatOpenAI(
        openai_api_key="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",
        model_name="gpt-3.5-turbo",
        temperature=0.0,
    )
    conversational_memory = ConversationBufferWindowMemory(
        memory_key="chat_history", k=5, return_messages=True
    )
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever()
    )
    return qa
