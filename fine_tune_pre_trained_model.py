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
from spacy.util import minibatch

from ner.model_factory import get_empty_model, entity_types
from resources.config_provider import get_config_default

Offset = namedtuple('Offset', ['start', 'end', 'type'])

# reproducibility
random.seed(123)


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


def compute_score_per_entity(model: French, classes: List[str], content: List[Tuple[str, List[Offset]]],
                             print_errors: bool):
    entity_scores = {}

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
                current_scores: List[float] = entity_scores.get(entity_type, [])
                current_scores.append(score)
                entity_scores[entity_type] = current_scores
                if (score != 1) and print_errors:
                    print(entity_type, ": gold: ", gold_words, "pred:", set(pred_words),
                          "-|- diff", set(gold_words).difference(set(pred_words)))

    for entity_type in classes:
        if (entity_type in entity_scores) and (len(entity_scores[entity_type]) > 0):
            print(entity_type, np.round(100 * np.mean(entity_scores[entity_type]), 2), "%\tnb samples",
                  len(entity_scores[entity_type]))


def load_content(paths) -> List[Tuple[str, List[Offset]]]:
    results: List[Tuple[str, List[Offset]]] = []
    file_used = []
    for file_path in paths:
        file_path = os.path.join(eval_dataset_path, file_path)
        if file_path.endswith('.txt'):
            file_used.append(file_path)
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
                    results.append((line_case, gold_offsets))
    print("nb files", len(file_used))
    print("files", file_used)
    return results


config_training = get_config_default()
eval_dataset_path = config_training["eval_path"]

file_paths: List[str] = os.listdir(eval_dataset_path)
random.shuffle(file_paths)

ner_model = get_empty_model(load_labels_for_training=True)
ner_model = ner_model.from_disk(config_training["model_dir_path"])
# ner_model.begin_training()

content_to_rate: List[Tuple[str, List[Offset]]] = load_content(file_paths[:80])
content_to_rate_test = load_content(file_paths[80:])

print("total nb entities", sum([len(item) for item in content_to_rate]))

compute_score_per_entity(model=ner_model, classes=entity_types, content=content_to_rate_test, print_errors=False)
scores = spacy_evaluate(ner_model, content_to_rate_test)
print(f"Spacy scores: P: {scores['ents_p']}, R: {scores['ents_r']}, F: {scores['ents_f']}")

train_data = [(current_line, GoldParse(ner_model.make_doc(current_line), entities=gold_offsets))
              for current_line, gold_offsets in content_to_rate]

for epoch in range(10):
    random.shuffle(train_data)
    losses = dict()
    batches = minibatch(train_data)
    for batch in batches:
        texts, manual_annotations = zip(*batch)
        ner_model.update(
            texts,
            manual_annotations,
            drop=0.5,
            losses=losses)
    scores = spacy_evaluate(ner_model, content_to_rate_test)
    print(f"Training - round {epoch}, P: {scores['ents_p']}, R: {scores['ents_r']}, F: {scores['ents_f']}")


compute_score_per_entity(model=ner_model, classes=entity_types, content=content_to_rate_test, print_errors=True)
