# this is experimental code

import spacy

from textacy import extract, keyterms
from textacy.keyterms import aggregate_term_variants

nlp = spacy.load('fr_core_news_md')
text = """Aux termes de l'article premier du décret n° 97-1065 du 20 novembre 1997, «la commission paritaire des 
publications et agences de presse est chargée de donner un avis sur l'application aux journaux et écrits périodiques 
des textes législatifs ou réglementaires prévoyant des allégements en faveur de la presse en matière de taxes 
fiscales et de tarifs postaux. Elle est également chargée de faire des propositions pour l'inscription sur la liste 
des organismes constituant des agences de presse au sens de l'ordonnance du 2 novembre 1945. Elle est enfin chargée 
de la reconnaissance des services de presse en ligne, au sens de l'article 1er de la loi n° 86-897 du 1er août 1986 
portant réforme du régime juridique de la presse». Les éditeurs de périodiques, qui désirent obtenir le bénéfice du 
taux particulier, doivent adresser une demande en ce sens au secrétariat général de la commission paritaire des 
publications et agences de presse qui est assuré par la Direction générale des médias et des industries culturelles 
relevant du ministre chargé de la communication. La commission examine si la publication remplit les conditions 
prévues par les articles 72 et 73 de l'annexe III du CGI et formule son avis. Dans l'affirmative, elle délivre un 
certificat d'inscription qui doit être produit à l'appui de toute demande tendant à obtenir le bénéfice du taux 
particulier. Un avis négatif doit être motivé."""

doc = nlp(text)

print([nc.text.strip() for nc in extract.noun_chunks(doc, drop_determiners=True)])

print([', '.join(item.text for item in triple) for triple in extract.subject_verb_object_triples(doc)])

print([term for term, _ in keyterms.textrank(doc, normalize='lower', n_keyterms=5)])

print([term for term, _ in keyterms.sgrank(doc, normalize='lower', ngrams=(1, 2, 3), n_keyterms=5)])

print([term for term, _ in keyterms.singlerank(doc)])

aggregate_term_variants({"Benesty", "Monsieur Benesty", "Michael Benesty", "Jessica Benesty"})
