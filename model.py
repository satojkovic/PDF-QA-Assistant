from langchain_community.chat_models.ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain.vectorstores.utils import filter_complex_metadata
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser


class ChatPDF:
    vector_store = None
    retriever = None
    chain = None

    def __init__(self, model="llama3.1"):
        self.model = ChatOllama(model=model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        self.prompt = PromptTemplate.from_template(
            """
            <s> [INST] You are an assistant for question-answering tasks. Use the following pieces of retrieved context 
            to answer the question. If you don't know the answer, just say that you don't know. Use three sentences
             maximum and keep the answer concise. [/INST] </s> 
            [INST] Question: {question} 
            Context: {context} 
            Answer: [/INST]
            """
        )

    def ingest(self, pdf_file_path: str):
        docs = PyPDFLoader(file_path=pdf_file_path).load()
        print(f"Loaded {len(docs)} pages from PDF")
        for i, doc in enumerate(docs[:2]):  # Print first 2 pages for debugging
            print(f"Page {i+1} content preview: {doc.page_content[:200]}...")
        
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)
        print(f"Created {len(chunks)} chunks after splitting")

        vector_store = Chroma.from_documents(
            documents=chunks, embedding=OllamaEmbeddings(model="llama3.1")
        )
        self.retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 5,
            },
        )

        self.chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.model
            | StrOutputParser()
        )

    def ask(self, query: str):
        if not self.chain:
            return "Please add a PDF document first."

        return self.chain.invoke(query)

    def clear(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None
