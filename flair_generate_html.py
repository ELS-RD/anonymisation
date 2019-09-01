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
from typing import List

import spacy
from flair.data import Sentence, build_spacy_tokenizer
from flair.models import SequenceTagger
from flair.visual.ner_html import render_ner_html
from spacy.language import Language
from tqdm import tqdm

from misc.command_line import train_parse_args
from ner.model_factory import get_tokenizer
from viewer.flair_viewer import colors
from xml_extractions.extract_node_values import get_paragraph_from_file, Paragraph


def main(data_folder: str, model_folder: str, top_n: int) -> None:
    print(f"keep only top {top_n} examples per file")
    nlp: Language = spacy.blank('fr')
    nlp.tokenizer = get_tokenizer(nlp)
    tokenizer = build_spacy_tokenizer(nlp)
    filenames = [filename for filename in os.listdir(data_folder) if filename.endswith(".xml")]
    sentences: List[Sentence] = list()
    with tqdm(total=len(filenames), unit=" XML", desc="Parsing XML") as progress_bar:
        for filename in filenames:
            paragraphs: List[Paragraph] = get_paragraph_from_file(path=os.path.join(data_folder, filename),
                                                                  keep_paragraph_without_annotation=True)
            if len(paragraphs) > top_n:
                for paragraph in paragraphs[:top_n]:
                    if len(paragraph.text) > 0:
                        s = Sentence(text=paragraph.text, tokenizer=tokenizer)
                        sentences.append(s)
            progress_bar.update()
    if len(sentences) == 0:
        raise Exception("No example loaded, causes: no cases in provided path or sample size is to high")

    tagger: SequenceTagger = SequenceTagger.load(os.path.join(model_folder, 'best-model.pt'))
    _ = tagger.predict(sentences=sentences,
                       mini_batch_size=32,
                       verbose=True,
                       embedding_storage_mode="cpu")

    print("prepare html")
    page_html = render_ner_html(sentences, colors=colors)
    print("write html")
    with open("sentence.html", "w") as writer:
        writer.write(page_html)


if __name__ == '__main__':
    args = train_parse_args(train=False)
    assert int(args.dev_size) >= 1
    main(data_folder=args.input_dir,
         model_folder=args.model_dir,
         top_n=int(args.dev_size))

# data_folder = "../case_annotation/data/tc/spacy_manual_annotations"
# model_folder = "resources/flair_ner/tc/"
# top_n = 2000

# data_folder = "resources/training_data"
# model_folder = "resources/flair_ner/ca/"
# top_n = 50
