#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

import warnings
import logging
import random
import os
from spacy.tokens.doc import Doc  # type: ignore
from spacy.language import Language  # type: ignore
from tqdm import tqdm  # type: ignore

from argparse import ArgumentParser, Namespace
from match_text_unsafe.build_entity_dictionary import EntityTypename
from xml_extractions.extract_node_values import get_paragraph_from_folder
from annotate_case.annotate_case import complete_case_annotations
from ner.model_factory import get_empty_model

from typing import List, Tuple, Iterable

Offset = Tuple[int, int, str]
Case = List[Tuple[str, str, List[str], List[Offset]]]

warnings.filterwarnings('ignore')


def parse_args() -> Namespace:
    """
    Parse command line arguments.

    :returns: a namespace with all the set parameters
    """

    parser = ArgumentParser(
        description='Annotate a sample of the given files in the input directory'
    )
    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        '-q', '--quiet',
        help="Silent execution",
        action="store_const", dest="loglevel", const=logging.ERROR,
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
        '-o', '--output-files-dir',
        help="Output files directory",
        action="store", dest="output_dir",
        required=True
    )
    parser.add_argument(
        '-k', '--sample-size',
        help="Sample size",
        type=int,
        action="store", dest="sample_size",
        required=True
    )
    parser.add_argument(
        '-s', '--seed',
        help="Seed",
        type=int,
        action="store", dest="seed",
        default=123
    )
    args = parser.parse_args()
    return args


def random_iter(iterable: Iterable, size: int, seed: int = 123) -> Iterable:
    """
    Get a random sample iterator.

    :param iterable: the iterable to pick a random sample from
    :param size: the size of the sample
    :param seed: the random seed
    :returns: an iterator of the random sample
    """

    random.seed(seed)
    sequence = list(iterable)
    assert (len(sequence) >= size)
    sample = random.sample(sequence, size)
    return iter(sample)


def annotate_case(case: Case, entity_typename_builder: EntityTypename, nlp: Language) -> List[Doc]:
    """
    Annotate one case.

    :param case: the case id
    :param entity_typename_builder: the entity typename dictionary builder
    :param nlp: the spacy tagger

    """

    spacy_docs = list()
    entity_typename_builder.clear()

    for _, original_text, _, _ in case:
        spacy_doc = nlp(original_text)
        entity_typename_builder.add_spacy_entities(spacy_doc=spacy_doc)
        spacy_docs.append(spacy_doc)

    spans = entity_typename_builder.get_dict()
    complete_case_annotations(spacy_docs, spans)

    return spacy_docs


def save_doc(case: Case, spacy_docs: List[Doc], directory: str) -> None:
    """
    Save document annotation.

    :param case: the case id
    :param spacy_docs: the spacy annotations
    :param directory: the output directory
    """

    assert (len(case) == len(spacy_docs))
    assert (len(case) > 0)

    case_id, _, _, _ = case[0]
    text_file = os.path.join(directory, case_id) + '.txt'
    ents_file = os.path.join(directory, case_id) + '.ents'
    with open(text_file, 'w') as out:
        for _, original_text, _, _ in case:
            out.write(original_text + '\n')
    sep_inter_token = ','
    sep_intra_token = ' '
    with open(ents_file, 'w') as out:
        for spacy_doc in spacy_docs:
            out.write(sep_inter_token.join(
                [sep_intra_token.join([str(ent.start_char), str(ent.end_char), ent.label_]) for ent in
                 spacy_doc.ents]) + '\n')


# TODO merge with annotate_txt
def annotate_xml(model_dir_path: str, files_dir_path: str, out_dir_path: str, sample_size: int, seed: int) -> None:
    """
    Annotate a sample of the given XML files and save them into the given directory.

    :param model_dir_path: the directory of the Spacy model
    :param files_dir_path: the directory containing the XML files
    :param out_dir_path: the directory where to write the annotations
    :param sample_size: the size of the sample to annotate
    :param seed: the seed to select an random sample
    """

    logging.info("Loading NER model…")
    nlp = get_empty_model(load_labels_for_training=False)
    nlp = nlp.from_disk(model_dir_path)
    entity_typename_builder = EntityTypename()

    logging.info("Loading cases…")
    cases = list(random_iter(
        get_paragraph_from_folder(folder_path=files_dir_path,
                                  keep_paragraph_without_annotation=True,
                                  flatten=False), sample_size, seed=seed))

    with tqdm(total=len(cases), unit=" cases", desc="Find entities") as progress_bar:
        for case in cases:
            if len(case) > 0:
                spacy_docs = annotate_case(case, entity_typename_builder, nlp)
                save_doc(case, spacy_docs, out_dir_path)
                progress_bar.update()
            else:
                logging.error("Empty case")


def annotate_txt(model_dir_path: str, files_dir_path: str, out_dir_path: str) -> None:
    """
    Annotate a sample of the given flat text files and save them into the given directory.

    :param model_dir_path: the directory of the Spacy model
    :param files_dir_path: the directory containing the text files
    :param out_dir_path: the directory where to write the annotations
    """

    logging.info("Loading NER model…")
    nlp = get_empty_model(load_labels_for_training=False)
    nlp = nlp.from_disk(model_dir_path)
    entity_typename_builder = EntityTypename()

    logging.info("Loading cases…")

    cases: List[Case] = list()

    for filename in os.listdir(files_dir_path):
        case: Case = list()
        basename = filename.split(".")[0]
        path = os.path.join(files_dir_path, filename)
        with open(path) as f:
            lines = f.readlines()
            for line in lines:
                if len(line) > 1:
                    clean_text = line.strip()
                    case.append((basename, clean_text, list(), list()))
            cases.append(case)

    with tqdm(total=len(cases), unit=" cases", desc="Find entities") as progress_bar:
        for case in cases:
            if len(case) > 0:
                spacy_docs = annotate_case(case, entity_typename_builder, nlp)
                save_doc(case, spacy_docs, out_dir_path)
                progress_bar.update()
            else:
                logging.error("Empty case")


def main() -> None:
    args = parse_args()

    if args.loglevel == logging.DEBUG:
        log_format = '%(asctime)s %(levelname)s %(funcName)s: %(message)s'
    else:
        log_format = logging.BASIC_FORMAT
    logging.basicConfig(level=args.loglevel, format=log_format)

    annotate_xml(args.model_dir, args.input_dir, args.output_dir, args.sample_size, args.seed)


if __name__ == '__main__':
    main()
