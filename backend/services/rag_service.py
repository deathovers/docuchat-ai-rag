from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from backend.config import settings

class RAGService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.llm = ChatOpenAI(model="gpt-4o", streaming=True)

    def _get_vectorstore(self, session_id: str):
        return PineconeVectorStore(
            index_name=settings.PINECONE_INDEX_NAME,
            embedding=self.embeddings,
            namespace=session_id
        )

    async def ingest_pdf(self, pages_data, filename, session_id):
        documents = []
        for page in pages_data:
            chunks = self.text_splitter.split_text(page["text"])
            for chunk in chunks:
                documents.append(Document(
                    page_content=chunk,
                    metadata={
                        "source": filename,
                        "page": page["page"],
                        "session_id": session_id
                    }
                ))
        
        vectorstore = self._get_vectorstore(session_id)
        vectorstore.add_documents(documents)

    def get_chat_chain(self, session_id: str):
        vectorstore = self._get_vectorstore(session_id)
        
        template = """Answer the question based only on the following context. 
        If the answer is not present in the context, state: 'The answer was not found in the uploaded documents.'
        Include citations in the format [Filename - Page X].

        Context: {context}
        Question: {question}
        Answer:"""
        
        QA_CHAIN_PROMPT = PromptTemplate(
            input_variables=["context", "question"],
            template=template,
        )

        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT}
        )
