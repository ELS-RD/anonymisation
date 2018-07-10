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

- ajout fonction pour lister les phrases sans offset pour repérer des erreurs
- ajout fonction pour comparer les résultats entre Themis et Spacy sur les PP
- ajout aléatoire de phrase sans offset (5% pour pas fausser si mal parsé)
- add first name to dictionary
- randomly remove company type (la société)
- implement prediction with multi thread (pipe)
- search for phone number, social security number, etc. 
- train with all matches
- build a dict of PM and match everywhere against this matcher
- replace spacy matcher by generic TRI function (https://github.com/pytries/marisa-trie)
- ajout Dr et Prof dans les recherches
- lister les offsets qui contiennent une virgule

Entities [('Nathalie CAILHETON', 'GREFFIER'), ('Aurore BLUM, conseiller', 'GREFFIER')]
Tokens [('a', '', 2), ('rendu', '', 2), ("l'", '', 2), ('arrêt', '', 2), ('contradictoire', '', 2), ('suivant', '', 2), ('.', '', 2), ('La', '', 2), ('cause', '', 2), ('a', '', 2), ('été', '', 2), ('débattue', '', 2), ('et', '', 2), ('plaidée', '', 2), ('en', '', 2), ('audience', '', 2), ('publique', '', 2), (',', '', 2), ('le', '', 2), ('15', '', 2), ('Décembre', '', 2), ('2014', '', 2), ('sans', '', 2), ('opposition', '', 2), ('des', '', 2), ('parties', '', 2), (',', '', 2), ('devant', '', 2), ('Aurore', '', 2), ('BLUM', '', 2), (',', '', 2), ('conseiller', '', 2), ('faisant', '', 2), ('fonction', '', 2), ('de', '', 2), ('président', '', 2), (',', '', 2), ('rapporteur', '', 2), (',', '', 2), ('assistée', '', 2), ('de', '', 2), ('Nathalie', 'GREFFIER', 3), ('CAILHETON', 'GREFFIER', 1), (',', '', 2), ('greffier', '', 2), ('.', '', 2), ('Aurore', 'GREFFIER', 3), ('BLUM', 'GREFFIER', 1), (',', 'GREFFIER', 1), ('conseiller', 'GREFFIER', 1), (',', '', 2), ('rapporteur', '', 2), (',', '', 2), ('en', '', 2), ('a', '', 2), (',', '', 2), ('dans', '', 2), ('son', '', 2), ('délibéré', '', 2), (',', '', 2), ('rendu', '', 2), ('compte', '', 2), ('à', '', 2), ('la', '', 2), ('cour', '', 2), ('composée', '', 2), (',', '', 2), ('outre', '', 2), ('elle', '', 2), ('même', '', 2), (',', '', 2), ('de', '', 2), ('Daniel', '', 2), ('TROUVE', '', 2), (',', '', 2), ('premier', '', 2), ('président', '', 2), (',', '', 2), ('et', '', 2), ('Frédérique', '', 2), ('GAYSSOT', '', 2), (',', '', 2), ('conseiller', '', 2), (',', '', 2), ('en', '', 2), ('application', '', 2), ('des', '', 2), ('dispositions', '', 2), ('des', '', 2), ('articles', '', 2), ('945', '', 2), ('-', '', 2), ('1', '', 2), ('et', '', 2), ('786', '', 2), ('du', '', 2), ('code', '', 2), ('de', '', 2), ('procédure', '', 2), ('civile', '', 2), (',', '', 2), ('et', '', 2), ("qu'", '', 2), ('il', '', 2), ('en', '', 2), ('ait', '', 2), ('été', '', 2), ('délibéré', '', 2), ('par', '', 2), ('les', '', 2), ('magistrats', '', 2), ('ci', '', 2), ('dessus', '', 2), ('nommés', '', 2), (',', '', 2), ('les', '', 2), ('parties', '', 2), ('ayant', '', 2), ('été', '', 2), ('avisées', '', 2), ('par', '', 2), ('le', '', 2), ('président', '', 2), (',', '', 2), ('à', '', 2), ("l'", '', 2), ('issue', '', 2), ('des', '', 2), ('débats', '', 2), (',', '', 2), ('que', '', 2), ("l'", '', 2), ('arrêt', '', 2), ('serait', '', 2), ('prononcé', '', 2), ('par', '', 2), ('sa', '', 2), ('mise', '', 2), ('à', '', 2), ('disposition', '', 2), ('au', '', 2), ('greffe', '', 2), ('à', '', 2), ('la', '', 2), ('date', '', 2), ("qu'", '', 2), ('il', '', 2), ('indique', '', 2), ('.', '', 2)]


Entities [('Vincent THOMAS, SCP PGTA', 'AVOCAT')]
Tokens [('Représenté', '', 2), ('par', '', 2), ('Me', '', 2), ('Vincent', 'AVOCAT', 3), ('THOMAS', 'AVOCAT', 1), (',', 'AVOCAT', 1), ('SCP', 'AVOCAT', 1), ('PGTA', 'AVOCAT', 1), (',', '', 2), ('avocat', '', 2), ('inscrit', '', 2), ('au', '', 2), ('barreau', '', 2), ('du', '', 2), ('GERS', '', 2)]

