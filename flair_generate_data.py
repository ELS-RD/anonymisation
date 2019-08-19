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
import time
from typing import List

import spacy
from flair.data import Sentence
from flair.models import SequenceTagger
from spacy.tokens.doc import Doc

from ner.model_factory import get_tokenizer
from resources.config_provider import get_config_default
from xml_extractions.extract_node_values import Paragraph, get_paragraph_from_file

random.seed(123)

tagger: SequenceTagger = SequenceTagger.load('resources/flair_ner/ca/best-model.pt')

config_training = get_config_default()
xml_train_path = config_training["xml_train_path"]

nlp = spacy.blank('fr')
nlp.tokenizer = get_tokenizer(nlp)

generated_paragraphs: List[Sentence] = list()
for filename in os.listdir(xml_train_path):
    if filename.endswith(".xml"):
        current_path = os.path.join(xml_train_path, filename)
        paragraphs = get_paragraph_from_file(path=current_path,
                                             keep_paragraph_without_annotation=True)
        if len(paragraphs) > 50000:
            for paragraph in random.sample(paragraphs, 50000):   # type: Paragraph
                if len(paragraph.text) > 0:
                    doc: Doc = nlp(paragraph.text)
                    s = Sentence(' '.join([w.text for w in doc]))
                    generated_paragraphs.append(s)

start_time = time.time()
_ = tagger.predict(generated_paragraphs, 100)
elapsed_time = time.time() - start_time
print(elapsed_time)  # 91 mn

text_lines: List[str] = list()
offset_lines: List[str] = list()
for sentence in generated_paragraphs:
    text_lines.append(sentence.to_tokenized_string())
    offset_line = [f"{tag.start_pos} {tag.end_pos} {tag.tag}" for tag in sentence.get_spans('ner')]
    offset_lines.append(",".join(offset_line))

assert len(offset_lines) == len(text_lines)

with open("./resources/training_data/generated_annotations.txt", mode='w') as f:
    f.write("\n".join(text_lines))
with open("./resources/training_data/generated_annotations.ent", mode='w') as f:
    f.write("\n".join(offset_lines))
