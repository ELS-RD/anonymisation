from annotated_text import annotated_text
from flair.data import Sentence
from flair.models import SequenceTagger

sentence = Sentence('I love Berlin .')
tagger = SequenceTagger.load('ner')

tagger.predict(sentence)
line = list()
for word in sentence:
    tag = word.get_tag('ner').value
    if tag != 'O':
        line.append((word.text, tag, "#8ef"))
    else:
        line.append(word.text)
    if word.whitespace_after:
        line.append(" ")

annotated_text(*line)
