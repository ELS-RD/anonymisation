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
from typing import Tuple, List, Dict

import numpy as np
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from tqdm import tqdm

from match_text_unsafe.build_entity_dictionary import EntityTypename
from ner.model_factory import get_empty_model, token_types
from resources.config_provider import get_config_default


def convert_offsets(text: str) -> Tuple[int, int, str]:
    """
    Convert to the right offset format
    :param text: original line
    :return: a tuple containing the offset
    """
    item = text.split(' ')
    return int(item[0]), int(item[1]), item[2]


def extract_offsets(text: str, offsets: List[Tuple[int, int, str]]) -> List[str]:
    """
    Extract a span from a line according to provided offsets
    :param text: original text
    :param offsets: list of tuples containing the positional information and a class of entity
    :return: a list of tokens
    """
    return [text[offset[0]: offset[1]] for offset in offsets]


config_training = get_config_default()
model_dir_path = config_training["model_dir_path"]
eval_dataset_path = config_training["eval_path"]
ner_model = get_empty_model(load_labels_for_training=False)
ner_model = ner_model.from_disk(model_dir_path)

content_to_rate: List[Tuple[str,  str, List[Tuple[int, int, str]]]] = []

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
            line_annotations_parsed = [convert_offsets(item) for item in line_annotations.split(',') if item != ""]
            if len(line_annotations_parsed) > 0:
                content_to_rate.append((file_path, line_case, line_annotations_parsed))

entity_typename_builder = EntityTypename()

scores = {}
for token_type in token_types:
    scores[token_type] = []

with tqdm(total=len(content_to_rate), unit=" samples", desc="compute score") as progress_bar:
    for file_path, line, gold_offsets in content_to_rate:
        predictions = ner_model(line)
        pred_offset: List[Tuple[int, int, str]] = [(ent.start_char, ent.end_char, ent.label_) for ent in predictions.ents]
        for token_type in token_types:
            selected_pred_offset = [item for item in pred_offset if item[2] == token_type]
            selected_pred_tokens = extract_offsets(text=line, offsets=selected_pred_offset)
            selected_pred_words = [token.split(" ") for token in selected_pred_tokens]
            selected_pred_words = [val for sublist in selected_pred_words for val in sublist]
            selected_gold_offset = [item for item in gold_offsets if item[2] == token_type]
            selected_gold_tokens = extract_offsets(text=line, offsets=selected_gold_offset)
            selected_gold_words = [token.split(" ") for token in selected_gold_tokens]
            selected_gold_words = [val for sublist in selected_gold_words for val in sublist]
            if len(selected_gold_offset) > 0:
                score = len(set(selected_gold_words).intersection(set(selected_pred_words))) / len(set(selected_gold_words))
                scores[token_type].append(score)
                # if score != 1:
                #     print(token_type, ":", selected_pred_tokens, "VS", selected_gold_tokens)
            progress_bar.update()


for token_type in token_types:
    if len(scores[token_type]) > 0:
        print(token_type, np.round(100 * np.mean(scores[token_type]), 2), "%\tnb samples", len(scores[token_type]))


def evaluate(model, samples: List[Tuple[str, str, List[Tuple[int, int, str]]]]) -> Dict[str, float]:
    """
    Compute entity global scores according to Spacy
    :param model: Spacy NER model
    :param samples: list of tuples containgin the filename, the text, and the offsets
    :return: a dict of scores
    """
    scorer = Scorer()
    for _, input_, annot in samples:
        doc_gold_text = model.make_doc(input_)
        gold = GoldParse(doc_gold_text, entities=annot)
        pred_value = model(input_)
        scorer.score(pred_value, gold)
    return scorer.scores


results = evaluate(ner_model, content_to_rate)
print(results)

print("nb entities", sum([len(item) for item in content_to_rate]))
