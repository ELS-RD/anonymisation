# coding: utf8

# https://github.com/explosion/spacy/blob/master/examples/training/train_ner.py
# https://github.com/explosion/spaCy/issues/1530
# https://spacy.io/usage/linguistic-features#named-entities


import random
from pathlib import Path
import spacy
from spacy import util
from tqdm import tqdm

from resources.config_provider import get_config_default
from xml_parser.extract_node_value import get_paragraph_from_file

config_training = get_config_default()
xml_train_path = config_training["xml_train_path"]
model_dir_path = config_training["model_dir_path"]
n_iter = int(config_training["number_iterations"])
batch_size = int(config_training["batch_size"])


TRAIN_DATA = get_paragraph_from_file(xml_train_path,
                                     keep_paragraph_without_annotation=False)
# TRAIN_DATA = TRAIN_DATA[0:1000]
TRAIN_DATA = [(texts, annotations) for _, texts, _, annotations in TRAIN_DATA]

nlp = spacy.blank('fr')  # create blank Language class

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
