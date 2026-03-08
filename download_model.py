import requests
import os
import sys

def download_model():
    print("🚀 Starting model download from verified sources...")
    
    # Create Models directory
    os.makedirs("Models", exist_ok=True)
    
    # GUARANTEED WORKING URLs - DialoGPT models from Microsoft
    models = [
        {
            "name": "DialoGPT Small (Fastest)",
            "url": "https://huggingface.co/microsoft/DialoGPT-small/resolve/main/pytorch_model.bin",
            "filename": "dialogpt-small.bin",
            "type": "dialogpt"
        },
        {
            "name": "DialoGPT Medium (Good Balance)", 
            "url": "https://huggingface.co/microsoft/DialoGPT-medium/resolve/main/pytorch_model.bin",
            "filename": "dialogpt-medium.bin",
            "type": "dialogpt"
        }
    ]
    
    # Try each model until one works
    for model in models:
        local_path = f"Models/{model['filename']}"
        
        # Skip if already exists
        if os.path.exists(local_path):
            file_size = os.path.getsize(local_path) / (1024 * 1024)
            print(f"✅ {model['name']} already exists! ({file_size:.1f} MB)")
            return local_path, model['name'], model['type']
        
        print(f"\n📥 Downloading: {model['name']}")
        print("This should work reliably...")
        
        try:
            response = requests.get(model['url'], stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded += len(chunk)
                        f.write(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            mb_downloaded = downloaded / (1024 * 1024)
                            print(f"📊 Progress: {percent:.1f}% ({mb_downloaded:.1f} MB)", end='\r')
            
            print("\n" + "✅" * 20)
            print(f"🎉 {model['name']} downloaded successfully!")
            return local_path, model['name'], model['type']
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    print("\n💡 Manual download option:")
    print("1. Go to: https://huggingface.co/microsoft/DialoGPT-small")
    print("2. Click 'Files and versions'")
    print("3. Download 'pytorch_model.bin'")
    print("4. Save to: Models/dialogpt-small.bin")
    return None, None, None

if __name__ == "__main__":
    model_path, model_name, model_type = download_model()
    if model_path:
        print(f"\n✨ Success! Using: {model_name}")
        print("Next: Update your app.py and run: python app.py")
    else:
        sys.exit(1)