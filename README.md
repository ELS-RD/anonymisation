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

Main NER algorithm is from [Spacy](https://spacy.io/) library and is best described in this [video](https://www.youtube.com/watch?v=sqDHBH9IjRU).
  
Basically it is a **CNN + HashingTrick / Bloom filter + L2S** approach over it.

Advantages:
- no feature extraction (but suffix and prefix, 3 letters each, and the word shape)
- quite rapid on CPU (for Lambda deployment)
- works end to end without many dependencies

Project is done in Python and can't be rewrite in something else because Spacy only exists in Python.

Other approaches (LSTM, etc.) may have shown slightly better performance but are much slower to learn and for inference.

Configuration is done through **resources/config.ini** file

### TODO:

- ajout aléatoire de phrase sans offset (5% pour pas fausser si mal parsé)
- randomly remove company type (la société)

- implement prediction with multi thread (pipe)
- search for phone number, social security number, etc. 
- train with all matches (?)
- build a dict of common PM (> 100 occurences) and match everywhere against this matcher
- ajout Dr et Prof dans les recherches
- lister les offsets qui contiennent une virgule
- ajouter les rapporteurs


https://github.com/dominictarr/random-name/blob/master/first-names.txt


Entities [('Daniel TROUVE', 'PARTIE_PP'), ('Nathalie CAILHETON', 'GREFFIER')]
Tokens [('Prononcé', '', 2), ('par', '', 2), ('mise', '', 2), ('à', '', 2), ('disposition', '', 2), ('au', '', 2), ('greffe', '', 2), ('conformément', '', 2), ('au', '', 2), ('second', '', 2), ('alinéa', '', 2), ('des', '', 2), ('articles', '', 2), ('450', '', 2), ('et', '', 2), ('453', '', 2), ('du', '', 2), ('code', '', 2), ('de', '', 2), ('procédure', '', 2), ('civile', '', 2), ('le', '', 2), ('deux', '', 2), ('Février', '', 2), ('deux', '', 2), ('mille', '', 2), ('quinze', '', 2), (',', '', 2), ('par', '', 2), ('Daniel', 'PARTIE_PP', 3), ('TROUVE', 'PARTIE_PP', 1), (',', '', 2), ('premier', '', 2), ('président', '', 2), (',', '', 2), ('assisté', '', 2), ('de', '', 2), ('Nathalie', 'GREFFIER', 3), ('CAILHETON', 'GREFFIER', 1), (',', '', 2), ('greffier', '', 2), (',', '', 2)]

Entities [('WOLF', 'PARTIE_PP')]
Tokens [('Mme', '', 2), ('WOLF', 'PARTIE_PP', 3), (',', '', 2), ('Conseiller', '', 2)]


Entities [('FABREGUETTES', 'PARTIE_PP')]
Tokens [('Mme', '', 2), ('FABREGUETTES', 'PARTIE_PP', 3), (',', '', 2), ('Conseiller', '', 2)]


Si pattern, appliquer dico
pattern Prénom (né) le XX/YY
- Ilona le 16 avril 2004 à Grenoble (38),
•   Eugène né le 23 mars 1997 à Grenoble ( 38
- Vanessa née le 1er octobre 1987 a TOULON (Var),

