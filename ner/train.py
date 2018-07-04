# coding: utf8

# https://github.com/explosion/spacy/blob/master/examples/training/train_ner.py
# https://github.com/explosion/spaCy/issues/1530
# https://spacy.io/usage/linguistic-features#named-entities


import random
from pathlib import Path
import spacy
from spacy import util
from spacy.util import compounding

from xml_parser.xml_parser import get_paragraph_text, read_xml

batch_size = 50

xml_path = "./resources/training_data/CA-2013-sem-06.xml"
tree = read_xml(xml_path)
r = tree.xpath('//TexteJuri/P')

TRAIN_DATA = list()
for i in r:
    paragraph_text, extracted_text, offset = get_paragraph_text(i)
    if len(extracted_text) > 0:
        item_text = extracted_text[0]
        current_attribute = offset.get('entities')[0]
        start = current_attribute[0]
        end = current_attribute[1]
        assert item_text == paragraph_text[start:end]
        TRAIN_DATA.append((paragraph_text, offset))


def get_batches(train_data, model_type):
    max_batch_sizes = {'tagger': 32, 'parser': 16, 'ner': 16, 'textcat': 64}
    max_batch_size = max_batch_sizes[model_type]
    if len(train_data) < 1000:
        max_batch_size /= 2
    if len(train_data) < 500:
        max_batch_size /= 2
    batch_size = compounding(1, max_batch_size, 1.001)
    batches = util.minibatch(train_data, size=batch_size)
    return batches


batches = util.minibatch(TRAIN_DATA, size=batch_size)

n_iter = 10
output_dir = None

nlp = spacy.blank('fr')  # create blank Language class
print("Created blank 'fr' model")

# create the built-in pipeline components and add them to the pipeline
# nlp.create_pipe works for built-ins that are registered with spaCy

ner = nlp.create_pipe('ner')
nlp.add_pipe(ner, last=True)

# add labels
for _, annotations in TRAIN_DATA:
    for ent in annotations.get('entities'):
        ner.add_label(ent[2])

# get names of other pipes to disable them during training
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
with nlp.disable_pipes(*other_pipes):  # only train NER
    optimizer = nlp.begin_training()
    for itn in range(n_iter):
        # random.shuffle(TRAIN_DATA)
        losses = {}
        batch_count = 0
        for current_batch_item in batches:
            text, annotations = zip(*current_batch_item)
            nlp.update(
                text,  # batch of texts
                annotations,  # batch of annotations
                drop=0.5,  # dropout - make it harder to memorise resources
                sgd=optimizer,  # callable to update weights
                losses=losses)
            print("batch ", batch_count, "/", len(TRAIN_DATA) / batch_size)
            batch_count += 1
        print(losses)

# test the trained model
for text, _ in TRAIN_DATA:
    doc = nlp(text)
    print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
    print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])

# save model to output directory
if output_dir is not None:
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir()
    nlp.to_disk(output_dir)
    print("Saved model to", output_dir)

    # test the saved model
    print("Loading from", output_dir)
    nlp2 = spacy.load(output_dir)
    for text, _ in TRAIN_DATA:
        doc = nlp2(text)
        print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
        print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])

# Expected output:
# Entities [('Shaka Khan', 'PERSON')]
# Tokens [('Who', '', 2), ('is', '', 2), ('Shaka', 'PERSON', 3),
# ('Khan', 'PERSON', 1), ('?', '', 2)]
# Entities [('London', 'LOC'), ('Berlin', 'LOC')]
# Tokens [('I', '', 2), ('like', '', 2), ('London', 'LOC', 3),
# ('and', '', 2), ('Berlin', 'LOC', 3), ('.', '', 2)]
