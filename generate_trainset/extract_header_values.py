from generate_trainset.common_xml_parser_function import read_xml


def parse_xml_header(path: str):
    """
    Extract some values from Jurica XML headers
    :param path: path to the Jurica XML file
    :return: a dict, 1 slot per legal case, for each slot, there is a dict of list with values
    """
    tree = read_xml(path)
    nodes = tree.xpath('//Juri|//MetaJuri//DecisionTraitee/Numero|//Demandeurs//Texte|//Demandeurs//TexteAnonymise|'
                       '//MetaJuri/Defendeurs//TexteAnonymise|//MetaJuri/Defendeurs//Texte|'
                       '//Greffier|//Avocat|//DecisionTraitee/Date')

    headers_content = dict()

    for node in nodes:
        if node.tag == "Juri":
            # init empty mutable list
            # in following steps, these lists will be updated
            current_case = dict()
            defendeur_full = list()
            defendeur_hidden = list()
            demandeur_full = list()
            demandeur_hidden = list()
            greffier = list()
            avocat = list()
            conseiller = list()
            president = list()
            # need to be a mutable list to get the update
            # in Python str are immutable, so future update would be impossible
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

            headers_content[node.get("id")] = current_case

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

    return headers_content
