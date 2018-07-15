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

- PARTIE_PP (include first name unlike Temis)
- PARTIE_PM (not done by Temis)
- AVOCAT (not done by Temis)
- PRESIDENT (not done by Temis)
- CONSEILLER (not done by Temis)
- GREFFIER (not done by Temis)
- ADRESSE

To add:

- phone numbers
- social security numbers
- credit card number
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

- ajout aléatoire de phrase sans offset (5% pour pas fausser si mal parsé) ? utile ?
- randomly remove company type (la société |sasu|sarl)
- randomly remove M Mme Mlle ...
- post process to remove M Mme, [^Et] etc. in offsets

- implement prediction with multi thread (pipe) V2.1 ?
- search for phone number, social security number, etc. 
- train with all matches (?)
- build a dict of common PM (> 100 occurences) and match everywhere against this matcher
- ajout Dr et Prof dans les recherches
- lister les offsets qui contiennent une virgule
- ajouter les rapporteurs
- ajouter les experts (qui font aussi un rapport)



retirer le de/le... a la fin des noms


[('Bâtiment', '', 2), ('G', '', 2), (',', '', 2), ('Porte', '', 2), ('1', '', 2), ('B', '', 2), (',', '', 2), ('appartement', '', 2), ('142', '', 2)]

Entities [('société ESPACE LUMIERE ET SOIN et Mme GUERIN', 'PARTIE_PM')]
Tokens [('Vu', '', 2), ('le', '', 2), ('contredit', '', 2), ('formé', '', 2), ('le', '', 2), ('13', '', 2), ('novembre', '', 2), ('2014', '', 2), ('par', '', 2), ('la', '', 2), ('société', 'PARTIE_PM', 3), ('ESPACE', 'PARTIE_PM', 1), ('LUMIERE', 'PARTIE_PM', 1), ('ET', 'PARTIE_PM', 1), ('SOIN', 'PARTIE_PM', 1), ('et', 'PARTIE_PM', 1), ('Mme', 'PARTIE_PM', 1), ('GUERIN', 'PARTIE_PM', 1), (',', '', 2)]


['MARTIN', 'STUTZ', 'MARTIN', 'MARTIN', 'VIVIE', 'STUTZ']
Entities [('Patrice MARTIN', 'PARTIE_PP'), ('scp Odile STUTZ', 'PARTIE_PM'), ('Patrice MARTIN', 'PARTIE_PP'), ('Patrice MARTIN', 'PARTIE_PP'), ('Bénédicte DE VIVIE DE REGIE', 'PARTIE_PP'), ('Laurent CALBO', 'PARTIE_PP'), ('scp Odile STUTZ et la scp GRANIER DAVID', 'PARTIE_PM')]
Tokens [('Attendu', '', 2), ('que', '', 2), ('par', '', 2), ('jugement', '', 2), ('du', '', 2), ('10', '', 2), ('octobre', '', 2), ('2014', '', 2), (',', '', 2), ('le', '', 2), ('Tribunal', '', 2), ('de', '', 2), ('Grande', '', 2), ('Instance', '', 2), ('de', '', 2), ('MARMANDE', '', 2), ('a', '', 2), ('constaté', '', 2), ("l'", '', 2), ('état', '', 2), ('de', '', 2), ('cessation', '', 2), ('des', '', 2), ('paiements', '', 2), ('de', '', 2), ('Patrice', 'PARTIE_PP', 3), ('MARTIN', 'PARTIE_PP', 1), (',', '', 2), ('fixé', '', 2), ('la', '', 2), ('date', '', 2), ('de', '', 2), ('cessation', '', 2), ('des', '', 2), ('paiements', '', 2), ('à', '', 2), ('ce', '', 2), ('jour', '', 2), (',', '', 2), ('fait', '', 2), ('droit', '', 2), ('à', '', 2), ('la', '', 2), ('demande', '', 2), ('de', '', 2), ('résolution', '', 2), ('du', '', 2), ('plan', '', 2), ('de', '', 2), ('la', '', 2), ('scp', 'PARTIE_PM', 3), ('Odile', 'PARTIE_PM', 1), ('STUTZ', 'PARTIE_PM', 1), ('pour', '', 2), ('défaut', '', 2), ('de', '', 2), ('paiement', '', 2), ('des', '', 2), ('dividendes', '', 2), ('par', '', 2), ('Patrice', 'PARTIE_PP', 3), ('MARTIN', 'PARTIE_PP', 1), (',', '', 2), ('prononcé', '', 2), ("l'", '', 2), ('ouverture', '', 2), ('de', '', 2), ('la', '', 2), ('liquidation', '', 2), ('judiciaire', '', 2), ('des', '', 2), ('biens', '', 2), ('de', '', 2), ('Patrice', 'PARTIE_PP', 3), ('MARTIN', 'PARTIE_PP', 1), (',', '', 2), ('désigné', '', 2), ('Bénédicte', 'PARTIE_PP', 3), ('DE', 'PARTIE_PP', 1), ('VIVIE', 'PARTIE_PP', 1), ('DE', 'PARTIE_PP', 1), ('REGIE', 'PARTIE_PP', 1), (',', '', 2), ('vice', '', 2), ('présidente', '', 2), (',', '', 2), ('en', '', 2), ('qualité', '', 2), ('de', '', 2), ('juge', '', 2), ('commissaire', '', 2), ('titulaire', '', 2), ('et', '', 2), ('Laurent', 'PARTIE_PP', 3), ('CALBO', 'PARTIE_PP', 1), (',', '', 2), ('juge', '', 2), (',', '', 2), ('en', '', 2), ('qualité', '', 2), ('de', '', 2), ('juge', '', 2), ('commissaire', '', 2), ('suppléant', '', 2), (',', '', 2), ('désigné', '', 2), ('en', '', 2), ('qualité', '', 2), ('de', '', 2), ('mandataire', '', 2), ('judiciaire', '', 2), ('à', '', 2), ('la', '', 2), ('liquidation', '', 2), ('la', '', 2), ('scp', 'PARTIE_PM', 3), ('Odile', 'PARTIE_PM', 1), ('STUTZ', 'PARTIE_PM', 1), ('et', 'PARTIE_PM', 1), ('la', 'PARTIE_PM', 1), ('scp', 'PARTIE_PM', 1), ('GRANIER', 'PARTIE_PM', 1), ('DAVID', 'PARTIE_PM', 1), (',', '', 2), ('huissier', '', 2), ('de', '', 2), ('justice', '', 2), (',', '', 2), ('aux', '', 2), ('fins', '', 2), ('de', '', 2), ('réaliser', '', 2), ("l'", '', 2), ('inventaire', '', 2), ('prévu', '', 2), ('aux', '', 2), ('articles', '', 2), ('L', '', 2), ('622', '', 2), ('-', '', 2), ('6', '', 2), ('et', '', 2), ('R', '', 2), ('622', '', 2), ('-', '', 2), ('4', '', 2), ('du', '', 2), ('code', '', 2), ('de', '', 2), ('commerce', '', 2), ('.', '', 2)]
['MARTIN', 'STUTZ']


['DUTEL']
Entities []
Tokens [('I.', '', 2), ('SUR', '', 2), ('LA', '', 2), ('DEMANDE', '', 2), ('PRINCIPALE', '', 2), ('DE', '', 2), ('JOSIANE', '', 2), ('DUTEL', '', 2)]

['BENDJEBOUR']
Entities []
Tokens [('en', '', 2), ('qualité', '', 2), ('de', '', 2), ('représentante', '', 2), ('légale', '', 2), ('de', '', 2), ('BENDJEBOUR', '', 2), ('Riad', '', 2), (',', '', 2), ('né', '', 2), ('le', '', 2), ('15/08/1997', '', 2), ('à', '', 2), ('TOURS', '', 2), ('(', '', 2), ('37', '', 2), (')', '', 2)]


['77400 SAINT THIBAULT DES VIGNES']
Entities []
Tokens [('3ème', '', 2), ('étage', '', 2), ('-', '', 2), ('Appart', '', 2), ('.', '', 2), ('38', '', 2), ('-', '', 2), ('77400', '', 2), ('SAINT', '', 2), ('THIBAULT', '', 2), ('DES', '', 2), ('VIGNES', '', 2)]
['35000 RENNES']
Entities []
Tokens [('19C', '', 2), ('Rue', '', 2), ('de', '', 2), ('Brest', '', 2), ('-', '', 2), ('Appart', '', 2), ('5041', '', 2), ('-', '', 2), ('35000', '', 2), ('RENNES', '', 2)]
['MONTESINOS', 'LARIOS']


Approche liste métiers
retirer président, conseiller, greffier avocat
METIER (Monsieur) XXX
Monsieur XXX, METIER
http://popoblog.o.p.f.unblog.fr/files/2009/12/mtiers.txt
https://www.data.gouv.fr/fr/datasets/repertoire-operationnel-des-metiers-et-des-emplois-rome/#_
https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&ved=0ahUKEwjp7qHV2pvcAhVMvRQKHVQHCB4QFggoMAA&url=https%3A%2F%2Fwww.federation-auto-entrepreneur.fr%2Fsites%2Fdefault%2Ffiles%2Frevue_metiers.xls&usg=AOvVaw0ncXlEx-4Eo6l5kjkwxdcM

('société AUDIBERT et de la société AMT', 'PARTIE_PM')


['Castaing']
Entities []
Tokens [('-', '', 2), ('contre', '', 2), ("l'", '', 2), ('architecte', '', 2), ('Castaing', '', 2), ("d'", '', 2), ('une', '', 2), ('action', '', 2), ('en', '', 2), ('paiement', '', 2), ('de', '', 2), ('diverses', '', 2), ('sommes', '', 2)]


Number of tags: 1773909
Warning: Unnamed vectors -- this won't allow multiple vectors models to be loaded. (Shape: (0, 0))
  0%|          | 0/145040.8 [00:00<?, ?it/s]
Iter 1
 10%|▉         | 14504/145040.8 [2:09:49<18:59:21,  1.91it/s]{'ner': 57.427544362485946}

Iter 2
 20%|██        | 29009/145040.8 [4:18:30<17:04:46,  1.89it/s]{'ner': 36.54777899100043}

Iter 3
 30%|███       | 43515/145040.8 [6:27:13<11:37:35,  2.43it/s]{'ner': 32.62351346588014}

Iter 4
 40%|████      | 58019/145040.8 [8:39:24<15:51:11,  1.52it/s]{'ner': 30.822936655417266}

Iter 5
 50%|█████     | 72525/145040.8 [10:52:50<9:14:25,  2.18it/s] {'ner': 29.70916408157069}

Iter 6
 60%|██████    | 87029/145040.8 [13:06:14<8:45:25,  1.84it/s]{'ner': 28.97088341355564}

Iter 7
 70%|███████   | 101534/145040.8 [15:19:42<6:31:44,  1.85it/s]{'ner': 28.445833063707028}

Iter 8
 80%|████████  | 116039/145040.8 [17:33:06<4:28:08,  1.80it/s]{'ner': 27.971498231318378}

Iter 9
 90%|█████████ | 130544/145040.8 [19:46:28<2:23:44,  1.68it/s]{'ner': 27.52150698761693}




A épouse B
Entities X ['CAMMAS', 'LUC']
Entities S [('Françoise CAMMAS', 'PARTIE_PP')]
Tokens [('Françoise', 'PARTIE_PP', 3), ('CAMMAS', 'PARTIE_PP', 1), ('épouse', '', 2), ('LUC', '', 2)]


Supprimer les doublons


# Extension
Représenté et assisté par Me FABIEn MANOURY, avocat au barreau de GRASSE
29|34
last_document_texts = ["Représenté et assisté par Me FABIEn MANOURY, avocat au barreau de GRASSE"]
last_document_offsets = [[(29, 34, "AVOCAT")]]


Représenté et assisté par Me ROMAIN CHERFILS de la SELARL BOULAN CHERFILS IMPERATORE, avocat au barreau d'AIX EN PROVENCE
29|39
