from langchain.vectorstores import Pinecone
import pinecone

def init_vectordb():
    index_name = 'langchain-retrieval-agent'
    pinecone.init(
        api_key='b8e3aad9-951d-4ba5-8057-40172bab8644',
        environment='us-west4-gcp-free'
    )

    if index_name not in pinecone.list_indexes():
        # we create a new index
        pinecone.create_index(
            name=index_name,
            metric='dotproduct',
            dimension=768  # 1536 dim of huggingface embeddings
        )


def create_vector_store(text_field, index_name, embed):

    # switch back to normal index for langchain
    index = pinecone.Index(index_name)

    vectorstore = Pinecone(
        index, embed.embed_query, text_field
    )
    return vectorstore
    