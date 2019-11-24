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
import tempfile
from typing import List, Tuple

from flair.data import Corpus
from flair.datasets import ColumnCorpus
from spacy.gold import GoldParse
from spacy.language import Language
from spacy.tokens.doc import Doc

from xml_extractions.extract_node_values import Offset


def parse_offsets(text: str) -> Offset:
    """
    Convert to the right offset format
    :param text: original line
    :return: a tuple containing the offset
    """
    item = text.split(' ')
    return Offset(int(item[0]), int(item[1]), item[2])


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
            content_case = [item[:-1] if item[-1] is "\n" else item for item in f.readlines()]
        path_annotations = txt_path.replace('.txt', '.ent')
        with open(path_annotations, 'r') as f:
            # strip to remove \n
            annotations = [item.strip() for item in f.readlines()]

        if len(content_case) == 0:
            continue
        assert len(content_case) == len(annotations)

        for line_case, line_annotations in zip(content_case, annotations):
            gold_offsets = [parse_offsets(item) for item in line_annotations.split(',') if item != ""]
            results.append((line_case, gold_offsets))

    return results


def convert_to_flair_format(spacy_model: Language, data: List[Tuple[str, List[Offset]]]) -> List[str]:
    result: List[str] = list()
    for text, offsets in data:
        doc: Doc = spacy_model(text)
        # remove duplicated offsets
        offset_tuples = list(set([offset.to_tuple() for offset in offsets]))
        gold_annotations = GoldParse(doc, entities=offset_tuples)
        annotations: List[str] = gold_annotations.ner
        assert len(annotations) == len(doc)
        # Flair uses BIOES and Spacy BILUO
        # BILUO for Begin, Inside, Last, Unit, Out
        # BIOES for Begin, Inside, Outside, End, Single
        annotations = [a.replace('L-', 'E-') for a in annotations]
        annotations = [a.replace('U-', 'S-') for a in annotations]
        result += [f"{word} {tag}\n" for word, tag in zip(doc, annotations)]
        result.append('\n')
    return result


def export_data_set_flair_format(spacy_model: Language, data_file_names: List[str]) -> str:
    data = load_content(txt_paths=data_file_names)
    data_flair_format = convert_to_flair_format(spacy_model, data)
    f = tempfile.NamedTemporaryFile(delete=False, mode="w")
    tmp_path = f.name
    f.writelines(data_flair_format)
    f.close()
    return tmp_path


def prepare_flair_train_test_corpus(spacy_model: Language, data_folder: str, dev_size: float) -> Corpus:

    all_annotated_files: List[str] = [os.path.join(data_folder, filename)
                                      for filename in os.listdir(data_folder) if filename.endswith(".txt")]
    random.shuffle(all_annotated_files)

    nb_doc_dev_set: int = int(len(all_annotated_files) * dev_size)

    dev_file_names = all_annotated_files[0:nb_doc_dev_set]

    train_file_names = [file for file in all_annotated_files if file not in dev_file_names]

    train_path = export_data_set_flair_format(spacy_model, train_file_names)
    dev_path = export_data_set_flair_format(spacy_model, dev_file_names)

    corpus: Corpus = ColumnCorpus(data_folder=tempfile.gettempdir(),
                                  column_format={0: 'text', 1: 'ner'},
                                  train_file=os.path.basename(train_path),
                                  dev_file=os.path.basename(dev_path),
                                  test_file=os.path.basename(dev_path))
    return corpus
