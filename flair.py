#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.
import os
import random
import tempfile
from typing import List, Tuple

import spacy
from flair.embeddings import StackedEmbeddings, TokenEmbeddings, WordEmbeddings, FlairEmbeddings, CharacterEmbeddings
from spacy.gold import GoldParse
from spacy.lang.fr import French
from spacy.tokens import Span
from spacy.tokens.doc import Doc

from misc.import_annotations import load_content
from ner.model_factory import get_tokenizer
from xml_extractions.extract_node_values import Offset
from flair.data import Corpus, Sentence
from flair.datasets import ColumnCorpus
from flair.trainers import ModelTrainer
from flair.visual.training_curves import Plotter
from flair.models import SequenceTagger

# reproducibility
random.seed(123)


def convert_to_flair_format(model: French, data: List[Tuple[str, List[Offset]]]) -> List[str]:
    result: List[str] = list()
    for text, offsets in data:
        doc: Doc = model(text)
        offset_tuples = [offset.to_tuple() for offset in offsets]
        gold_annotations = GoldParse(doc, entities=offset_tuples)
        annotations: List[str] = gold_annotations.ner
        assert len(annotations) == len(doc)
        # Flair uses BIOES and Spacy BILUO
        # BILUO for Begin, Inside, Last, Unit, Out
        # BIOES for Begin, Inside, Outside, End, Single
        annotations = [a.replace('L-', 'E-') for a in annotations]
        annotations = [a.replace('U-', 'S-') for a in annotations]
        result += [f"{word} {tag}\n" for word, tag in zip(doc, annotations)]
        result.append('\n')
    return result


def export_data_set(model: French, data_file_names: List[str]) -> str:
    data = load_content(txt_paths=data_file_names)
    data_flair_format = convert_to_flair_format(model, data)
    f = tempfile.NamedTemporaryFile(delete=False, mode="w")
    tmp_path = f.name
    f.writelines(data_flair_format)
    f.close()
    return tmp_path


dev_size = 0.2
data_folder = "../case_annotation/data/appeal_court/spacy_manual_annotations"

nlp = spacy.blank('fr')
nlp.tokenizer = get_tokenizer(nlp)

all_annotated_files: List[str] = [os.path.join(data_folder, filename)
                                  for filename in os.listdir(data_folder) if filename.endswith(".txt")]
random.shuffle(all_annotated_files)

nb_doc_dev_set: int = int(len(all_annotated_files) * dev_size)

dev_file_names = all_annotated_files[0:nb_doc_dev_set]

train_file_names = [file for file in all_annotated_files if file not in dev_file_names]

train_path = export_data_set(nlp, train_file_names)
dev_path = export_data_set(nlp, dev_file_names)

# init a corpus using column format, data folder and the names of the train, dev and test files
corpus: Corpus = ColumnCorpus(data_folder="/tmp",
                              column_format={0: 'text', 1: 'ner'},
                              train_file=os.path.basename(train_path),
                              test_file=os.path.basename(dev_path),
                              dev_file=os.path.basename(dev_path))

print(corpus.train[0].to_tagged_string('ner'))

tag_dictionary = corpus.make_tag_dictionary(tag_type='ner')
print(tag_dictionary.idx2item)

# 4. initialize embeddings
embedding_types: List[TokenEmbeddings] = [
    WordEmbeddings('fr'),
    CharacterEmbeddings(),
    FlairEmbeddings('fr-forward'),
    FlairEmbeddings('fr-backward'),
]

embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)

tagger: SequenceTagger = SequenceTagger(hidden_size=256,
                                        embeddings=embeddings,
                                        tag_dictionary=tag_dictionary,
                                        tag_type='ner',
                                        use_crf=True)

trainer: ModelTrainer = ModelTrainer(tagger, corpus)

trainer.train('resources/taggers/example-ner',
              learning_rate=0.1,
              mini_batch_size=100,
              checkpoint=True,
              patience=10,
              max_epochs=100)


plotter = Plotter()
plotter.plot_training_curves('resources/taggers/example-ner/loss.tsv')
plotter.plot_weights('resources/taggers/example-ner/weights.txt')


tagger = SequenceTagger.load('resources/taggers/example-ner/final-model.pt')

sentence = Sentence("Le préposé Michael Benesty est en train de jeuner .")
tagger.predict(sentence)

doc = nlp(sentence.to_original_text())

for span in sentence.get_spans('ner'):
    idx = [token.idx for token in span.tokens]
    span = Span(doc, idx[0]-1, idx[-1], label='PERS')  # Create a span in Spacy
    doc.ents = list(doc.ents) + [span]  # add span to doc.ents

