# required by (\ SHELL COMMANDS \)
SHELL:=/bin/bash

# avoid collision with a file having the same name as a command listed here
.PHONY: setup train show_spacy_entities show_rule_based_entities list_differences test

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

show_rule_based_entities:
# launch a server to display entities found by rule based system
	( \
	$(SOURCE_VIRT_ENV); \
	python3 entities_viewer_rule_based.py; \
	)

list_differences:
# print differences between entities found by Spacy and rule based system
	( \
	$(SOURCE_VIRT_ENV); \
	python3 display_errors.py; \
	)

fine_tune:
# print differences between entities found by Spacy and rule based system
	( \
	$(SOURCE_VIRT_ENV); \
	python fine_tune_pre_trained_model.py -i ../case_annotation/data/tc/spacy_manual_annotations -s 0.2 -e 50; \
	)

test:
# run unit tests
	( \
	$(SOURCE_VIRT_ENV); \
	pytest; \
	)

extract_com:
	( \
	$(SOURCE_VIRT_ENV); \
	python entities_sample_extractor.py -i ./resources/doc_courts/tc_6_tesseract_selection -o ./resources/doc_courts/spacy_tc_6_tesseract_selection -m ./resources/model -k 200; \
	)


extract_ca:
	( \
	$(SOURCE_VIRT_ENV); \
	python entities_sample_extractor.py -i ./resources/training_data -o ../case_annotation/data_spacy_automatic_annotations -m ./resources/model -k 200; \
	)
