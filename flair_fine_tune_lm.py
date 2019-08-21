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
from typing import List, Tuple, Iterable

from flair.data import Dictionary, Sentence
from flair.embeddings import FlairEmbeddings
from flair.trainers.language_model_trainer import LanguageModelTrainer, TextCorpus
from tqdm import tqdm

from resources.config_provider import get_config_default
from xml_extractions.extract_node_values import get_paragraph_from_file

random.seed(123)


def chunks(content: List, n: int) -> Iterable[Tuple[int, List]]:
    for i in range(0, len(content), n):
        yield i / n, content[i:i + n]


config_training = get_config_default()
xml_train_path = config_training["xml_train_path"]

all_paragraphs = list()
generated_paragraphs: List[Sentence] = list()
xml_files = os.listdir(xml_train_path)
with tqdm(total=len(xml_files), unit=" xml", desc="extract text from XML") as progress_bar:
    for filename in xml_files:
        if filename.endswith(".xml"):
            current_path = os.path.join(xml_train_path, filename)
            paragraphs = get_paragraph_from_file(path=current_path,
                                                 keep_paragraph_without_annotation=True)
            if len(paragraphs) > 50000:
                all_paragraphs += [p.text for p in paragraphs]
        progress_bar.update()

tmp_path: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
print(f"tmp folder: {tmp_path.name}")

os.mkdir(os.path.join(tmp_path.name, "train"))

random.shuffle(all_paragraphs)
limit_train = int(len(all_paragraphs) * 0.9)
train_set = all_paragraphs[:limit_train]
dev_set = all_paragraphs[limit_train:]

print("write files")
for index, l in chunks(train_set, 100000):
    filename = f"train_split_{index}"
    with open(os.path.join(tmp_path.name, "train", filename), 'w') as f:
        f.writelines("\n".join(l))

with open(os.path.join(tmp_path.name, "valid.txt"), 'w') as f:
    f.writelines("\n".join(dev_set))

with open(os.path.join(tmp_path.name, "test.txt"), 'w') as f:
    f.writelines("\n".join(dev_set))

print("load original model")
language_model = FlairEmbeddings('fr-backward').lm
is_forward_lm = language_model.is_forward_lm
dictionary: Dictionary = language_model.dictionary

print("load corpus")
corpus = TextCorpus(tmp_path.name,
                    dictionary,
                    is_forward_lm,
                    character_level=True)

print("start training")
trainer = LanguageModelTrainer(language_model, corpus)

trainer.train('resources/flair_ner/lm/ca_backward',
              sequence_length=100,
              mini_batch_size=100,
              learning_rate=20,
              patience=10,
              max_epochs=5,
              checkpoint=True)


print("load original model")
language_model = FlairEmbeddings('fr-forward').lm
is_forward_lm = language_model.is_forward_lm
dictionary: Dictionary = language_model.dictionary

print("load corpus")
corpus = TextCorpus(tmp_path.name,
                    dictionary,
                    is_forward_lm,
                    character_level=True)

print("start training")
trainer = LanguageModelTrainer(language_model, corpus)

trainer.train('resources/flair_ner/lm/ca_forward',
              sequence_length=100,
              mini_batch_size=100,
              learning_rate=20,
              patience=10,
              max_epochs=5,
              checkpoint=True)
