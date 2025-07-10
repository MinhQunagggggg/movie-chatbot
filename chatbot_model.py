# chatbot_model.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "NlpHUST/gpt2-vietnamese"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id).eval()

def answer_via_model(q: str, max_len=100) -> str:
    inp = tokenizer.encode(q, return_tensors="pt")
    out = model.generate(inp, max_new_tokens=max_len, do_sample=True, top_p=0.9, temperature=0.7)
    return tokenizer.decode(out[0], skip_special_tokens=True)[len(q):].strip()
