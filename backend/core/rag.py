from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from .vector_store import VectorStoreManager

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
vector_manager = VectorStoreManager()

system_prompt = (
    "You are a specialized assistant. Use only the provided context to answer. "
    "If the answer is not in the context, state 'The answer was not found in the uploaded documents.' "
    "Provide citations in [File: Page] format at the end of your response."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)

def get_chat_response(session_id: str, message: str):
    retriever = vector_manager.get_retriever(session_id)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    response = rag_chain.invoke({"input": message})
    
    sources = []
    for doc in response["context"]:
        sources.append({
            "file_name": doc.metadata["file_name"],
            "page_number": doc.metadata["page_number"]
        })
    
    # Deduplicate sources
    unique_sources = [dict(t) for t in {tuple(d.items()) for d in sources}]
    
    return {
        "answer": response["answer"],
        "sources": unique_sources
    }
