# Pseudo-anonymization of French legal cases

[![Build Status](https://travis-ci.com/ELS-RD/anonymisation.svg?token=9BHyni1rDpKLxVsHDRNp&branch=master)](https://travis-ci.com/ELS-RD/anonymisation)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Scope

Build `Named Entity Recognition` (`NER`) training dataset and learn a model dedicated to French legal case anonymization by leveraging pre-trained language models.    
The projects goes above the scope covered by our previous rule based system which was limited to address and natural person names (this rule based system was used by most legal actors in France).  
This model can be used in a pseudo-anonymization system.  

Measures computed over manually annotated data show strong performance, in particular on natural person and legal professionals names.  

The only French legal cases massively acquired by `Lefebvre Sarrut` not pseudo-anonymized are those from appeal courts (Jurica database).  
The input data are manually annotated data by `Lefebvre Sarrut` employees.  

The project is focused on finding mentions of entities and guessing their types.  
It doesn't manage the pseudo-anonymization step, meaning replacing entities found in precedent step by another representation.  

# Evolution

Previous version of the project in 2018 was based on Spacy library.  
In 2019, new pre-trained language models appeared and provided a much butter quality than what Spacy delivered.  
Current project is now based on Flair.    

If you want more information about the project, check these articles:

* [Why we switched from Spacy to Flair to anonymize French case law](https://towardsdatascience.com/why-we-switched-from-spacy-to-flair-to-anonymize-french-legal-cases-e7588566825f?source=friends_link&sk=de15a2550de1141865329fd37ef793b3)
* [NER algo benchmark: spaCy, Flair, m-BERT and camemBERT on anonymizing French commercial legal cases](https://towardsdatascience.com/benchmark-ner-algorithm-d4ab01b2d4c3?source=friends_link&sk=5bffa2cb19997d1658479f18ce8cf6bb)

## Commands to use the code

This project uses [Python virtual environment](https://virtualenv.pypa.io/en/stable/) to manage dependencies without interfering with those used by the machine.  
`pip3` and `python3` are the only requirements.  
To setup a virtual environment on the machine, install `virtualenv` from `pip3` and install the project dependencies (from the `requirements.txt` file).  

These steps are scripted in the `Makefile` (tested only on `Ubuntu`) and can be performed with the following command:  

```bash
make setup
```

> Variable `VIRT_ENV_FOLDER` can be changed in the `Makefile` to change where to install `Python` dependencies.

... then you can use the project by running one of the following actions:

All commands can be found in the `Makefile`.

## Setup Pycharm

For tests run from Pycharm, you need to create a Pytest test task.    
Then the working folder by default (implicit) is the test folder.  
**It has to be setup as the project root folder explicitly.**

## License

This project is licensed under Apache 2.0 License (found in the LICENSE file in the root directory).
