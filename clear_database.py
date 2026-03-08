import chromadb
import os
import shutil

def clear_chromadb():
    print("🗑️ Clearing ChromaDB...")
    
    try:
        # Method 1: Delete the entire chroma_db folder
        if os.path.exists("chroma_db"):
            shutil.rmtree("chroma_db")
            print("✅ Deleted chroma_db folder")
        else:
            print("ℹ️ chroma_db folder doesn't exist")
        
        # Method 2: Also try to delete collection via client
        try:
            client = chromadb.PersistentClient(path="chroma_db")
            client.delete_collection("medical-chatbot")
            print("✅ Deleted medical-chatbot collection")
        except:
            print("ℹ️ No collection to delete")
            
        print("\n🎯 ChromaDB cleared successfully!")
        print("Next steps:")
        print("1. Run: python store_index.py  (to rebuild with all PDFs)")
        print("2. Run: python app.py  (to start chatbot)")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    clear_chromadb()