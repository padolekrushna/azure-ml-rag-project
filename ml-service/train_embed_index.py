# train_embed_index.py

import os
import pickle
import faiss
import numpy as np
from azure.storage.blob import BlobServiceClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load env (for local testing)
load_dotenv()

# Initialize model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Azure Blob setup
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

def chunk_text(text, max_len=300):
    sentences = text.split('. ')
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) < max_len:
            current += s + ". "
        else:
            chunks.append(current.strip())
            current = s + ". "
    if current: chunks.append(current.strip())
    return chunks

def download_document_from_blob(filename):
    container_client = blob_service_client.get_container_client("documents")
    blob_client = container_client.get_blob_client(filename)
    data = blob_client.download_blob().readall()
    return data.decode('utf-8')

def upload_to_blob(container_name, blob_name, data):
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(data, overwrite=True)
    print(f"✅ Uploaded {blob_name} to {container_name}")

def main():
    # Get document name from environment (passed during job)
    doc_name = os.getenv("DOCUMENT_NAME", "sample.txt")

    print(f"📥 Downloading {doc_name} from Blob Storage...")
    text = download_document_from_blob(doc_name)

    print("✂️ Chunking text...")
    chunks = chunk_text(text)
    print(f"📄 Created {len(chunks)} chunks.")

    print("🧠 Embedding chunks...")
    embeddings = model.encode(chunks).astype('float32')

    print("🏗️ Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index and chunks locally
    faiss.write_index(index, "faiss_index.bin")
    with open("chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    # Upload to Blob Storage
    with open("faiss_index.bin", "rb") as f:
        upload_to_blob("embeddings", "faiss_index.bin", f)

    with open("chunks.pkl", "rb") as f:
        upload_to_blob("embeddings", "chunks.pkl", f)

    print("🎉 FAISS index and chunks saved to Azure Blob Storage!")

if __name__ == "__main__":
    main()