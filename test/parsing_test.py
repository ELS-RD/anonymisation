from parser.xml_parser import get_paragraph_text, read_xml


def test_parser():
    xml_path = "../data/xml_legal_case_exemple/CA-2013-sem-06.xml"
    tree = read_xml(xml_path)

    # r = tree.xpath('//TexteJuri/P|//MetaJuri/DecisionTraitee/Date|//MetaJuri/DecisionTraitee/Numero')
    r = tree.xpath('//TexteJuri/P')

    for i in r:
        result = get_paragraph_text(i)
        if len(result[1]) > 0:
            current_attribute = result[1][0]
            start = current_attribute[2]
            end = current_attribute[3]
            item_text = current_attribute[0]
            paragraph_text = result[0]
            assert item_text == paragraph_text[start:end]
