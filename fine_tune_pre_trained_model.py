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
from typing import Tuple, List, Optional, Dict, Set

from spacy.gold import GoldParse
from spacy.scorer import Scorer
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.util import minibatch, compounding
from thinc.neural.optimizers import Optimizer

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
        required=False
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
        offset_tuples = [offset.to_tuple() for offset in offsets]
        expected_entities: Set[Span] = {doc_gold_text.char_span(o[0], o[1]) for o in offset_tuples}
        # print(text)
        # print(offsets)
        assert None not in expected_entities

        gold: GoldParse = GoldParse(doc_gold_text, entities=offset_tuples)

        predicted_entities: Doc = model(text)

        if set(predicted_entities.ents) != expected_entities:
            diff = set(predicted_entities.ents).difference(expected_entities)
            print("------------")
            print(text)
            print("diff:", diff)
            print("expected:", expected_entities)
            print("offsets:", offset_tuples)
            print("predicted:", list(predicted_entities.ents))

        s.score(predicted_entities, gold)

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


# def recompose_paragraphs(paragraphs: List[Tuple[str, List[Offset]]]) -> List[Tuple[str, List[Offset]]]:
#     results = list()
#     precedent_paragraph_not_finished = False
#     precedent_paragraph: Optional[str] = None
#     precedent_offsets = list()
#     for index, (current_paragraph, current_offsets) in enumerate(paragraphs):
#         current_start_lower_char = current_paragraph[0].islower()
#
#         if current_start_lower_char and precedent_paragraph_not_finished:
#             precedent_offsets += [Offset(o.start + len(precedent_paragraph), o.end + len(precedent_paragraph), o.type)
#                                   for o in current_offsets]
#             precedent_paragraph += " " + current_paragraph
#
#         else:
#             if precedent_paragraph is not None:
#                 results.append((precedent_paragraph, precedent_offsets))
#             precedent_paragraph = current_paragraph
#             precedent_offsets = current_offsets
#
#         last_char_precedent_paragraph = precedent_paragraph[-1]
#         precedent_paragraph_not_finished = (last_char_precedent_paragraph.isalnum() or
#                                             (last_char_precedent_paragraph is ","))
#
#         if index == len(paragraphs) - 1 and precedent_paragraph is not None:
#             results.append((precedent_paragraph, precedent_offsets))
#
#     return results


def load_content(txt_paths: List[str]) -> List[Tuple[str, List[Offset]]]:
    """
    Parse text and offsets files
    :param txt_paths: paths to the text files, offset files are guessed
    :return: parsed information
    """
    results: List[Tuple[str, List[Offset]]] = list()
    file_used: List[str] = list()
    for txt_path in txt_paths:
        if not txt_path.endswith('.txt'):
            raise Exception(f"wrong file in the selection (not .txt): {txt_path}")
        file_used.append(txt_path)
        with open(txt_path, 'r') as f:
            # remove \n only
            content_case = [item[:-1] for item in f.readlines() if item[-1] is "\n"]
        path_annotations = txt_path.replace('.txt', '.ent')
        with open(path_annotations, 'r') as f:
            # strip to remove \n
            annotations = [item.strip() for item in f.readlines()]

        assert len(content_case) > 0
        assert len(content_case) == len(annotations)

        for line_case, line_annotations in zip(content_case, annotations):
            gold_offsets = [parse_offsets(item) for item in line_annotations.split(',') if item != ""]
            results.append((line_case, gold_offsets))
    print(len(results))
    # results = recompose_paragraphs(results)  # TODO why this step is necessary?
    print(len(results))
    return results


def main(data_folder: str, model_path: Optional[str], dev_size: float, nb_epochs: int) -> None:
    nlp = get_empty_model(load_labels_for_training=True)
    if model_path is not None:
        nlp = nlp.from_disk(path=model_path)
        nlp.begin_training()
        # ner = nlp.get_pipe("ner")
        # ner.model.learn_rate = 0.0001
    else:
        nlp.begin_training()

    all_annotated_files: List[str] = [os.path.join(data_folder, filename)
                                      for filename in os.listdir(data_folder) if filename.endswith(".txt")]
    random.shuffle(all_annotated_files)

    nb_doc_dev_set: int = int(len(all_annotated_files) * dev_size)

    dev_file_names = all_annotated_files[0:nb_doc_dev_set]

    train_file_names = [file for file in all_annotated_files if file not in dev_file_names]

    content_to_rate = load_content(txt_paths=train_file_names)
    content_to_rate_test = load_content(txt_paths=dev_file_names)

    print("nb PERS entities", sum([1
                                   for text, offsets in content_to_rate
                                   for offset in offsets
                                   if offset.type == "PERS"]))

    if model_path is not None:
        print("evaluation without fine tuning")
        spacy_evaluate(nlp, content_to_rate_test)

    train_data: List[Tuple[str, GoldParse]] = [(current_line,
                                                GoldParse(nlp.make_doc(current_line),
                                                          entities=[offset.to_tuple() for offset in gold_offsets]))
                                               for current_line, gold_offsets in content_to_rate]

    optimizer: Optimizer = nlp.resume_training()

    for epoch in range(nb_epochs):
        random.shuffle(train_data)
        losses = dict()
        batches = minibatch(train_data, size=compounding(4., 16., 1.001))
        for batch in batches:
            texts, manual_annotations = zip(*batch)  # type: List[str], List[GoldParse]
            nlp.update(
                texts,
                manual_annotations,
                drop=0.3,
                losses=losses,
                sgd=optimizer)
        print(f"Epoch {epoch + 1}\nLoss: {losses}\n")
        spacy_evaluate(model=nlp,
                       dev=content_to_rate_test)


# if __name__ == '__main__':
#     args = parse_args()
#     main(data_folder=args.input_dir,
#          model_path=args.model_dir,
#          dev_size=float(args.dev_size),
#          nb_epochs=int(args.epoch))

main(data_folder="../case_annotation/data/tc/spacy_manual_annotations",
     model_path=None,
     dev_size=0.2,
     nb_epochs=10)
