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

import spacy
from flair.data import build_spacy_tokenizer
from flair.models import SequenceTagger
from flair.visual.ner_html import render_ner_html
from spacy.language import Language
from tqdm import tqdm

from misc.command_line import train_parse_args
from ner.model_factory import get_tokenizer, colors


def main(data_folder: str, output_folder: str, model_folder: str) -> None:
    nlp: Language = spacy.blank('fr')
    nlp.tokenizer = get_tokenizer(nlp)
    tokenizer = build_spacy_tokenizer(nlp)
    filenames = [filename for filename in os.listdir(data_folder) if filename.endswith(".txt")]
    tagger: SequenceTagger = SequenceTagger.load(os.path.join(model_folder, 'best-model.pt'))

    for filename in tqdm(iterable=filenames, unit=" txt", desc="anonymize cases"):
        with open(os.path.join(data_folder, filename), 'r') as input_f:
            sentences = tagger.predict(sentences=input_f.readlines(),
                                       mini_batch_size=32,
                                       verbose=False,
                                       use_tokenizer=tokenizer)
            case_name = filename.split('.')[0]
            page_html = render_ner_html(sentences, colors=colors, title=case_name)

            with open(os.path.join(output_folder, case_name + ".html"), "w") as output:
                output.write(page_html)


if __name__ == '__main__':
    args = train_parse_args(train=False)
    assert args.dev_size >= 1
    main(data_folder=args.input_dir,
         model_folder=args.model_dir)

# data_folder = "resources/tc/txt"
# output_folder = "resources/tc/html"
# model_folder = "resources/flair_ner/tc/"
# top_n = 50
