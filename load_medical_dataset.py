from datasets import load_dataset
import pandas as pd
import chromadb

def load_and_explore_medical_dataset():
    """Load the medical chatbot dataset and explore its structure"""
    
    print("📥 Loading AI Medical Chatbot dataset...")
    
    try:
        # Load the dataset
        ds = load_dataset("ruslanmv/ai-medical-chatbot")
        print("✅ Dataset loaded successfully!")
        
        # Explore the dataset structure
        print(f"\n📊 Dataset structure: {ds}")
        print(f"📁 Splits available: {list(ds.keys())}")
        
        # Let's look at the first few examples
        if 'train' in ds:
            print(f"\n🔍 First 3 examples from training set:")
            for i in range(min(3, len(ds['train']))):
                print(f"Example {i+1}:")
                for key, value in ds['train'][i].items():
                    print(f"  {key}: {value}")
                print()
        
        return ds
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None

def convert_to_dataframe(ds):
    """Convert the dataset to pandas DataFrame for easier handling"""
    
    if 'train' in ds:
        df = pd.DataFrame(ds['train'])
        print(f"📋 Converted to DataFrame with {len(df)} rows")
        print(f"📝 Columns: {list(df.columns)}")
        return df
    else:
        print("❌ No 'train' split found in dataset")
        return None

if __name__ == "__main__":
    dataset = load_and_explore_medical_dataset()
    if dataset:
        df = convert_to_dataframe(dataset)