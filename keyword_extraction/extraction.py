# this is experimental code
# requires to download Spacy French trained model

import spacy

from textacy import extract, keyterms
from textacy.keyterms import aggregate_term_variants
from spacy_lefff import LefffLemmatizer, POSTagger

nlp = spacy.load('fr_core_news_md')
pos = POSTagger()
nlp.add_pipe(pos, name='pos', after='parser')
french_lemmatizer = LefffLemmatizer(after_melt=True)
nlp.add_pipe(french_lemmatizer, name='lefff', after='pos')
text = """Par la décision Ministre de l'agriculture c/ Dame Lamotte, le Conseil d'État juge qu'il existe un principe général du droit selon lequel toute décision administrative peut faire l'objet, même sans texte, d'un recours pour excès de pouvoir.
La loi du 17 août 1940 avait donné aux préfets le pouvoir de concéder à des tiers les exploitations abandonnées ou incultes depuis plus de deux ans aux fins de mise en culture immédiate. C'est en application de cette loi que, par deux fois sans compter un arrêté de réquisition, les terres de la dame Lamotte avaient fait l'objet d'un arrêté préfectoral de concession. Le Conseil d'État avait annulé à chaque fois ces décisions. Par un arrêté du 10 août 1944, le préfet de l'Ain avait de nouveau concédé les terres en cause. Mais une loi du 23 mai 1943, dont le but manifeste était de contourner la résistance des juges à l'application de la loi de 1940, avait prévu que l'octroi de la concession ne pouvait "faire l'objet d'aucun recours administratif ou judiciaire". Sur le fondement de cette disposition, le juge administratif aurait dû déclarer le quatrième recours de la dame Lamotte irrecevable.
Le Conseil d'État ne retint pas cette solution en estimant, aux termes d'un raisonnement très audacieux mais incontestablement indispensable pour protéger les administrés contre l'arbitraire de l'État, qu'il existe un principe général du droit selon lequel toute décision administrative peut faire l'objet, même sans texte, d'un recours pour excès de pouvoir et que la disposition de la loi du 23 mai 1943, faute de l'avoir précisé expressément, n'avait pas pu avoir pour effet d'exclure ce recours. Le même raisonnement prévaut s'agissant du droit au recours en cassation (CE, ass., 7 février 1947, d'Aillières, p. 50).
En application de cette jurisprudence, confirmée à plusieurs reprises, le pouvoir réglementaire ne peut jamais interdire le recours pour excès de pouvoir contre les décisions qu'il prend. Certes, en principe, le législateur, s'il le précisait, pourrait interdire le recours pour excès de pouvoir contre certaines décisions. Mais, dans le contexte normatif actuel, une telle disposition se heurterait sans doute aux stipulations du droit international relatives aux droits des individus à exercer un recours effectif contre les décisions administratives. La Cour de justice des communautés européennes en a fait un principe général du droit communautaire (15 mai 1986, Johnston, n°222/84, p. 1651) et l'article 13 de la Convention européenne de sauvegarde des droits de l'homme et des libertés fondamentales prévoit le droit à un recours effectif pour toute personne dont les droits et libertés reconnus dans la Convention auraient été méconnus. Elle serait également et surtout contraire aux normes et principes de valeur constitutionnelle puisque, dans une décision du 21 janvier 1994 (93-335 DC, p. 40), confirmée par une décision du 9 avril 1996 (96-373 DC), le Conseil constitutionnel a rattaché le droit des individus à un recours effectif devant une juridiction en cas d'atteintes substantielles à leurs droits à l'article 16 de la Déclaration des droits de l'homme et du citoyen qui fait partie du bloc de constitutionnalité."""

doc = nlp(text.replace("\n", " "))

lemma_doc = [d.lemma_ for d in doc]
lemma_doc = ' '.join(lemma_doc)
print(lemma_doc)
nlp2 = spacy.load('fr_core_news_md')
lemma_doc = nlp2(lemma_doc)


print([term for term, _ in keyterms.textrank(lemma_doc, normalize='lower', n_keyterms=5)])

print([term for term, _ in keyterms.sgrank(lemma_doc, normalize='lower', ngrams=(1, 2, 3), n_keyterms=5)])

print([term for term, _ in keyterms.singlerank(lemma_doc, normalize='lower')])

