import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv() 
file_path = "/Users/nainishdhanorkar/Downloads/task/macbook-air-13inch-m4-2025-info (1).pdf"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

loader = PyPDFLoader(file_path=file_path)
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
)

splits = text_splitter.split_documents(documents)
len(splits), splits[0].page_content[:200]

vectorstore = FAISS.from_documents(splits, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})


prompt = ChatPromptTemplate.from_template(
    "You are a concise assistant. Use the context to answer.\n"
    "If the answer is not in the context, say you don't know.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}"
)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

