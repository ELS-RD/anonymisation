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
from typing import Optional

import spacy
from flair.data import Corpus, Sentence, Span
from flair.models import SequenceTagger
from misc.command_line import train_parse_args
from misc.import_annotations import prepare_flair_train_dev_corpus
from ner.model_factory import get_tokenizer


# reproducibility
random.seed(5)


def main(
    data_folder: str, model_folder: str, dev_size: float, nb_segment: Optional[int], segment: Optional[int]
) -> None:
    nlp = spacy.blank(name="fr")
    nlp.tokenizer = get_tokenizer(nlp)

    corpus: Corpus = prepare_flair_train_dev_corpus(
        spacy_model=nlp, data_folder=data_folder, dev_size=dev_size, nb_segment=nb_segment, segment=segment
    )
    print(corpus)
    # flair.device = torch.device('cpu')  # (4mn 28)
    tagger: SequenceTagger = SequenceTagger.load(model=os.path.join(model_folder, "best-model.pt"))
    test_results, _ = tagger.evaluate(sentences=corpus.dev, mini_batch_size=32)
    print(test_results.detailed_results)

    sentences_predict = copy.deepcopy(corpus.dev.sentences)
    # clean tokens in case there is a bug
    for s in sentences_predict:
        for t in s:
            t.tags = {}

    _ = tagger.predict(sentences=sentences_predict, mini_batch_size=32, embedding_storage_mode="none", verbose=True)

    def span_to_str(span: Span) -> str:
        start_token = span.tokens[0].idx
        end_token = span.tokens[len(span.tokens) - 1].idx
        token_position = f"{start_token}" if start_token == end_token else f"{start_token}-{end_token}"
        return f"{span.text} [{span.tag}] ({token_position})"

    for index, (sentence_original, sentence_predict) in enumerate(
        zip(corpus.dev, sentences_predict)
    ):  # type: int, (Sentence, Sentence)
        expected_entities_text = [span_to_str(span=s) for s in sentence_original.get_spans("ner")]
        predicted_entities_text = [span_to_str(span=s) for s in sentence_predict.get_spans("ner")]

        diff_expected = [i for i in expected_entities_text if i not in predicted_entities_text]
        diff_predicted = [i for i in predicted_entities_text if i not in expected_entities_text]
        common_expected_predicted = [i for i in predicted_entities_text if i in expected_entities_text]

        if len(diff_predicted) > 0:
            print("------------")
            print(f"source {index}: [{sentence_original.to_plain_string()}]")
            print(f"expected missing: [{diff_expected}]")
            print(f"predicted missing: [{diff_predicted}]")
            print(f"common: [{common_expected_predicted}]")


if __name__ == "__main__":
    args = train_parse_args(train=False)
    assert int(args.nb_segment is None) + int(args.dev_size is None) == 1
    main(
        data_folder=args.input_dir,
        model_folder=args.model_dir,
        dev_size=args.dev_size,
        nb_segment=args.nb_segment,
        segment=args.segment,
    )
