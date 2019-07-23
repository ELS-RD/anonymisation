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
from typing import Tuple, List, Union, Optional

from spacy.gold import GoldParse
from spacy.scorer import Scorer
from spacy.tokens.doc import Doc
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
        gold: GoldParse = GoldParse(doc_gold_text, entities=offset_tuples)
        # count_ent_gold = sum([1 for item in gold.ner if item != "O"])
        pred_value: Doc = model(text)
        # if count_ent_gold != len(offsets):
        #     gold_to_print = [text[o.start:o.end] + " - " + o.type for o in offsets]
        #
        #     print("---------")
        #     print("gold:", gold.ner)
        #     print("gold from offset:", gold_to_print)
        #     print(text)
        #     print("---------")

        # pred_ents = [Offset(pred.start_char, pred.end_char, pred.label_) for pred in pred_value.ents]
        # if pred_ents != offsets:
        #     predictions_to_print = ["[" + text[o.start:o.end] + "] - " + o.type for o in pred_ents if (o not in offsets) and o.type == "PERS"]
        #     gold_to_print = [text[o.start:o.end] for o in offsets if (o.type == "PERS")]
        #     contains_space = sum([1 for t in gold_to_print for c in t if not c.isalpha() and not c.isspace()]) > 0
        #
        #     if (len(gold_to_print) > 0) and contains_space:
        #         print("---------")
        #         print([c for t in gold_to_print for c in t if not c.isalpha() and not c.isspace()])
        #         print(pred_ents, "|", offsets)
        #         print("pred:", predictions_to_print)
        #         print("gold:", gold_to_print)
        #         print(text)
        #         print("---------")

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


def recompose_paragraphs(paragraphs: List[Tuple[str, List[Offset]]]) -> List[Tuple[str, List[Offset]]]:
    results = list()
    precedent_paragraph_not_finished = False
    precedent_paragraph: Optional[str] = None
    precedent_offsets = list()
    for index, (current_paragraph, current_offsets) in enumerate(paragraphs):
        current_start_lower_char = current_paragraph[0].islower()

        if current_start_lower_char and precedent_paragraph_not_finished:
            precedent_offsets += [Offset(o.start + len(precedent_paragraph), o.end + len(precedent_paragraph), o.type)
                                  for o in current_offsets]
            precedent_paragraph += " " + current_paragraph

        else:
            if precedent_paragraph is not None:
                results.append((precedent_paragraph, precedent_offsets))
            precedent_paragraph = current_paragraph
            precedent_offsets = current_offsets

        last_char_precedent_paragraph = precedent_paragraph[-1]
        precedent_paragraph_not_finished = (last_char_precedent_paragraph.isalnum() or
                                            (last_char_precedent_paragraph is ","))

        if index == len(paragraphs) - 1 and precedent_paragraph is not None:
            results.append((precedent_paragraph, precedent_offsets))

    return results


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
            # strip to remove \n
            content_case = [item.strip() for item in f.readlines()]
        path_annotations = txt_path.replace('.txt', '.ent')
        with open(path_annotations, 'r') as f:
            # strip to remove \n
            annotations = [item.strip() for item in f.readlines()]

        assert len(content_case) > 0
        assert len(content_case) == len(annotations)

        for line_case, line_annotations in zip(content_case, annotations):
            gold_offsets = [parse_offsets(item) for item in line_annotations.split(',') if item != ""]
            if len(gold_offsets) > 0:
                results.append((line_case, gold_offsets))
    print(len(results))
    results = recompose_paragraphs(results)
    print(len(results))
    return results


def convert_to_tuple(offsets: List[Offset]) -> List[Tuple[int, int, str]]:
    """
    Convert List of offsets to the Tupple format (may be useful as input to Spacy)
    """
    return [offset.to_tuple() for offset in offsets]


def main(data_folder: str, model_path: str, dev_size: float, nb_epochs: int) -> None:
    nlp = get_empty_model(load_labels_for_training=True)
    nlp = nlp.from_disk(path=model_path)
    # ner = nlp.get_pipe("ner")
    # ner.model.learn_rate = 0.0001

    # nlp = spacy.blank('fr')
    # nlp.add_pipe(prevent_sentence_boundary_detection, name='prevent-sbd', first=True)
    # ner: EntityRecognizer = nlp.create_pipe('ner')
    # add labels
    # if load_labels_for_training:
    # entity_types = ["PERS", "PHONE_NUMBER", "LICENCE_PLATE",
    #                 # "SOCIAL_SECURITY_NUMBER",
    #                 "ORGANIZATION", "LAWYER", "JUDGE_CLERK",
    #                 "ADDRESS", "COURT", "DATE", "RG",
    #                 "BAR", "UNKNOWN"]
    # for token_type in entity_types:
    #     ner.add_label(token_type)
    # nlp.add_pipe(ner, last=True)

    # nlp.begin_training()

    all_annotated_files: List[str] = [os.path.join(data_folder, filename)
                                      for filename in os.listdir(data_folder) if filename.endswith(".txt")]
    random.shuffle(all_annotated_files)

    # ner_model.begin_training()

    nb_doc_dev_set: int = int(len(all_annotated_files) * dev_size)

    dev_file_names = all_annotated_files[0:nb_doc_dev_set]

    train_file_names = [file for file in all_annotated_files if file not in dev_file_names]

    content_to_rate = load_content(txt_paths=train_file_names)
    content_to_rate_test = load_content(txt_paths=dev_file_names)

    print("nb PERS entities", sum([1
                                   for text, offsets in content_to_rate
                                   for offset in offsets
                                   if offset.type == "PERS"]))

    spacy_evaluate(nlp, content_to_rate_test)

    train_data = [(current_line, GoldParse(nlp.make_doc(current_line), entities=convert_to_tuple(gold_offsets)))
                  for current_line, gold_offsets in content_to_rate]
    optimizer: Optimizer = nlp.resume_training()

    for epoch in range(nb_epochs):
        random.shuffle(train_data)
        losses = dict()
        batches = minibatch(train_data, size=compounding(4., 16., 1.001))
        for batch in batches:
            texts, manual_annotations = zip(*batch)
            nlp.update(
                texts,
                manual_annotations,
                drop=0.3,
                losses=losses,
                sgd=optimizer)
        print(f"Epoch {epoch + 1}\nLoss: {losses}\n")
        spacy_evaluate(model=nlp,
                       dev=content_to_rate_test)


if __name__ == '__main__':
    args = parse_args()
    main(data_folder=args.input_dir,
         model_path=args.model_dir,
         dev_size=float(args.dev_size),
         nb_epochs=int(args.epoch))
