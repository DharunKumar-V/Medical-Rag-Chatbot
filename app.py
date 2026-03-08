# =========================================================
# 🩺 Medical RAG Chatbot (CLEAN HUMAN RESPONSE VERSION)
# =========================================================

from flask import Flask, render_template, request
import chromadb
import torch
import os
import re
import time
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForCausalLM


# =========================================================
# ⚡ SETTINGS
# =========================================================
torch.set_num_threads(4)
os.environ["ANONYMIZED_TELEMETRY"] = "False"

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "medical-chatbot"

TOP_K = 3
MAX_CONTEXT_CHARS = 800

app = Flask(__name__)


# =========================================================
# 🗄️ LOAD DB
# =========================================================
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(COLLECTION_NAME)


# =========================================================
# 🤖 LOAD MODEL
# =========================================================
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.eval()


# =========================================================
# 🔍 RETRIEVE
# =========================================================
def find_relevant_chunks(query: str):
    results = collection.query(
        query_texts=[query],
        n_results=TOP_K,
        include=["documents"]
    )

    return results["documents"][0] if results["documents"] else []


# =========================================================
# 🧹 CLEAN BOOK TEXT (IMPORTANT)
# =========================================================
def clean_chunks(chunks):

    cleaned = []

    for chunk in chunks:

        # join broken OCR words: symp- toms → symptoms
        chunk = re.sub(r'-\s+', '', chunk)

        # remove weird symbols
        chunk = re.sub(r'[^a-zA-Z0-9.,;:()/%\s-]', ' ', chunk)

        # normalize spaces
        chunk = re.sub(r'\s+', ' ', chunk).strip()

        if len(chunk.split()) > 25:
            cleaned.append(chunk)

    return cleaned[:3]


# =========================================================
# ✨ CLEAN MODEL OUTPUT
# =========================================================
def clean_answer(text):

    # remove prompt leakage
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'Context:.*', '', text, flags=re.I)
    text = re.sub(r'Question:.*', '', text, flags=re.I)

    text = text.strip()

    # keep only first paragraph (prevents rambling)
    text = text.split("\n")[0]

    return text


# =========================================================
# 🤖 GENERATE (NO [INST] !!!)
# =========================================================
def generate_with_model(question, chunks):

    context = "\n".join(clean_chunks(chunks))[:MAX_CONTEXT_CHARS]

    prompt = f"""
You are a helpful and professional medical assistant.

Using the medical information below, answer the question in simple, clear, human-friendly language.

Medical Information:
{context}

Answer:
"""

    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=80,
            do_sample=False,
            temperature=0.0,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id
        )

    raw = tokenizer.decode(outputs[0], skip_special_tokens=True)

    answer = raw.replace(prompt, "")
    answer = clean_answer(answer)

    return answer + "\n\nNote: Please consult a healthcare professional."


# =========================================================
# ⚡ CACHE
# =========================================================
@lru_cache(maxsize=128)
def answer_query(question: str):

    chunks = find_relevant_chunks(question)

    if not chunks:
        return "No relevant medical information found."

    return generate_with_model(question, chunks)


# =========================================================
# 🌐 ROUTES
# =========================================================
@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/get", methods=["POST"])
def chat():

    user_input = request.form["msg"].strip()

    if not user_input:
        return "Please enter a question."

    return answer_query(user_input)


# =========================================================
# 🚀 RUN
# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)