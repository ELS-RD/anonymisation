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
- MAGISTRAT (not done by Temis)
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

- Use a dict + TRIE to find les MAGISTRATS, GREFFIERS, PM
- ajout aléatoire de phrase sans offset (5% pour pas fausser si mal parsé) ? utile ?

- implement prediction with multi thread (pipe) V2.1 ?
- search for phone number, social security number, etc. 
- train with all matches (?)
- build a dict of common PM (> 100 occurences) and match everywhere against this matcher
- ajout Dr et Prof dans les recherches
- ajouter les rapporteurs
- ajouter les experts (qui font aussi un rapport)



retirer le de/le... a la fin des noms




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

--------------
Number of tags: 1775635
Warning: Unnamed vectors -- this won't allow multiple vectors models to be loaded. (Shape: (0, 0))

Iter 1
 50%|█████     | 14382/28763.26 [2:04:41<1:49:30,  2.19it/s]{'ner': 59.536253356406405}

Iter 2
100%|█████████▉| 28763/28763.26 [4:10:13<00:00,  1.89it/s]{'ner': 39.26536671542931}
28764it [4:10:13,  2.14it/s]        
-------------------
Number of tags: 1789948
Warning: Unnamed vectors -- this won't allow multiple vectors models to be loaded. (Shape: (0, 0))

Iter 1
 25%|██▍       | 14454/57816.04 [2:06:59<6:06:57,  1.97it/s]{'ner': 67.71795046884715}

Iter 2
 50%|█████     | 28909/57816.04 [4:13:19<4:05:11,  1.96it/s]{'ner': 46.69826582446979}

Iter 3
 75%|███████▌  | 43365/57816.04 [6:19:56<1:36:55,  2.49it/s]{'ner': 42.69678843677113}

Iter 4
57819it [8:29:44,  1.85it/s]{'ner': 40.70850695853477}
57820it [8:29:44,  2.42it/s]
----------------------
Expert judiciaire


-----
Mettre en place des regles pour attraper toutes les mentions repérées par le NER
-> comment les ajouter aux résultats ?
------
Trouver les adresses des parties avec certitude
------
Nom du tribunal + chambre
Date de l'arrêt
RG
------
date de naissance
-------
Tiret dans les noms d avocats
 Me Carine Chevalier - Kasprzak ...
-------
Noms qui commencent par [de MAJ...]

