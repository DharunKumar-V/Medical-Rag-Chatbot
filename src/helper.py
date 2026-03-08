import os
import warnings
warnings.filterwarnings("ignore")

from pypdf import PdfReader
import re

def clean_text(text):
    """Clean and preprocess text for better embeddings"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep medical terms
    text = re.sub(r'[^\w\s\.\,\-\+\%\(\)]', '', text)
    return text.strip()

def load_pdf(data_folder):
    """Load and clean PDF files"""
    documents = []
    pdf_files = [f for f in os.listdir(data_folder) if f.endswith('.pdf')]
    
    print(f"Found {len(pdf_files)} PDF files")
    
    for filename in pdf_files:
        file_path = os.path.join(data_folder, filename)
        try:
            print(f"Processing: {filename}")
            reader = PdfReader(file_path)
            text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    cleaned_text = clean_text(page_text)
                    if cleaned_text:
                        text += cleaned_text + "\n"
            
            if text.strip():
                documents.append({
                    'page_content': text,
                    'metadata': {'source': filename, 'pages': page_num + 1}
                })
                print(f"✓ Loaded {filename} ({len(text)} chars)")
            else:
                print(f"✗ No text extracted from {filename}")
                
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    return documents

def smart_text_split(extracted_data, chunk_size=400, chunk_overlap=50):
    """Smart text splitting that respects sentence boundaries"""
    text_chunks = []
    
    for doc in extracted_data:
        text = doc['page_content']
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        for sentence in sentences:
            # If adding this sentence exceeds chunk size, save current chunk
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                text_chunks.append({
                    'page_content': current_chunk.strip(),
                    'metadata': doc['metadata']
                })
                # Keep overlap for context
                overlap_sentences = current_chunk.split()[-20:]  # Last 20 words
                current_chunk = ' '.join(overlap_sentences) + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Don't forget the last chunk
        if current_chunk.strip():
            text_chunks.append({
                'page_content': current_chunk.strip(),
                'metadata': doc['metadata']
            })
    
    print(f"Created {len(text_chunks)} smart text chunks")
    return text_chunks

def download_hugging_face_embeddings():
    """Use sentence-transformers with optimizations"""
    try:
        from sentence_transformers import SentenceTransformer
        
        # Load model with optimizations
        model = SentenceTransformer(
            'all-MiniLM-L6-v2',
            device='cpu',  # Force CPU for compatibility
        )
        
        # Warm up the model
        model.encode(["warmup text"])
        
        class SimpleEmbeddings:
            def __init__(self, model):
                self.model = model
            
            def embed_documents(self, texts):
                return self.model.encode(
                    texts,
                    batch_size=32,
                    show_progress_bar=False,
                    convert_to_numpy=True
                ).tolist()
            
            def embed_query(self, text):
                return self.model.encode([text]).tolist()[0]
        
        print("✓ Embeddings model loaded and warmed up")
        return SimpleEmbeddings(model)
        
    except Exception as e:
        print(f"Error loading embeddings: {e}")
        raise