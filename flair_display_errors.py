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
import copy
import os
import random
from typing import List

import spacy
from flair.data import Corpus, Sentence
from flair.datasets import DataLoader
from flair.models import SequenceTagger

from misc.command_line import train_parse_args
from misc.import_annotations import prepare_flair_train_test_corpus
from ner.model_factory import get_tokenizer

# reproducibility
random.seed(5)


def main(data_folder: str, model_folder: str, dev_size: float, entities_to_remove: List[str]) -> None:
    nlp = spacy.blank('fr')
    nlp.tokenizer = get_tokenizer(nlp)

    corpus: Corpus = prepare_flair_train_test_corpus(spacy_model=nlp, data_folder=data_folder, dev_size=dev_size)
    # flair.device = torch.device('cpu')  # (4mn 28)
    tagger: SequenceTagger = SequenceTagger.load(model=os.path.join(model_folder, 'best-model.pt'))
    test_results, _ = tagger.evaluate(data_loader=DataLoader(corpus.test, batch_size=32))
    print(test_results.detailed_results)

    sentences_original = (corpus.train.sentences + corpus.test.sentences)
    sentences_predict = copy.deepcopy(sentences_original)
    # clean tokens in case there is a bug
    for s in sentences_predict:
        for t in s:
            t.tags = {}

    _ = tagger.predict(sentences=sentences_predict,
                       mini_batch_size=32,
                       embedding_storage_mode="none",
                       verbose=True)

    for index, (sentence_original, sentence_predict) \
            in enumerate(zip(sentences_original, sentences_predict)):  # type: int, (Sentence, Sentence)
        expected_entities_text = {f"{s.text} {s.tag}"
                                  for s in sentence_original.get_spans('ner')
                                  if s.tag not in entities_to_remove}
        predicted_entities_text = {f"{s.text} {s.tag}"
                                   for s in sentence_predict.get_spans('ner')
                                   if s.tag not in entities_to_remove}

        diff_expected = expected_entities_text.difference(predicted_entities_text)
        diff_predicted = predicted_entities_text.difference(expected_entities_text)

        if len(diff_predicted) > 0:  # (len(diff_expected) > 0) or
            print("------------")
            print(f"source {index}: [{sentence_original.to_plain_string()}]")
            print(f"expected missing: [{diff_expected}]")
            print(f"predicted missing: [{diff_predicted}]")
            print(f"common: [{set(predicted_entities_text).intersection(set(expected_entities_text))}]")


if __name__ == '__main__':
    args = train_parse_args(train=False)
    main(data_folder=args.input_dir,
         model_folder=args.model_dir,
         dev_size=float(args.dev_size),
         entities_to_remove=[])
