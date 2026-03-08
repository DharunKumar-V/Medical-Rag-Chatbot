from src.helper import load_pdf, smart_text_split, download_hugging_face_embeddings
import chromadb
import os
import time

def main():
    print("🚀 Starting optimized medical knowledge base setup...")
    start_time = time.time()
    
    # Step 1: Load PDFs
    print("\n📖 Step 1: Loading PDF documents...")
    extracted_data = load_pdf("data/")
    if not extracted_data:
        print("❌ No documents found in data/ folder")
        return
    print(f"✓ Loaded {len(extracted_data)} documents")
    
    # Step 2: Split text intelligently
    print("\n✂️ Step 2: Splitting text into smart chunks...")
    text_chunks = smart_text_split(extracted_data, chunk_size=400, chunk_overlap=50)
    print(f"✓ Created {len(text_chunks)} text chunks")
    
    # Step 3: Initialize ChromaDB with optimizations
    print("\n🗄️ Step 3: Initializing ChromaDB...")
    client = chromadb.PersistentClient(path="chroma_db")
    
    # Delete existing collection if it exists (for fresh start)
    try:
        client.delete_collection("medical-chatbot")
        print("✓ Cleared existing collection")
    except:
        print("✓ Creating new collection")
    
    collection = client.create_collection(
        name="medical-chatbot",
        metadata={
            "description": "Optimized medical knowledge base",
            "chunk_size": "400",
            "chunk_overlap": "50"
        }
    )
    
    # Step 4: Prepare documents for efficient storage
    print("\n💾 Step 4: Storing documents in ChromaDB...")
    
    documents = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(text_chunks):
        documents.append(chunk['page_content'])
        metadatas.append({
            'source': chunk['metadata']['source'],
            'chunk_id': i,
            'length': len(chunk['page_content'])
        })
        ids.append(f"med_chunk_{i}")
        
        # Show progress
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(text_chunks)} chunks...")
    
    # Batch add to ChromaDB for better performance
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        end_idx = min(i + batch_size, len(documents))
        
        collection.add(
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )
        print(f"  Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
    
    # Verify storage
    count = collection.count()
    print(f"✓ Successfully stored {count} documents in ChromaDB")
    
    total_time = time.time() - start_time
    print(f"\n🎉 Data indexing complete in {total_time:.2f} seconds!")
    print("📊 Collection info:")
    print(f"   - Total chunks: {count}")
    print(f"   - Average chunk size: {sum(len(d) for d in documents) // len(documents)} chars")
    print(f"   - Storage location: ./chroma_db")

if __name__ == "__main__":
    main()