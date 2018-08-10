# required by (\ SHELL COMMANDS \)
SHELL:=/bin/bash

# avoid collision with a file having the same name as a command listed here
.PHONY: setup train show_spacy_entities show_temis_entities list_differences test

VIRT_ENV_FOLDER = ~/.local/share/virtualenvs/anonymisation/venv
SOURCE_VIRT_ENV = source $(VIRT_ENV_FOLDER)/bin/activate

setup:
# setup the virtualenv required by the project
	( \
	mkdir -p $(VIRT_ENV_FOLDER); \
	sudo pip3 install virtualenv --upgrade; \
	virtualenv $(VIRT_ENV_FOLDER); \
	$(SOURCE_VIRT_ENV); \
	pip3 install -r requirements.txt; \
	)

train:
# launch model training
	( \
	$(SOURCE_VIRT_ENV); \
	python3 train.py train_data_set; \
	)

export_frequent_entities:
# export the dataset to be used in a second pass, like for freq entities finding
	( \
	$(SOURCE_VIRT_ENV); \
	python3 train.py export_dataset; \
	)

display_dataset:
# display generated training set (for debug purpose)
	( \
	$(SOURCE_VIRT_ENV); \
	python3 train.py; \
	)

show_spacy_entities:
# launch a server to display entities found by Spacy
	( \
	$(SOURCE_VIRT_ENV); \
	python3 entities_viewer_spacy.py; \
	)

show_temis_entities:
# launch a server to display entities found by Temis
	( \
	$(SOURCE_VIRT_ENV); \
	python3 entities_viewer_temis.py; \
	)

list_differences:
# print differences between entities found by Spacy and Temis
	( \
	$(SOURCE_VIRT_ENV); \
	python3 display_errors.py; \
	)

test:
# run unit tests
	( \
	$(SOURCE_VIRT_ENV); \
	pytest; \
	)
