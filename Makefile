SHELL:=/bin/bash

# avoid collision with a file having the same name as a command listed here
.PHONY: setup train spacy_entities temis_entities display_errors test

VIRT_ENV_FOLDER = ~/.virtualenvs/workspace/anonymisation/venv
SOURCE_VIRT_ENV = source $(VIRT_ENV_FOLDER)/bin/activate

setup:
	( \
	pip3 install virtualenv; \
	virtualenv $(VIRT_ENV_FOLDER); \
	pip3 install -r requirements.txt; \
	)

train:
	( \
	$(SOURCE_VIRT_ENV); \
	python3 train.py; \
	)

spacy_entities:
	( \
	$(SOURCE_VIRT_ENV); \
	python3 entities_viewer_spacy.py; \
	)

temis_entities:
	( \
	$(SOURCE_VIRT_ENV); \
	python3 entities_viewer_temis.py; \
	)

display_errors:
	( \
	$(SOURCE_VIRT_ENV); \
	python3 display_errors.py; \
	)

test:
	( \
	$(SOURCE_VIRT_ENV); \
	pytest; \
	)
