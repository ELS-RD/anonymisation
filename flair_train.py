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
import random
from typing import List, Optional

import spacy
from flair.data import Corpus
from flair.embeddings import StackedEmbeddings, TokenEmbeddings, WordEmbeddings, FlairEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer

from misc.command_line import train_parse_args
from misc.import_annotations import prepare_flair_train_dev_corpus
from ner.model_factory import get_tokenizer

# reproducibility
random.seed(5)


def main(data_folder: str, model_folder: str, dev_size: float, nb_epochs: int,
         nb_segment: Optional[int], segment: Optional[int]) -> None:
    nlp = spacy.blank(name='fr')
    nlp.tokenizer = get_tokenizer(nlp)

    corpus: Corpus = prepare_flair_train_dev_corpus(spacy_model=nlp, data_folder=data_folder, dev_size=dev_size,
                                                    nb_segment=nb_segment, segment=segment)
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
                                            use_crf=True,
                                            tag_dictionary=tag_dictionary,
                                            tag_type='ner')

    trainer: ModelTrainer = ModelTrainer(model=tagger, corpus=corpus, use_tensorboard=True)

    trainer.train(model_folder,
                  max_epochs=nb_epochs,
                  mini_batch_size=32,
                  embeddings_storage_mode="cpu",
                  checkpoint=False,
                  )


if __name__ == '__main__':
    args = train_parse_args(train=True)
    main(data_folder=args.input_dir,
         model_folder=args.model_dir,
         dev_size=args.dev_size,
         nb_epochs=args.epoch,
         nb_segment=args.nb_segment,
         segment=args.segment)
