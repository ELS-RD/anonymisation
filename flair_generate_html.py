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

from misc.command_line import train_parse_args
from ner.model_factory import get_tokenizer
from viewer.flair_viewer import render_ner_html, colors
from xml_extractions.extract_node_values import get_paragraph_from_file, Paragraph


def main(data_folder: str, model_folder: str, top_n: float) -> None:
    nlp = spacy.blank('fr')
    nlp.tokenizer = get_tokenizer(nlp)

    sentences: List[Sentence] = list()
    for filename in os.listdir(data_folder):
        if filename.endswith(".xml"):
            current_path = os.path.join(data_folder, filename)
            paragraphs: List[Paragraph] = get_paragraph_from_file(path=current_path,
                                                                  keep_paragraph_without_annotation=True)
            if len(paragraphs) > top_n:
                for paragraph in random.sample(paragraphs, top_n):  # type: Paragraph
                    if len(paragraph.text) > 0:
                        doc: Doc = nlp(paragraph.text)
                        s = Sentence(' '.join([w.text for w in doc]))
                        sentences.append(s)

    model_path = os.path.join(model_folder, 'best-model.pt')
    tagger: SequenceTagger = SequenceTagger.load(model_path)

    start = time.time()
    _ = tagger.predict(sentences, 50)
    print(time.time() - start)

    options = {"labels": {i: i for i in list(colors.keys())}, "colors": colors}

    page_html = render_ner_html(sentences, settings=options)
    with open("sentence.html", "w") as writer:
        writer.write(page_html)


if __name__ == '__main__':
    args = train_parse_args(train=False)
    main(data_folder=args.input_dir,
         model_folder=args.model_dir,
         top_n=float(args.dev_size))

# data_folder = "../case_annotation/data/tc/spacy_manual_annotations"
# model_folder = "resources/flair_ner/tc/"
# dev_size = 0.2

# data_folder = "../case_annotation/data/appeal_court/spacy_manual_annotations"
# model_folder = "resources/flair_ner/ca/"
# dev_size = 0.2
