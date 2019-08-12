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
from argparse import Namespace, ArgumentParser
from typing import List, Tuple

import spacy
from flair.data import Corpus, Sentence
from flair.datasets import ColumnCorpus
from flair.embeddings import StackedEmbeddings, TokenEmbeddings, WordEmbeddings, FlairEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from spacy.gold import GoldParse
from spacy.lang.fr import French
from spacy.tokens.doc import Doc

from misc.command_line import train_parse_args
from misc.import_annotations import load_content
from ner.model_factory import get_tokenizer
from xml_extractions.extract_node_values import Offset

# reproducibility
random.seed(123)


def convert_to_flair_format(model: French, data: List[Tuple[str, List[Offset]]]) -> List[str]:
    result: List[str] = list()
    for text, offsets in data:
        doc: Doc = model(text)
        offset_tuples = [offset.to_tuple() for offset in offsets]
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


def export_data_set(model: French, data_file_names: List[str]) -> str:
    data = load_content(txt_paths=data_file_names)
    data_flair_format = convert_to_flair_format(model, data)
    f = tempfile.NamedTemporaryFile(delete=False, mode="w")
    tmp_path = f.name
    f.writelines(data_flair_format)
    f.close()
    return tmp_path


def main(data_folder: str, model_folder: str, dev_size: float, nb_epochs: int, print_diff: bool) -> None:

    nlp = spacy.blank('fr')
    nlp.tokenizer = get_tokenizer(nlp)

    all_annotated_files: List[str] = [os.path.join(data_folder, filename)
                                      for filename in os.listdir(data_folder) if filename.endswith(".txt")]
    random.shuffle(all_annotated_files)

    nb_doc_dev_set: int = int(len(all_annotated_files) * dev_size)

    dev_file_names = all_annotated_files[0:nb_doc_dev_set]

    train_file_names = [file for file in all_annotated_files if file not in dev_file_names]

    train_path = export_data_set(nlp, train_file_names)
    dev_path = export_data_set(nlp, dev_file_names)

    corpus: Corpus = ColumnCorpus(data_folder="/tmp",
                                  column_format={0: 'text', 1: 'ner'},
                                  train_file=os.path.basename(train_path),
                                  dev_file=os.path.basename(dev_path),
                                  test_file=os.path.basename(dev_path))

    tag_dictionary = corpus.make_tag_dictionary(tag_type='ner')
    print(tag_dictionary.idx2item)

    embedding_types: List[TokenEmbeddings] = [
        WordEmbeddings('fr'),
        FlairEmbeddings('fr-forward'),
        FlairEmbeddings('fr-backward'),
    ]

    embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)

    tagger: SequenceTagger = SequenceTagger(hidden_size=256,
                                            embeddings=embeddings,
                                            tag_dictionary=tag_dictionary,
                                            tag_type='ner')

    trainer: ModelTrainer = ModelTrainer(tagger, corpus)

    trainer.train(model_folder,
                  learning_rate=0.1,
                  checkpoint=True,
                  patience=3,
                  max_epochs=nb_epochs)

    # doc = nlp(sentence.to_original_text())
    #
    # for span in sentence.get_spans('ner'):
    #     idx = [token.idx for token in span.tokens]
    #     span = Span(doc, idx[0]-1, idx[-1], label='PERS')  # Create a span in Spacy
    #     doc.ents = list(doc.ents) + [span]  # add span to doc.ents

    if print_diff:
        tagger = SequenceTagger.load(model_folder + 'final-model.pt')
        # corpus.train +
        for index, sentence in enumerate(corpus.train + corpus.test):  # type: int, Sentence
            text = sentence.to_tokenized_string()
            sentence.get_spans('ner')
            expected_entities_text = {s.text for s in sentence.get_spans('ner')}
            sentence_predict: Sentence = Sentence(text)
            tagger.predict(sentence_predict)
            predicted_entities_text = {s.text for s in sentence_predict.get_spans('ner')}
            diff_expected = expected_entities_text.difference(predicted_entities_text)
            diff_predicted = predicted_entities_text.difference(expected_entities_text)

            if (len(diff_expected) > 0) or (len(diff_predicted) > 0):
                print("------------")
                print(f"source {index}: [{text}]")
                print(f"expected missing: [{diff_expected}]")
                print(f"predicted missing: [{diff_predicted}]")
                print(f"common: [{set(predicted_entities_text).intersection(set(expected_entities_text))}]")


if __name__ == '__main__':
    args = train_parse_args()
    main(data_folder=args.input_dir,
         model_folder=args.model_dir,
         dev_size=float(args.dev_size),
         nb_epochs=int(args.epoch),
         print_diff=args.print_diff)

