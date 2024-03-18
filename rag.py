import os

from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.prompts.prompts import QuestionAnswerPrompt
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.extractors import TitleExtractor, SummaryExtractor
from llama_index.core.storage.index_store import SimpleIndexStore

load_dotenv("keys.env")


def create_index(nodes):
    index = VectorStoreIndex(nodes)
    return index

def save_index(index, persist_dir):
    index.storage_context.persist(persist_dir=persist_dir)

def load_index(persist_path):
    # storage_context = StorageContext.from_defaults(persist_path=persist_path)
    # index = load_index_from_storage(storage_context)
    index = SimpleIndexStore.from_persist_path(persist_path)
    return index

def add_documents_to_index(index, documents):
    index.add_documents(documents)
    return index

def create_retriever(index, similarity_top_k=3):
    retriever = VectorIndexRetriever(index, similarity_top_k=similarity_top_k)
    return retriever

def retrieve_and_rerank(retriever, query_str, rerank_top_k=3):
    retrieved_docs = retriever.retrieve(query_str)
    # reranked_docs = retriever.rerank(query_str, retrieved_docs, rerank_top_k)
    print(retrieved_docs)
    
    return retrieved_docs

def generate_prompt(query_str, context_str):
    DEFAULT_TEXT_QA_PROMPT_TMPL = (
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the context information and not prior knowledge, "
        "answer the query.\n"
        "Query: {query_str}\n"
        "Answer: "
    )

    prompt_template = DEFAULT_TEXT_QA_PROMPT_TMPL

    prompt = prompt_template.format(query_str=query_str, context_str=context_str)
    return prompt

def query_index(retriever, query_str, response_mode="default", verbose=False):
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_mode=response_mode,
        verbose=verbose
    )
    response = query_engine.query(query_str)
    return response

def main(stock_symbol="AAPL", query_str="How many iPhones were sold?", context_query_str="iPhone sales"):

    files_dir = "../files/"
    index_dir = f"{files_dir}indexes/{stock_symbol}/"
    files_path = f"{files_dir}{stock_symbol}/"
    # Create an index from documents
    documents = SimpleDirectoryReader(files_path).load_data()

    splitter = SentenceSplitter(
        chunk_size=8192,
        chunk_overlap=1024,
    )

    title_extractor = TitleExtractor(nodes=5)
    summary_extractor = SummaryExtractor()

    pipeline = IngestionPipeline(
        transformations=[splitter, OpenAIEmbedding(), title_extractor]
    )

    nodes = pipeline.run(documents=documents)

    index = create_index(nodes)

    # Save the index
    save_index(index, index_dir)

    # Load the index
    # loaded_index = load_index(index_dir)

    # Add new documents to the index
    # new_documents = SimpleDirectoryReader(f'../files/{stock_symbol}/').load_data()
    # updated_index = add_documents_to_index(loaded_index, new_documents)

    # Create a retriever with re-ranking and select top-k contexts
    retriever = create_retriever(index, similarity_top_k=3)
    nodes = retrieve_and_rerank(retriever, query_str=context_query_str)

    contexts_list = [
        f"<context>{node.text}</context>" for node in nodes
    ]
    context_str = "\n\n".join(contexts_list)
    query_str = f"<query>{query_str}</query>"
    prompt = generate_prompt(query_str, context_str)

    # Query the index
    print(prompt)


if __name__ == "__main__":
    main(stock_symbol="AAPL", query_str="How many iPhones were sold?", context_query_str="iPhone sales")
    