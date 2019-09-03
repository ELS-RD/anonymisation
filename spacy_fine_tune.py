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
from typing import Tuple, List, Optional

from spacy.gold import GoldParse
from spacy.scorer import Scorer
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy.util import minibatch, compounding
from thinc.neural.optimizers import Optimizer

from misc.command_line import train_parse_args
from misc.import_annotations import load_content
from ner.model_factory import get_empty_model, get_tokenizer
from xml_extractions.extract_node_values import Offset

# reproducibility
random.seed(1230)


def spacy_evaluate(model, dev: List[Tuple[str, List[Offset]]], print_diff: bool) -> None:
    """
    Compute entity global scores according to Spacy
    :param model: Spacy NER model
    :param dev: list of tuples containgin the filename, the text, and the offsets
    :return: a dict of scores
    """
    s = Scorer()

    for index, (text, offsets) in enumerate(dev):
        doc = model.make_doc(text)
        offset_tuples = [offset.to_tuple() for offset in offsets]
        expected_entities: List[Span] = [doc.char_span(o[0], o[1]) for o in offset_tuples]
        if None in expected_entities:
            raise Exception(f"entity parsing failed: [{expected_entities}], for offsets [{offset_tuples}] in [{text}]")

        predicted_entities: Doc = model(text)

        gold: GoldParse = GoldParse(doc, entities=offset_tuples)
        s.score(predicted_entities, gold)

        if print_diff:
            expected_entities_text = {e.text for e in expected_entities if
                                      e.label_ in ["PERS", "ADDRESS", "ORGANIZATION"]}
            predicted_entities_text = {e.text for e in predicted_entities.ents if
                                       e.label_ in ["PERS", "ADDRESS", "ORGANIZATION"]}
            # diff_expected = set(expected_entities_text).difference(set(predicted_entities_text))
            # diff_predicted = set(predicted_entities_text).difference(set(expected_entities_text))
            # diff = list()
            # for p in predicted_entities_text:
            #     if not any([(p in e) or (e in p) for e in expected_entities_text]):
            #         diff.append(p)

            # if (len(diff_expected) > 0) or (len(diff_predicted) > 0):
            #     print("------------")
            #     print(f"source: [{text}]")
            #     print(f"expected missing: [{diff_expected}]")
            #     print(f"predicted missing: [{diff_predicted}]")
            #     print(f"common: [{set(predicted_entities_text).intersection(set(expected_entities_text))}]")

            diff_expected = expected_entities_text.difference(predicted_entities_text)
            diff_predicted = predicted_entities_text.difference(expected_entities_text)

            if (len(diff_predicted) > 0):  # (len(diff_expected) > 0) or
                print("------------")
                print(f"source {index}: [{text}]")
                print(f"expected missing: [{diff_expected}]")
                print(f"predicted missing: [{diff_predicted}]")
                print(f"common: [{set(predicted_entities_text).intersection(set(expected_entities_text))}]")

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


def main(data_folder: str, model_path: Optional[str], dev_size: float, nb_epochs: int, print_diff: bool) -> None:
    nlp = get_empty_model(load_labels_for_training=True)
    if model_path is not None:
        nlp = nlp.from_disk(path=model_path)
        nlp.tokenizer = get_tokenizer(nlp)  # replace tokenizer
        nlp.begin_training()
        # ner = nlp.get_pipe("ner")
        # ner.model.learn_rate = 0.0001
    else:
        nlp.tokenizer = get_tokenizer(nlp)  # replace tokenizer
        nlp.begin_training()

    all_annotated_files: List[str] = [os.path.join(data_folder, filename)
                                      for filename in os.listdir(data_folder) if filename.endswith(".txt")]
    random.shuffle(all_annotated_files)

    nb_doc_dev_set: int = int(len(all_annotated_files) * dev_size)

    dev_file_names = all_annotated_files[0:nb_doc_dev_set]

    train_file_names = [file for file in all_annotated_files if file not in dev_file_names]
    # train_file_names = ["./resources/training_data/generated_annotations.txt"] + train_file_names

    content_to_rate = load_content(txt_paths=train_file_names)
    content_to_rate_test = load_content(txt_paths=dev_file_names)

    print(f"nb PERS entities {sum([1 for _, offsets in content_to_rate for o in offsets if o.type == 'PERS'])}")

    if model_path is not None:
        print("evaluation without fine tuning")
        spacy_evaluate(nlp, content_to_rate_test, print_diff)

    train_data: List[Tuple[str, GoldParse]] = list()
    for current_line, gold_offsets in content_to_rate:
        entities = []
        space_error = False
        for offset in gold_offsets:
            text = current_line[offset.start:offset.end]
            if text == text.strip():
                entities.append(offset.to_tuple())
            else:
                space_error = True
                break
        if space_error:
            continue
        gold = GoldParse(nlp.make_doc(current_line), entities=entities)
        train_data.append((current_line, gold))

    optimizer: Optimizer = nlp.resume_training()

    for epoch in range(nb_epochs):
        print(f"------- {epoch}  -------")
        random.shuffle(train_data)
        losses = dict()
        batches = minibatch(train_data, size=compounding(4., 16., 1.001))
        for batch in batches:
            texts, manual_annotations = zip(*batch)  # type: List[str], List[GoldParse]
            nlp.update(
                texts,
                manual_annotations,
                drop=0.5,
                losses=losses,
                sgd=optimizer)
        print(f"Epoch {epoch + 1}\nLoss: {losses}\n")
        spacy_evaluate(model=nlp,
                       dev=content_to_rate_test,
                       print_diff=print_diff)


if __name__ == '__main__':
    args = train_parse_args(train=True)
    main(data_folder=args.input_dir,
         model_path=args.model_dir,
         dev_size=float(args.dev_size),
         nb_epochs=int(args.epoch),
         print_diff=False)

# data_folder = "../case_annotation/data/appeal_court/spacy_manual_annotations"
# model_path = "./resources/model"
# dev_size = 0.2
# nb_epochs = 1
# print_diff = False
