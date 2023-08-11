from langchain import PromptTemplate

from langchain.chat_models import ChatOpenAI

from langchain.chains.conversation.memory import (
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
    ConversationSummaryMemory,
)

from langchain.chains import (
    ConversationalRetrievalChain,
    RetrievalQA,
    ConversationChain,
)

from langchain.llms import OpenAI


def init_conversational_agent(vectorstore):
    llm = ChatOpenAI(
        openai_api_key="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",
        model_name="gpt-3.5-turbo",
        temperature=0.0,
    )

    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", k=12, return_messages=True, output_key="answer"
    )

    retriever = vectorstore.as_retriever()

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        memory=memory,
        retriever=retriever,
    )

    return qa
