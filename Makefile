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

# required by (\ SHELL COMMANDS \)
SHELL:=/bin/sh

# avoid collision with a file having the same name as a command listed here
.PHONY: setup train show_spacy_entities show_rule_based_entities list_differences test

VIRT_ENV_FOLDER = ~/.local/share/virtualenvs/anonymisation
SOURCE_VIRT_ENV = . $(VIRT_ENV_FOLDER)/bin/activate

.PHONY: setup
setup:
# setup the virtualenv required by the project
	( \
	mkdir -p $(VIRT_ENV_FOLDER); \
	sudo pip3 install virtualenv --upgrade; \
	virtualenv $(VIRT_ENV_FOLDER); \
	$(SOURCE_VIRT_ENV); \
	pip3 install -r requirements.txt; \
	)

.PHONY: train
train:
# launch model training
	( \
	$(SOURCE_VIRT_ENV); \
	python3 train.py train_data_set; \
	)

.PHONY: export_frequent_entities
export_frequent_entities:
# export the dataset to be used in a second pass, like for freq entities finding
	( \
	$(SOURCE_VIRT_ENV); \
	python3 spacy_train.py export_dataset; \
	)

.PHONY: display_dataset
display_dataset:
# display generated training set (for debug purpose)
	( \
	$(SOURCE_VIRT_ENV); \
	python3 train.py; \
	)

.PHONY: show_spacy_entities
show_spacy_entities:
# launch a server to display entities found by Spacy
	( \
	$(SOURCE_VIRT_ENV); \
	python3 spacy_generate_html.py; \
	)

.PHONY: show_rule_based_entities
show_rule_based_entities:
# launch a server to display entities found by rule based system
	( \
	$(SOURCE_VIRT_ENV); \
	python3 rule_based_generate_html.py; \
	)

.PHONY: list_differences
list_differences:
# print differences between entities found by Spacy and rule based system
	( \
	$(SOURCE_VIRT_ENV); \
	python3 temis_display_errors.py; \
	)

.PHONY: spacy_fine_tune_tc
spacy_fine_tune_tc:
# train a model from manual annotations
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python spacy_fine_tune.py -i ../case_annotation/data/tc/spacy_manual_annotations -s 0.2 -e 3; \
	)

.PHONY: flair_train_tc
flair_train_tc:
# train a model from manual annotations
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_train.py -i ../case_annotation/data/tc/spacy_manual_annotations -m resources/flair_ner/tc -s 0.2 -e 40; \
	)

.PHONY: flair_display_errors_tc
flair_display_errors_tc:
# display prediction errors
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_display_errors.py -i ../case_annotation/data/tc/spacy_manual_annotations -m resources/flair_ner/tc -s 0.2; \
	)

.PHONY: spacy_fine_tune_ca
spacy_fine_tune_ca:
# train a model from manual annotations
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python spacy_fine_tune.py -i ../case_annotation/data/appeal_court/spacy_manual_annotations  -s 0.2 -e 20 -m ./resources/model -o ./resources/new_model; \
	)

.PHONY: flair_train_ca
flair_train_ca:
# train a model from manual annotations
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_train.py -i ../case_annotation/data/appeal_court/spacy_manual_annotations -m resources/flair_ner/ca -s 0.2 -e 100; \
	)

.PHONY: flair_display_errors_ca
flair_display_errors_ca:
# display prediction errors
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_display_errors.py -i ../case_annotation/data/appeal_court/spacy_manual_annotations -m resources/flair_ner/ca -s 0.2; \
	)

.PHONY: flair_generate_html_ca
flair_generate_html_ca:
# display prediction errors
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_generate_html.py -i resources/training_data -m resources/flair_ner/ca -s 2000; \
	)

.PHONY: spacy_fine_tune_lux
spacy_fine_tune_lux:
# train a model from manual annotations
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python spacy_fine_tune.py -i ../luxano/output/trainset -s 0.2 -e 3; \
	)

.PHONY: flair_train_lux
flair_train_lux:
# train a model from generated annotations
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_train.py -i ../luxano/output/trainset -m resources/flair_ner/luxano -s 0.2 -e 40; \
	)

.PHONY: flair_display_errors_lux
flair_display_errors_lux:
# display prediction errors
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_display_errors.py -i ../luxano/output/trainset -m resources/flair_ner/luxano -s 0.2; \
	)

.PHONY: test
test:
# run unit tests
	( \
	$(SOURCE_VIRT_ENV); \
	pytest; \
	)

.PHONY: extract_com
extract_com:
	( \
	$(SOURCE_VIRT_ENV); \
	python entities_sample_extractor.py -i ./resources/doc_courts/tc_6_tesseract_selection -o ./resources/doc_courts/spacy_tc_6_tesseract_selection -m ./resources/model -k 200; \
	)

.PHONY: extract_ca
extract_ca:
	( \
	$(SOURCE_VIRT_ENV); \
	python entities_sample_extractor.py -i ./resources/training_data -o ../case_annotation/data_spacy_automatic_annotations -m ./resources/model -k 200; \
	)
