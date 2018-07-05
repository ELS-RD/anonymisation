from xml_parser.extract_node_value import get_paragraph_with_entities, read_xml

xml_path = "./resources/test/test.xml"
# xml_path = "./resources/training_data/CA-2013-sem-06.xml"

tree = read_xml(xml_path)
nodes = tree.xpath('//Juri|//MetaJuri//DecisionTraitee/Numero|//Demandeurs//Texte|//Demandeurs//TexteAnonymise|'
                   '//MetaJuri/Defendeurs//TexteAnonymise|//MetaJuri/Defendeurs//Texte|'
                   '//Greffier|//Avocat|//DecisionTraitee/Date')

cases = dict()

for node in nodes:
    if node.tag == "Juri":
        current_case = dict()
        defendeur_full = list()
        defendeur_hidden = list()
        demandeur_full = list()
        demandeur_hidden = list()
        greffier = list()
        avocat = list()
        conseiller = list()
        president = list()
        numero = list()
        date = list()

        current_case['defendeur_fullname'] = defendeur_full
        current_case['defendeur_hidden'] = defendeur_hidden
        current_case['demandeur_fullname'] = demandeur_full
        current_case['demandeur_hidden'] = demandeur_hidden
        current_case['avocat'] = avocat
        current_case['president'] = president
        current_case['conseiller'] = conseiller
        current_case['greffier'] = greffier
        current_case['numero'] = numero
        current_case['date'] = date

        cases[node.get("id")] = current_case

    if node.tag == "Numero":
        numero.append(node.text)
    if node.tag == "Date":
        date.append(node.text)
    if ("Defendeurs" in tree.getpath(node)):
        if (node.tag == "Texte"):
            defendeur_full.append(node.text)
        if (node.tag == "TexteAnonymise"):
            defendeur_hidden.append(node.text)
    if ("Demandeurs" in tree.getpath(node)):
        if (node.tag == "Texte"):
            demandeur_full.append(node.text)
        if (node.tag == "TexteAnonymise"):
            demandeur_hidden.append(node.text)
    if node.tag == "Greffier":
        greffier.append(node.text)
    if node.tag == "Avocat":
        avocat.append(node.text)
    if node.tag == "President":
        president.append(node.text)
    if node.tag == "Conseiller":
        conseiller.append(node.text)

print(cases)
