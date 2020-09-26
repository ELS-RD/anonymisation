import streamlit as st
from flair.data import Sentence
from flair.models import SequenceTagger
from flair.visual.ner_html import render_ner_html
from streamlit import cache


@cache(allow_output_mutation=True)
def get_model():
    return SequenceTagger.load('resources/flair_ner/luxano_segment_0/best-model.pt')


st.beta_set_page_config(
    page_title="Anonymisation",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

"""
# Reconnaissance des entités nommées en vue d'une anonymisation automatisée

Modèle [Flair](https://github.com/flairNLP/flair) entraîné sur 342 décisions Luxembourgeoises annotées manuellement.  

Ressources:
* [code du projet anonymisation](https://github.com/ELS-RD/anonymisation)
* [code du projet récupération tagtog / transformations](https://github.com/ELS-RD/lux-ano)
"""

st.image(image="http://svowebmaster.free.fr/images_site_svo/armoiries/armoiries_LUXEMBOURG.gif", width=150)

user_input = st.text_area(
    "coller une décision ci-dessous", "", max_chars=20000, height=300
)

"## Résultat"

paragraphs = list()
tagger = get_model()
for paragraph in user_input.split("\n"):
    if paragraph.strip() == "":
        continue
    sentence = Sentence(paragraph)
    tagger.predict(sentence)
    paragraphs.append(sentence)

colors = {"ETABLISSEMENT": "#35c2b2",
          "ADDRESS": "#FFAE62",
          "ORGANIZATION": "#FFB990",
          "SITE": "#ff8800",
          "HOPITAL": "#edddcb",
          "MEDIA": "#e966c4",
          "MAIL": "#1688cb",
          "ETAT": "#00c5ed",
          "RESIDENCE": "#94bce1",
          "PERSONNE_DE_JUSTICE": "#89B2C4",
          "GROUPE": "#9cae64",
          "DATE": "#F9E17D",
          "NUMEROS": "#F8485E",
          "PERS": "#FA7268",
          "FONDS": "#C3FF1F",
          }

st.write(render_ner_html(sentences=paragraphs, colors=colors, wrap_page=False), unsafe_allow_html=True)
