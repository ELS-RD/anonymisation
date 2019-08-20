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
from typing import List, Tuple

import spacy
from flair.data import Corpus, Sentence
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from spacy.language import Language
from spacy.tokens.doc import Doc

from misc.command_line import train_parse_args
from misc.import_annotations import prepare_flair_train_test_corpus
from ner.model_factory import get_tokenizer
from xml_extractions.extract_node_values import Offset

# CPU
# flair.device = torch.device('cpu')
# torch.set_num_threads(1)

# reproducibility
random.seed(1230)


def parse_texts(spacy_model: Language, flair_model: ModelTrainer, texts: List[str], batch_size=32) -> Tuple[List[List[Offset]],  List[Sentence]]:
    sentences = list()
    docs = list()
    for text in texts:
        doc: spacy.tokens.doc.Doc = spacy_model(text)
        docs.append(doc)
        sentence = Sentence(' '.join([w.text for w in doc]))
        sentences.append(sentence)
    start = time.time()
    _ = flair_model.predict(sentences, batch_size)
    print(time.time() - start)

    offsets: List[List[Offset]] = list()
    for doc, sentence in zip(docs, sentences):
        current_line_offsets = list()
        for entity in sentences[0].get_spans('ner'):
            # flair indexes starts at 1 but Spacy is 0 based
            indexes = [t.idx - 1 for t in entity.tokens]
            start = doc[indexes[0]].idx
            end = doc[indexes[-1]].idx + len(doc[indexes[-1]].text)
            current_line_offsets.append(Offset(start, end, entity.tag))
        offsets.append(current_line_offsets)

    return offsets, sentences


def main(data_folder: str, model_folder: str, dev_size: float) -> None:
    nlp = spacy.blank('fr')
    nlp.tokenizer = get_tokenizer(nlp)

    corpus: Corpus = prepare_flair_train_test_corpus(spacy_model=nlp, data_folder=data_folder, dev_size=dev_size)

    model_path = os.path.join(model_folder, 'best-model.pt')
    tagger: SequenceTagger = SequenceTagger.load(model_path)
    test_results, _ = tagger.evaluate(corpus.test)
    print(test_results.detailed_results)

    sentences_predict = [Sentence(s.to_tokenized_string()) for s in corpus.train + corpus.test]

    start = time.time()
    _ = tagger.predict(sentences_predict, 50)
    print(time.time() - start)

    for index, (sentence_original, sentence_predict) \
            in enumerate(zip(corpus.train + corpus.test, sentences_predict)):  # type: int, (Sentence, Sentence)
        sentence_original.get_spans('ner')
        expected_entities_text = {f"{s.text} {s.tag}"
                                  for s in sentence_original.get_spans('ner')
                                  if s.tag in ["PERS", "ADDRESS", "ORGANIZATION"]}
        predicted_entities_text = {f"{s.text} {s.tag}"
                                   for s in sentence_predict.get_spans('ner')
                                   if s.tag in ["PERS", "ADDRESS", "ORGANIZATION"]}
        diff_expected = expected_entities_text.difference(predicted_entities_text)
        diff_predicted = predicted_entities_text.difference(expected_entities_text)

        if (len(diff_predicted) > 0):  # (len(diff_expected) > 0) or
            print("------------")
            print(f"source {index}: [{sentence_original.to_plain_string()}]")
            print(f"expected missing: [{diff_expected}]")
            print(f"predicted missing: [{diff_predicted}]")
            print(f"common: [{set(predicted_entities_text).intersection(set(expected_entities_text))}]")


if __name__ == '__main__':
    args = train_parse_args(train=False)
    main(data_folder=args.input_dir,
         model_folder=args.model_dir,
         dev_size=float(args.dev_size))


# data_folder = "../case_annotation/data/tc/spacy_manual_annotations"
# model_folder = "resources/flair_ner/tc/"
# dev_size = 0.2

# data_folder = "../case_annotation/data/appeal_court/spacy_manual_annotations"
# model_folder = "resources/flair_ner/ca/"
# dev_size = 0.2
