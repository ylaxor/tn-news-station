import streamlit as st

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import pipeline

class MeaningSim:

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ar-en")
        self.translator = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-ar-en")
        self.classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')

    def translate(self, ar, translator, tokenizer):
        batch = tokenizer([ar], return_tensors="pt")
        generated_ids = translator.generate(**batch, max_new_tokens=512)
        en = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return en

    def predict(self, ar_text, ar_labels):
        en_text = self.translate(ar_text, self.translator, self.tokenizer)
        en_labels = [self.translate(ar_label, self.translator, self.tokenizer) for ar_label in ar_labels]
        return self.classifier(en_text, en_labels)