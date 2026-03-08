from datasets import load_dataset
import chromadb
import pandas as pd

def add_medical_dataset_correct():
    """Correct import for this specific dataset structure"""
    
    print("🚀 Loading medical dataset with correct structure...")
    ds = load_dataset("ruslanmv/ai-medical-chatbot")
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_collection("medical-chatbot")
    
    documents = []
    metadatas = []
    ids = []
    
    if 'train' in ds:
        train_data = ds['train']
        print(f"📊 Processing {len(train_data)} medical conversations...")
        
        for i, example in enumerate(train_data):
            description = str(example['Description']) if example['Description'] else ""
            patient_msg = str(example['Patient']) if example['Patient'] else ""
            doctor_response = str(example['Doctor']) if example['Doctor'] else ""
            
            # Create multiple document versions for better retrieval
            
            # Version 1: Full conversation
            if patient_msg and doctor_response:
                full_conversation = f"Patient: {patient_msg}\nDoctor: {doctor_response}"
                documents.append(full_conversation)
                metadatas.append({
                    "type": "full_conversation",
                    "source": "ai-medical-chatbot",
                    "has_patient": True,
                    "has_doctor": True,
                    "description": description[:100]
                })
                ids.append(f"full_conv_{i}")
            
            # Version 2: Just doctor's response (for direct answers)
            if doctor_response:
                documents.append(doctor_response)
                metadatas.append({
                    "type": "doctor_response",
                    "source": "ai-medical-chatbot", 
                    "is_answer": True,
                    "description": description[:100]
                })
                ids.append(f"doc_resp_{i}")
            
            # Version 3: Patient question + doctor response
            if patient_msg and doctor_response:
                qa_pair = f"Question: {patient_msg} Answer: {doctor_response}"
                documents.append(qa_pair)
                metadatas.append({
                    "type": "qa_pair",
                    "source": "ai-medical-chatbot",
                    "has_question": True,
                    "has_answer": True
                })
                ids.append(f"qa_pair_{i}")
            
            # Version 4: Description + doctor response (for context)
            if description and doctor_response:
                desc_doc = f"Medical context: {description}. Professional advice: {doctor_response}"
                documents.append(desc_doc)
                metadatas.append({
                    "type": "contextual",
                    "source": "ai-medical-chatbot",
                    "has_description": True
                })
                ids.append(f"ctx_doc_{i}")
            
            # Show progress
            if (i + 1) % 1000 == 0:
                print(f"📝 Processed {i + 1}/{len(train_data)} conversations...")
                print(f"   - Documents collected: {len(documents)}")
    
    print(f"\n📋 Total documents to add: {len(documents)}")
    
    # Add to ChromaDB in batches
    if documents:
        batch_size = 100
        total_added = 0
        
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            
            try:
                collection.add(
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx],
                    ids=ids[i:end_idx]
                )
                total_added += (end_idx - i)
                print(f"💾 Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1} - Total: {total_added} documents")
            except Exception as e:
                print(f"⚠️ Error in batch {i//batch_size + 1}: {e}")
                continue
        
        print(f"🎉 Successfully added {total_added} medical documents to ChromaDB!")
        
        # Verify the addition
        verify_count = collection.count()
        print(f"🔍 Total documents in ChromaDB now: {verify_count}")
        
        return total_added
    else:
        print("❌ No documents were created. This shouldn't happen with this dataset.")
        return 0

def test_retrieval():
    """Test if the data was added correctly"""
    
    print("\n🧪 Testing retrieval...")
    
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_collection("medical-chatbot")
    
    # Test queries
    test_queries = [
        "What is fever?",
        "How to treat headache?",
        "Symptoms of diabetes",
        "Back pain treatment"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        results = collection.query(
            query_texts=[query],
            n_results=2,
            include=["documents", "distances", "metadatas"]
        )
        
        if results['documents'][0]:
            print(f"✅ Found {len(results['documents'][0])} results")
            for j, doc in enumerate(results['documents'][0]):
                print(f"   Result {j+1}: {doc[:100]}...")
        else:
            print("   ❌ No results found")

if __name__ == "__main__":
    print("=== Medical Dataset Import (Corrected) ===")
    
    # Import the data
    added_count = add_medical_dataset_correct()
    
    # Test retrieval
    if added_count > 0:
        test_retrieval()
        
    print(f"\n✅ Import complete! Added {added_count} medical conversation documents.")