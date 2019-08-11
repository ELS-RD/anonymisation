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
from typing import List, Tuple

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

    return results