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
from typing import List

import spacy
from flair.data import Sentence, build_spacy_tokenizer
from flair.models import SequenceTagger

from ner.model_factory import get_tokenizer
from resources.config_provider import get_config_default
from xml_extractions.extract_node_values import Paragraph, get_paragraph_from_file

random.seed(123)

tagger: SequenceTagger = SequenceTagger.load('resources/flair_ner/ca/best-model.pt')

config_training = get_config_default()
nlp = spacy.blank('fr')
nlp.tokenizer = get_tokenizer(nlp)
tokenizer = build_spacy_tokenizer(nlp)

xml_train_path = "../similar_legal_case/data/jurica_original_xml/arrets-juri"  # config_training["xml_train_path"]
files = [os.path.join(path, name) for path, _, files in os.walk(xml_train_path) for name in files]
random.shuffle(files)

with open("./resources/training_data/generated_annotations.txt", mode='w') as generated_text:
    with open("./resources/training_data/generated_annotations.ent", mode='w') as generated_entities:
        for filename in files:
            if filename.endswith(".xml"):
                try:
                    print(f"--- {filename} ---")
                    text_lines: List[str] = list()
                    offset_lines: List[str] = list()
                    print("read XML")
                    generated_paragraphs: List[Sentence] = list()
                    paragraphs = get_paragraph_from_file(path=filename,
                                                         keep_paragraph_without_annotation=True)
                    if len(paragraphs) > 50000:
                        for paragraph in paragraphs:  # type: Paragraph
                            if len(paragraph.text) > 0:
                                s = Sentence(text=paragraph.text, tokenizer=tokenizer)
                                generated_paragraphs.append(s)

                        generated_paragraphs = tagger.predict(sentences=generated_paragraphs,
                                                              mini_batch_size=32,
                                                              verbose=True,
                                                              embedding_storage_mode="none")

                        for sentence in generated_paragraphs:
                            text_lines.append(sentence.original_text)
                            offset_line = [f"{tag.start_pos} {tag.end_pos} {tag.tag}" for tag in
                                           sentence.get_spans('ner')]
                            offset_lines.append(",".join(offset_line))
                        assert len(offset_lines) == len(text_lines)
                        assert len(offset_lines) > 0
                        print("exporting...")
                        generated_text.write("\n".join(text_lines))
                        generated_entities.write("\n".join(offset_lines))
                except Exception as e:
                    print(f"caught an exception: {e}")
