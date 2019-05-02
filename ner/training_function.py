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
from math import ceil
from pathlib import Path

from spacy import util
from tqdm import tqdm

from misc.convert_to_bilou import convert_unknown_bilou_bulk
from ner.model_factory import get_empty_model


def train_model(data: list, folder_to_save_model: str, n_iter: int, batch_size: int, dropout_rate: float):
    """
    Train a NER model using Spacy
    :param data: list of tuples [(text, offset)]
    :param folder_to_save_model: Where to save the learned model. None to skip. Will be overiden with new model
    :param n_iter: number iterations of the CNN
    :param batch_size: more = less precise / less time to learn
    :param dropout_rate: more : learn less / better generalization
    """
    nlp = get_empty_model(load_labels_for_training=True)
    nlp.vocab.vectors.name = 'spacy_pretrained_vectors'
    optimizer = nlp.begin_training()
    with tqdm(total=n_iter * ceil(len(data) / batch_size), unit=" paragraphs", desc="Learn NER model") as pbar:
        for itn in range(n_iter):
            pbar.set_description(f"Learn NER model - iteration {itn + 1}")
            losses = {}
            random.shuffle(data)
            batches = util.minibatch(data, batch_size)

            for current_batch_item in batches:
                case_id, texts, annotations = zip(*current_batch_item)
                docs = [nlp.make_doc(text) for text in texts]
                gold_with_unknown_bilou = convert_unknown_bilou_bulk(docs=docs, offsets=annotations)
                nlp.update(
                    docs,  # batch of texts
                    gold_with_unknown_bilou,  # batch of annotations
                    drop=dropout_rate,  # dropout - make it harder to memorise rules
                    sgd=optimizer,  # callable to update weights
                    losses=losses)
                pbar.postfix = "loss: " + str(losses['ner'])
                pbar.update()

    # save model to output directory
    if folder_to_save_model is not None:
        folder_to_save_model = Path(folder_to_save_model)
        nlp.to_disk(folder_to_save_model)
