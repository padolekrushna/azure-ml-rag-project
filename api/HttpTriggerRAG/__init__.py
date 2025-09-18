import logging
import azure.functions as func
import os
from azure.storage.blob import BlobServiceClient
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# Load env (Azure Functions reads from App Settings)
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = SentenceTransformer('all-MiniLM-L6-v2')
llm = genai.GenerativeModel('gemini-1.5-flash')

def load_faiss_and_chunks():
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client("embeddings")
    
    # Download FAISS index
    blob_client = container_client.get_blob_client("faiss_index.bin")
    index_data = blob_client.download_blob().readall()
    with open("/tmp/faiss_index.bin", "wb") as f:
        f.write(index_data)
    index = faiss.read_index("/tmp/faiss_index.bin")
    
    # Download chunks
    blob_client = container_client.get_blob_client("chunks.pkl")
    chunks_data = blob_client.download_blob().readall()
    with open("/tmp/chunks.pkl", "rb") as f:
        chunks = pickle.loads(chunks_data)
    
    return index, chunks

def search_index(index, chunks, query, top_k=3):
    q_emb = model.encode([query]).astype('float32')
    D, I = index.search(q_emb, top_k)
    return [chunks[i] for i in I[0]]

def generate_answer(question, context):
    prompt = f"Context: {' '.join(context)}\n\nQuestion: {question}\nAnswer:"
    response = llm.generate_content(prompt)
    return response.text

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        question = req_body.get('question')

        index, chunks = load_faiss_and_chunks()
        retrieved = search_index(index, chunks, question)
        answer = generate_answer(question, retrieved)

        return func.HttpResponse(
            json.dumps({"answer": answer}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)