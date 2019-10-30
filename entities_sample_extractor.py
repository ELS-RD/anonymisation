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

import logging
import os
import random
import warnings
from argparse import ArgumentParser, Namespace
from typing import List

import spacy
from spacy.language import Language  # type: ignore
from spacy.tokens.doc import Doc  # type: ignore
from tqdm import tqdm  # type: ignore

from annotate_case.annotate_case import complete_case_annotations
from match_text_unsafe.build_entity_dictionary import EntityTypename
from ner.model_factory import get_empty_model
from xml_extractions.extract_node_values import Paragraph, get_paragraph_from_file, Case

warnings.filterwarnings('ignore')
random.seed(5)


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
    args = parser.parse_args()
    return args


def annotate_case(case: Case, entity_typename_builder: EntityTypename, nlp: Language) -> List[Doc]:
    """
    Annotate one case.

    :param case: the case id
    :param entity_typename_builder: the entity typename dictionary builder
    :param nlp: the spacy tagger

    """

    spacy_docs = list()
    entity_typename_builder.clear()

    for paragraph in case:
        spacy_doc = nlp(paragraph.text)
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

    first_paragraph = case[0]
    text_file = os.path.join(directory, first_paragraph.case_id) + '.txt'
    ents_file = os.path.join(directory, first_paragraph.case_id) + '.ents'
    with open(text_file, 'w') as out:
        for paragraph in case:
            out.write(paragraph.text + '\n')
    sep_inter_token = ','
    sep_intra_token = ' '
    with open(ents_file, 'w') as out:
        for spacy_doc in spacy_docs:
            out.write(sep_inter_token.join(
                [sep_intra_token.join([str(ent.start_char), str(ent.end_char), ent.label_]) for ent in
                 spacy_doc.ents]) + '\n')


# TODO replace files dir by a list of paths
def annotate(model_dir_path: str, files_dir_path: List[str], out_dir_path: str) -> None:
    """
    Annotate a sample of the given XML files and save them into the given directory.

    :param model_dir_path: the directory of the Spacy model
    :param files_dir_path: the directory containing the XML files
    :param out_dir_path: the directory where to write the annotations
    """

    logging.info("Loading NER model…")
    nlp = get_empty_model(load_labels_for_training=False)
    nlp = nlp.from_disk(model_dir_path)

    # TODO remove when we have retrained
    infixes = nlp.Defaults.infixes + [r':', r"(?<=[\W\d_])-|-(?=[\W\d_])"]
    infixes_regex = spacy.util.compile_infix_regex(infixes)
    nlp.tokenizer.infix_finditer = infixes_regex.finditer
    # end of deletion above

    entity_typename_builder = EntityTypename()

    logging.info("Loading cases…")

    cases: List[Case] = list()
    for path in files_dir_path:
        if path.endswith(".xml"):
            case: Case = get_paragraph_from_file(path=path,
                                                 keep_paragraph_without_annotation=True)
            cases.append(case)
        elif path.endswith(".txt"):
            with open(path) as f:
                lines = f.readlines()
                case: Case = list()
                for line in lines:
                    clean_text = line.strip()
                    if len(clean_text) > 1:
                        basename = os.path.basename(path)
                        basename = basename.split(".")[0]
                        case.append(Paragraph(basename, clean_text, list(), list()))
                cases.append(case)
        else:
            raise Exception(f"can't parse, unknown file extension': {path}")

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

    input_paths = [os.path.join(args.input_dir, filename)
                   for filename in os.listdir(args.input_dir)]

    if len(input_paths) >= args.sample_size:
        input_paths = random.sample(input_paths, args.sample_size)

    annotate(args.model_dir, input_paths, args.output_dir)


if __name__ == '__main__':
    main()
