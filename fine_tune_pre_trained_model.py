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
from typing import Tuple, List

from spacy.gold import GoldParse
from spacy.scorer import Scorer
from spacy.util import minibatch

from ner.model_factory import get_empty_model
from resources.config_provider import get_config_default
# reproducibility
from xml_extractions.extract_node_values import Offset

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


def spacy_evaluate(model, samples: List[Tuple[str, List[Offset]]]) -> None:
    """
    Compute entity global scores according to Spacy
    :param model: Spacy NER model
    :param samples: list of tuples containgin the filename, the text, and the offsets
    :return: a dict of scores
    """
    s = Scorer()

    for input_, offsets in samples:
        doc_gold_text = model.make_doc(input_)
        offset_tuples = convert_to_tuple(offsets)
        gold = GoldParse(doc_gold_text, entities=offset_tuples)
        pred_value = model(input_)
        s.score(pred_value, gold)

    entities = list(s.ents_per_type.items())
    entities.sort(key=lambda tup: tup[0])

    print(f"\n----\n"
          f"global scores  :\t\t"
          f"P: {s.scores['ents_p']:.2f}\t"
          f"R: {s.scores['ents_r']:.2f}\t"
          f"F1: {s.scores['ents_f']:.2f}")

    print("----\nscores per entities\n----")
    print('\n'.join([f"{ent_type + (15 - len(ent_type)) * ' '}:\t\t"
                     f"P: {measures['p']:.2f}\t"
                     f"R: {measures['r']:.2f}\t"
                     f"F1: {measures['f']:.2f}"
                     for ent_type, measures in entities]))
    print(f"-----\n")


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


def convert_to_tuple(offsets: List[Offset]) -> List[Tuple[int, int, str]]:
    return [offset.to_tuple() for offset in offsets]


config_training = get_config_default()
eval_dataset_path = config_training["eval_path"]

all_annotated_files: List[str] = os.listdir(eval_dataset_path)
# random.shuffle(file_paths)

ner_model = get_empty_model(load_labels_for_training=True)
ner_model = ner_model.from_disk(config_training["model_dir_path"])
# ner_model.begin_training()

# fixed dev set
dev_files = ['CA-montpellier-20150203-1306777-jurica.txt',
             'CA-versailles-20150205-1308492-jurica.txt',
             'CA-aix-en-provence-20150203-2015056-jurica.txt',
             'CA-paris-20150205-1420931-jurica.txt',
             'CA-aix-en-provence-20090506-088938-jurica.txt',
             'CA-chambery-20150205-1401394-jurica.txt',
             'CA-douai-20150205-1591-jurica.txt',
             'CA-versailles-20150205-1401403-jurica.txt',
             'CA-caen-20120626-102034-jurica.txt',
             'CA-aix-en-provence-20130214-1201797-jurica.txt',
             'CA-aix-en-provence-20150203-1419737-jurica.txt']

train_files = [file for file in all_annotated_files if file not in dev_files]

content_to_rate: List[Tuple[str, List[Offset]]] = load_content(train_files)
content_to_rate_test = load_content(dev_files)

print("total nb entities", sum([len(item) for item in content_to_rate]))

# compute_score_per_entity(model=ner_model, classes=entity_types, content=content_to_rate_test, print_errors=False)
spacy_evaluate(ner_model, content_to_rate_test)

train_data = [(current_line, GoldParse(ner_model.make_doc(current_line), entities=convert_to_tuple(gold_offsets)))
              for current_line, gold_offsets in content_to_rate]

for epoch in range(20):
    random.shuffle(train_data)
    losses = dict()
    batches = minibatch(train_data)
    for batch in batches:
        texts, manual_annotations = zip(*batch)
        ner_model.update(
            texts,
            manual_annotations,
            # drop=0.8,
            losses=losses)
    print(f"Epoch {epoch+1}\n")
    spacy_evaluate(ner_model, content_to_rate_test)
