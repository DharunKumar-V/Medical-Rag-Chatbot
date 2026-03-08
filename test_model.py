from transformers import AutoTokenizer, AutoModelForCausalLM

print("Downloading model...")

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

print("✅ Model downloaded successfully!")