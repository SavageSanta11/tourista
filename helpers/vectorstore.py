from langchain.vectorstores import Pinecone
import pinecone


def init_vectordb():
    index_name = "langchain-retrieval-agent"
    pinecone.init(
        api_key="634516c5-6021-4e6e-b228-e8503912368f", environment="us-west1-gcp-free"
    )

    if index_name not in pinecone.list_indexes():
        # we create a new index
        pinecone.create_index(
            name=index_name,
            metric="dotproduct",
            dimension=768,  # 1536 dim of huggingface embeddings
        )


def create_vector_store(text_field, index_name, embed):
    # switch back to normal index for langchain
    index = pinecone.Index(index_name)

    vectorstore = Pinecone(index, embed.embed_query, text_field)
    return vectorstore
