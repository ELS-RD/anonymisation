import string
from typing import Dict

import spacy
import streamlit as st
from flair.data import Sentence
from flair.models import SequenceTagger
from flair.tokenization import SpacyTokenizer
from flair.visual.ner_html import render_ner_html
from spacy.lang.fr import French
from spacy.tokenizer import Tokenizer
from streamlit import cache


# embed the custom tokenizer function to have webapp as an autonomous file
def get_tokenizer(model: French) -> Tokenizer:
    split_char = r"[ ,\\.()-/\\|:;\"+=!?_+#“’'‘]"
    extended_infix = [r'[:\\(\\)-\./#"“’\'—‘'] + model.Defaults.infixes
    infix_re = spacy.util.compile_infix_regex(extended_infix)
    prefix_re = spacy.util.compile_prefix_regex(tuple(list(model.Defaults.prefixes) + [split_char]))
    suffix_re = spacy.util.compile_suffix_regex(tuple(list(model.Defaults.suffixes) + [split_char]))

    tok = Tokenizer(
        model.vocab,
        prefix_search=prefix_re.search,
        suffix_search=suffix_re.search,
        infix_finditer=infix_re.finditer,
        token_match=None,
    )
    return tok


@cache(allow_output_mutation=True, max_entries=1)
def get_model():
    return SequenceTagger.load("resources/flair_ner/luxano_segment_0/best-model.pt")


@cache(allow_output_mutation=True, max_entries=1)
def get_french_tokenizer():
    nlp = spacy.blank(name="fr")
    nlp.tokenizer = get_tokenizer(model=nlp)
    return SpacyTokenizer(nlp)


st.beta_set_page_config(
    page_title="Anonymisation", page_icon="🔍", layout="centered", initial_sidebar_state="collapsed",
)

"""
# Reconnaissance des entités nommées en vue d'une anonymisation automatisée

Modèle [Flair](https://github.com/flairNLP/flair) entraîné sur 342 décisions Luxembourgeoises annotées manuellement.

Ressources:
* [code du projet anonymisation](https://github.com/ELS-RD/anonymisation)
* [code du projet récupération tagtog / transformations](https://github.com/ELS-RD/lux-ano)
"""

st.image(image="http://svowebmaster.free.fr/images_site_svo/armoiries/armoiries_LUXEMBOURG.gif", width=150)

user_input = st.text_area("coller une décision ci-dessous", "", max_chars=100000, height=300)

replace_names = st.checkbox(label="Remplacer les entités nommées par des pseudos", value=False)

if user_input:
    "## Résultat"

paragraphs = list()
tagger = get_model()
tokenizer = get_french_tokenizer()
for paragraph in user_input.split("\n"):
    if paragraph.strip() == "":
        continue
    sentence = Sentence(paragraph, use_tokenizer=tokenizer)
    tagger.predict(sentence)
    paragraphs.append(sentence)

if replace_names:
    pseudo = list(string.ascii_uppercase) + [a + b for a in string.ascii_uppercase for b in string.ascii_uppercase]
    replacement_dict: Dict[str, str] = dict()
    for sentence in paragraphs:
        for word in sentence:
            if word.get_tag("ner").value != "O" and word.text not in string.punctuation:
                if word.text not in replacement_dict:
                    replacement_dict[word.text] = pseudo[len(replacement_dict)]
                word.text = replacement_dict[word.text]


colors = {
    "ETABLISSEMENT": "#35c2b2",
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
