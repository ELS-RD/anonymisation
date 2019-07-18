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
from argparse import Namespace, ArgumentParser
from typing import Tuple, List

from spacy.gold import GoldParse
from spacy.scorer import Scorer
from spacy.tokens.doc import Doc
from spacy.util import minibatch, compounding
from thinc.neural.ops import NumpyOps
from thinc.neural.optimizers import Optimizer, Adam

from ner.model_factory import get_empty_model
from xml_extractions.extract_node_values import Offset

# reproducibility
random.seed(123)


def parse_args() -> Namespace:
    """
    Parse command line arguments.

    :returns: a namespace with all the set parameters
    """

    parser = ArgumentParser(
        description='Annotate a sample of the given files in the input directory'
    )
    parser.add_argument(
        '-m', '--model-dir',
        help="Model directory",
        action="store", dest="model_dir",
        required=True
    )
    parser.add_argument(
        '-i', '--input-files-dir',
        help="Input files directory",
        action="store", dest="input_dir",
        required=True
    )
    parser.add_argument(
        '-s', '--dev-set-size',
        help="Percentage of random docs to put in dev set",
        action="store", dest="dev_size",
        required=True
    )
    parser.add_argument(
        '-e', '--epochs',
        help="Number of epochs",
        action="store", dest="epoch",
        required=True
    )

    return parser.parse_args()


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


def spacy_evaluate(model, dev: List[Tuple[str, List[Offset]]]) -> None:
    """
    Compute entity global scores according to Spacy
    :param model: Spacy NER model
    :param dev: list of tuples containgin the filename, the text, and the offsets
    :return: a dict of scores
    """
    s = Scorer()

    for text, offsets in dev:
        doc_gold_text = model.make_doc(text)
        offset_tuples = convert_to_tuple(offsets)
        gold = GoldParse(doc_gold_text, entities=offset_tuples)
        pred_value: Doc = model(text)
        # print(pred_value.text, pred_value.ents)
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


def load_content(paths: List[str], dataset_path: str) -> List[Tuple[str, List[Offset]]]:
    results: List[Tuple[str, List[Offset]]] = list()
    file_used: List[str] = list()
    for file_path in paths:
        file_path = os.path.join(dataset_path, file_path)
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
    # print("nb files", len(file_used))
    # print("files", file_used)
    return results


def convert_to_tuple(offsets: List[Offset]) -> List[Tuple[int, int, str]]:
    """
    Convert List of offsets to the Tupple format (may be useful as input to Spacy)
    """
    return [offset.to_tuple() for offset in offsets]


def main(data_folder: str, model_path: str, dev_size: float, nb_epochs: int) -> None:

    ner_model = get_empty_model(load_labels_for_training=True)
    ner_model = ner_model.from_disk(path=model_path)  # config_training["model_dir_path"]

    all_annotated_files: List[str] = [filename for filename in os.listdir(data_folder) if filename.endswith(".txt")]
    random.shuffle(all_annotated_files)

    # ner_model.begin_training()

    nb_doc_dev_set: int = int(len(all_annotated_files) * dev_size)

    dev_file_names = all_annotated_files[0:nb_doc_dev_set]

    train_file_names = [file for file in all_annotated_files if file not in dev_file_names]

    content_to_rate: List[Tuple[str, List[Offset]]] = load_content(paths=train_file_names,
                                                                   dataset_path=data_folder)
    content_to_rate_test = load_content(paths=dev_file_names,
                                        dataset_path=data_folder)

    print("total nb entities", sum([len(item) for item in content_to_rate]))

    # spacy_evaluate(ner_model, content_to_rate_test)

    train_data = [(current_line, GoldParse(ner_model.make_doc(current_line), entities=convert_to_tuple(gold_offsets)))
                  for current_line, gold_offsets in content_to_rate]

    for epoch in range(nb_epochs):
        optimizer: Optimizer = ner_model.entity.create_optimizer()
        random.shuffle(train_data)
        losses = dict()
        batches = minibatch(train_data, size=compounding(4., 16., 1.001))
        for batch in batches:
            texts, manual_annotations = zip(*batch)
            ner_model.update(
                texts,
                manual_annotations,
                drop=0.3,
                losses=losses,
                sgd=optimizer)
        print(f"Epoch {epoch + 1}\n")
        spacy_evaluate(ner_model, content_to_rate_test)
        # print(losses)


if __name__ == '__main__':
    args = parse_args()
    main(data_folder=args.input_dir,
         model_path=args.model_dir,
         dev_size=float(args.dev_size),
         nb_epochs=int(args.epoch))

    # data_folder = "../case_annotation/data/tc/spacy_manual_annotations"
    # model_path = "./resources/model/"
    # dev_size = 0.2

# python fine_tune_pre_trained_model.py -m ./resources/model/ -i ../case_annotation/data/tc/spacy_manual_annotations -s 0.2 -e 20