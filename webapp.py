import streamlit as st
from flair.data import Sentence
from flair.models import SequenceTagger
from flair.visual.ner_html import render_ner_html
from streamlit import cache
from streamlit.components.v1 import html


@cache(allow_output_mutation=True)
def get_model():
    return SequenceTagger.load('resources/flair_ner/luxano_segment_0/best-model.pt')

"""
# Anonymisation des décisions du parquet Luxembourgeois

Testez l'anonymisation par Machine learning. 
"""

user_input = st.text_area(
    "coller une décision", "", max_chars=10000, height=500
)

paragraphs = list()
tagger = get_model()
for paragraph in user_input.split("\n"):
    sentence = Sentence(paragraph)
    tagger.predict(sentence)
    paragraphs.append(sentence)

html(render_ner_html(sentences=paragraphs), height=2000)
