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
from collections import namedtuple
from typing import Tuple, List, Dict

import numpy as np
from spacy.gold import GoldParse
from spacy.lang.fr import French
from spacy.scorer import Scorer
from spacy.util import minibatch, compounding
from tqdm import tqdm

from ner.model_factory import get_empty_model, entity_types
from resources.config_provider import get_config_default

Offset = namedtuple('Offset', ['start', 'end', 'type'])


def parse_offsets(text: str) -> Offset:
    """
    Convert to the right offset format
    :param text: original line
    :return: a tuple containing the offset
    """
    item = text.split(' ')
    return Offset(int(item[0]), int(item[1]), item[2])


def extract_offsets(text: str, offsets: List[Offset]) -> List[str]:
    """
    Extract a span from a line according to provided offsets
    :param text: original text
    :param offsets: list of tuples containing the positional information and a class of entity
    :return: a list of tokens
    """
    return [text[offset.start:offset.end] for offset in offsets]


def convert_offset_to_words(line: str, offsets: List[Offset], selected_type: str) -> List[str]:
    """
    Convert offsets to word tokens
    :param line: original string
    :param offsets: list of offsets
    :param selected_type: the offset type to keep for this extraction
    :return: a list of words
    """
    offset = [item for item in offsets if item.type == selected_type]
    tokens = extract_offsets(text=line, offsets=offset)
    words = [token.split(" ") for token in tokens]
    words = [word for sublist in words for word in sublist]
    return words


def spacy_evaluate(model, samples: List[Tuple[str, List[Offset]]]) -> Dict[str, float]:
    """
    Compute entity global scores according to Spacy
    :param model: Spacy NER model
    :param samples: list of tuples containgin the filename, the text, and the offsets
    :return: a dict of scores
    """
    scorer = Scorer()
    for input_, annot in samples:
        doc_gold_text = model.make_doc(input_)
        gold = GoldParse(doc_gold_text, entities=annot)
        pred_value = model(input_)
        scorer.score(pred_value, gold)
    return scorer.scores


def eval(model: French, classes: List[str], content: List[Tuple[str, List[Offset]]]):
    scores = {}
    with tqdm(total=len(content), unit=" samples", desc="compute score") as progress_bar:
        for current_line, gold_offsets in content:
            spacy_offsets: List[Offset] = [Offset(ent.start_char, ent.end_char, ent.label_) for ent in
                                           model(current_line).ents]
            for entity_type in classes:
                # predictions from Spacy
                pred_words = convert_offset_to_words(line=current_line,
                                                     offsets=spacy_offsets,
                                                     selected_type=entity_type)
                # manual annotations
                gold_words = convert_offset_to_words(line=current_line,
                                                     offsets=gold_offsets,
                                                     selected_type=entity_type)
                if len(gold_words) > 0:
                    score = len(set(gold_words).intersection(set(pred_words))) / len(set(gold_words))
                    current_scores: List[float] = scores.get(entity_type, [])
                    current_scores.append(score)
                    scores[entity_type] = current_scores
                    # if score != 1:
                    #     print(token_type, ":", pred_tokens, "VS", gold_tokens)
                progress_bar.update()

    for entity_type in classes:
        if (entity_type in scores) and (len(scores[entity_type]) > 0):
            print(entity_type, np.round(100 * np.mean(scores[entity_type]), 2), "%\tnb samples",
                  len(scores[entity_type]))


config_training = get_config_default()
eval_dataset_path = config_training["eval_path"]
ner_model = get_empty_model(load_labels_for_training=False)
ner_model = ner_model.from_disk(config_training["model_dir_path"])

content_to_rate: List[Tuple[str, List[Offset]]] = []

for file_path in os.listdir(eval_dataset_path):
    file_path = os.path.join(eval_dataset_path, file_path)
    if file_path.endswith('.txt'):
        with open(file_path, 'r') as f:
            content_case = [item.strip() for item in f.readlines()]
        path_annotations = file_path.replace('.txt', '.ent')
        with open(path_annotations, 'r') as f:
            annotations = [item.strip() for item in f.readlines()]

        assert len(content_case) > 0
        assert len(content_case) == len(annotations)

        for line_case, line_annotations in zip(content_case, annotations):
            gold_offsets = [parse_offsets(item) for item in line_annotations.split(',') if item != ""]
            if len(gold_offsets) > 0:
                content_to_rate.append((line_case, gold_offsets))

eval(model=ner_model, classes=entity_types, content=content_to_rate)

# results = spacy_evaluate(ner_model, content_to_rate)
# print(results)

print("nb entities", sum([len(item) for item in content_to_rate]))


all_data = [(current_line, GoldParse(ner_model.make_doc(current_line), entities=gold_offsets)) for current_line, gold_offsets in content_to_rate]
train_data = all_data[:1800]


with tqdm(total=15, unit=" epoch", desc="update model") as progress_bar:
    for itn in range(15):
        random.shuffle(train_data)
        losses = dict()
        batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            texts, annotations = zip(*batch)
            ner_model.update(
                texts,
                annotations,
                drop=0.5,
                losses=losses
            )
        progress_bar.update()

eval(model=ner_model, classes=entity_types, content=content_to_rate[1800:])
