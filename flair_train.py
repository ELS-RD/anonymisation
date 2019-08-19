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
from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import StackedEmbeddings, TokenEmbeddings, WordEmbeddings, FlairEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from spacy.gold import GoldParse
from spacy.lang.fr import French
from spacy.tokens.doc import Doc

from misc.command_line import train_parse_args
from misc.import_annotations import load_content, export_data_set_flair_format
from ner.model_factory import get_tokenizer
from xml_extractions.extract_node_values import Offset

# reproducibility
random.seed(1230)


def main(data_folder: str, model_folder: str, dev_size: float, nb_epochs: int) -> None:
    nlp = spacy.blank('fr')
    nlp.tokenizer = get_tokenizer(nlp)

    all_annotated_files: List[str] = [os.path.join(data_folder, filename)
                                      for filename in os.listdir(data_folder) if filename.endswith(".txt")]
    random.shuffle(all_annotated_files)

    nb_doc_dev_set: int = int(len(all_annotated_files) * dev_size)

    dev_file_names = all_annotated_files[0:nb_doc_dev_set]

    train_file_names = [file for file in all_annotated_files if file not in dev_file_names]

    train_path = export_data_set_flair_format(nlp, train_file_names)
    dev_path = export_data_set_flair_format(nlp, dev_file_names)

    corpus: Corpus = ColumnCorpus(data_folder="/tmp",
                                  column_format={0: 'text', 1: 'ner'},
                                  train_file=os.path.basename(train_path),
                                  dev_file=os.path.basename(dev_path),
                                  test_file=os.path.basename(dev_path))

    tag_dictionary = corpus.make_tag_dictionary(tag_type='ner')
    print(tag_dictionary.idx2item)

    embedding_types: List[TokenEmbeddings] = [
        WordEmbeddings('fr'),
        FlairEmbeddings('fr-forward'),
        FlairEmbeddings('fr-backward'),
    ]

    embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)

    tagger: SequenceTagger = SequenceTagger(hidden_size=256,
                                            embeddings=embeddings,
                                            tag_dictionary=tag_dictionary,
                                            tag_type='ner')

    trainer: ModelTrainer = ModelTrainer(tagger, corpus)

    trainer.train(model_folder,
                  max_epochs=nb_epochs,
                  embeddings_in_memory=False,
                  checkpoint=True)


if __name__ == '__main__':
    args = train_parse_args(train=True)
    main(data_folder=args.input_dir,
         model_folder=args.model_dir,
         dev_size=float(args.dev_size),
         nb_epochs=int(args.epoch))


# data_folder = "../case_annotation/data/tc/spacy_manual_annotations"
# model_folder = "resources/flair_ner/tc/"
# dev_size = 0.2

# data_folder = "../case_annotation/data/appeal_court/spacy_manual_annotations"
# model_folder = "resources/flair_ner/ca/"
# dev_size = 0.2
