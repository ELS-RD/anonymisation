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

VIRT_ENV_FOLDER = ~/.local/share/virtualenvs/anonymisation
SOURCE_VIRT_ENV = . $(VIRT_ENV_FOLDER)/bin/activate

# setup the virtualenv required by the project
.PHONY: setup
setup:
	( \
	mkdir -p $(VIRT_ENV_FOLDER); \
	sudo pip3 install virtualenv --upgrade; \
	virtualenv $(VIRT_ENV_FOLDER); \
	$(SOURCE_VIRT_ENV); \
	pip3 install -r requirements.txt; \
	)

# train a model from manual annotations
.PHONY: flair_train_tc
flair_train_tc:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_train.py -i ../case_annotation/data/tc/spacy_manual_annotations -m resources/flair_ner/tc -s 0.2 -e 40; \
	)

# display prediction errors
.PHONY: flair_display_errors_tc
flair_display_errors_tc:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_display_errors.py -i ../case_annotation/data/tc/spacy_manual_annotations -m resources/flair_ner/tc -s 0.2; \
	)

# train a model from manual annotations
.PHONY: flair_train_ca
flair_train_ca:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_train.py -i ../case_annotation/data/appeal_court/spacy_manual_annotations -m resources/flair_ner/ca -s 0.2 -e 100; \
	)

# display prediction errors
.PHONY: flair_display_errors_ca
flair_display_errors_ca:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_display_errors.py -i ../case_annotation/data/appeal_court/spacy_manual_annotations -m resources/flair_ner/ca -s 0.2; \
	)

# display prediction errors
.PHONY: flair_generate_html_ca
flair_generate_html_ca:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_generate_html.py -i resources/training_data -m resources/flair_ner/ca -s 2000; \
	)

# train a model from generated annotations
.PHONY: flair_train_lux
flair_train_lux:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_train.py -i ../case_annotation/data/lux/spacy_manual_annotations \
	-m resources/flair_ner/luxano \
	-s 0.2 \
	-e 40; \
	)

# display prediction errors
.PHONY: flair_display_errors_lux
flair_display_errors_lux:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_display_errors.py -i ../case_annotation/data/lux/spacy_manual_annotations -m resources/flair_ner/luxano -s 0.2; \
	)

# run unit tests
.PHONY: test
test:
	( \
	$(SOURCE_VIRT_ENV); \
	pytest; \
	)
