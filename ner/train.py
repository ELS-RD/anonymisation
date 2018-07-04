# coding: utf8

# https://github.com/explosion/spacy/blob/master/examples/training/train_ner.py
# https://github.com/explosion/spaCy/issues/1530
# https://spacy.io/usage/linguistic-features#named-entities


import random
from pathlib import Path
import spacy
from spacy import util
from tqdm import tqdm
from xml_parser.xml_parser import get_paragraph
import configparser

config = configparser.ConfigParser()
config.read('resources/config.ini')
config_training = config['training']
xml_train_path = config_training["xml_train_path"]
xml_test_path = config_training["xml_test_path"]
model_dir_path = config_training["model_dir_path"]
n_iter = int(config_training["number_iterations"])
batch_size = int(config_training["batch_size"])


TRAIN_DATA = get_paragraph(xml_train_path, spacy_format=True)
# TRAIN_DATA = TRAIN_DATA[0:1000]
TEST_DATA = get_paragraph(xml_test_path, spacy_format=True)

nlp = spacy.blank('fr')  # create blank Language class
print("Created blank 'fr' model")

# create the built-in pipeline components and add them to the pipeline
# nlp.create_pipe works for built-ins that are registered with spaCy

ner = nlp.create_pipe('ner')
nlp.add_pipe(ner, last=True)

# add labels
for token_type in ["Adresse", "Personne"]:
    ner.add_label(token_type)


optimizer = nlp.begin_training()
with tqdm(total=n_iter * len(TRAIN_DATA) / batch_size) as pbar:
    for itn in range(n_iter):
        print("\nIter", itn + 1)
        losses = {}
        random.shuffle(TRAIN_DATA)
        batches = util.minibatch(TRAIN_DATA, batch_size)

        for current_batch_item in batches:
            texts, annotations = zip(*current_batch_item)
            nlp.update(
                texts,  # batch of texts
                annotations,  # batch of annotations
                drop=0.5,  # dropout - make it harder to memorise resources
                sgd=optimizer,  # callable to update weights
                losses=losses)
            pbar.update(1)

        print(losses)

# save model to output directory
if model_dir_path is not None:
    model_dir_path = Path(model_dir_path)
    nlp.to_disk(model_dir_path)
    print("Saved model to", model_dir_path)

    # test the saved model
    print("Loading from", model_dir_path)
    nlp2 = spacy.load(model_dir_path)

# test the trained model
for texts, _ in TEST_DATA:
    doc = nlp(texts)
    print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
    print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])
