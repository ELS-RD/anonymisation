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
	python flair_train.py --input-files-dir ../case_annotation/data/tc/spacy_manual_annotations \
	--model-dir resources/flair_ner/tc \
	--dev-set-size 0.2 \
	--epochs 40; \
	)

# display prediction errors
.PHONY: flair_display_errors_tc
flair_display_errors_tc:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_display_errors.py --input-files-dir ../case_annotation/data/tc/spacy_manual_annotations \
	--model-dir resources/flair_ner/tc \
	--dev-set-size 0.2; \
	)

# train a model from manual annotations
.PHONY: flair_train_ca
flair_train_ca:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_train.py --input-files-dir ../case_annotation/data/appeal_court/spacy_manual_annotations \
	--model-dir resources/flair_ner/ca \
	--dev-set-size 0.2 \
	--epochs 100; \
	)

# display prediction errors
.PHONY: flair_display_errors_ca
flair_display_errors_ca:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_display_errors.py --input-files-dir ../case_annotation/data/appeal_court/spacy_manual_annotations \
	--model-dir resources/flair_ner/ca \
	--dev-set-size 0.2; \
	)

# display prediction errors
.PHONY: flair_generate_html_ca
flair_generate_html_ca:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_generate_html.py --input-files-dir resources/training_data \
	--model-dir resources/flair_ner/ca \
	--dev-set-size 2000; \
	)

# train a model from generated annotations
.PHONY: flair_train_lux
flair_train_lux:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_train.py --input-files-dir ../case_annotation/data/lux/spacy_manual_annotations \
	--model-dir resources/flair_ner/luxano_segment_0 \
	--epochs 40 \
	--nb_segment 5 \
	--segment 0; \
	)

# display prediction errors
.PHONY: flair_display_errors_lux
flair_display_errors_lux:
	date
	( \
	$(SOURCE_VIRT_ENV); \
	python flair_display_errors.py \
	--input-files-dir ../case_annotation/data/lux/spacy_manual_annotations \
	--model-dir resources/flair_ner/luxano_segment_0 \
	--nb_segment 5 \
	--segment 0; \
	)

# run unit tests
.PHONY: test
test:
	( \
	$(SOURCE_VIRT_ENV); \
	pytest tests; \
	)


# apply formating rule
.PHONY: source_code_format
source_code_format:
	black --line-length 121 --target-version py37 tests misc ner xml_extractions ./*.py
	isort --src tests misc ner xml_extractions ./*.py

# check that formating rule is respected
.PHONY: source_code_check_format
source_code_check_format:
	black --check --line-length 121 --target-version py37 tests misc ner xml_extractions ./*.py
	isort --check-only --src tests misc ner xml_extractions ./*.py
	flake8 tests misc ner xml_extractions ./*.py
