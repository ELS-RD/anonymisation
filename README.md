# NER on legal case

[![Build Status](https://travis-ci.com/ELS-RD/anonymisation.svg?token=9BHyni1rDpKLxVsHDRNp&branch=master)](https://travis-ci.com/ELS-RD/anonymisation)

Purpose of this projet is to apply Named Entity Recognition to extract specific information from legal cases like 
names, RG number, etc.

## Data source

The input are XML files from **Jurica** database.

## Challenge

The main strategy is to generate as many training examples as possible, by:

- using the extractions from Themis
- using some regex
- looking for transformation of names discovered with other strategies (remove first name, remove family name, etc.)
- building dictionaries of names and look for them

## Type of tokens

Main token types searched: 

- PARTIE_PP
- PARTIE_PM
- AVOCAT
- PRESIDENT
- CONSEILLER
- GREFFIER
- ADRESSE

To add:

- phone numbers
- social security numbers
- RG

## Algorithm

Main NER algorithm is from [Spacy ](https://spacy.io/) library and is best described in this [video](https://www.youtube.com/watch?v=sqDHBH9IjRU).
  
Basically it is a **CNN + HashingTrick / Bloom filter + L2S** approach over it.

Advantages:
- no feature extraction (but suffix and prefix, 3 letters each, and the word shape)
- quite rapid on CPU (for Lambda deployment)
- works end to end without many dependencies

Project is done in Python and can't be rewrite in something else because Spacy only exists in Python.

Other approaches (LSTM, etc.) may have shown slightly better performance but are much slower to learn and for inference.

Configuration is done through **resources/config.ini** file

### TODO:

- priorities between tags
- implement prediction with multi thread (pipe)
- search for phone number, social security number, etc. 
- train with all matches
- build a dict of PM and match everywhere against this matcher
- replace spacy matcher by generic TRI function (https://github.com/pytries/marisa-trie)
- look for president, lawyer by regex (lawyer -> Maitre|Me.)



Magistrat
Président ... Magistrat
Président ... Cour
Conseiller ... Président(e)
Conseiller ... Cour
Président ... chambre
substitut général


, Greffier


Greffier : ...