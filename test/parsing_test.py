from xml_parser.xml_parser import get_paragraph_text, read_xml


def test_parser():
    xml_path = "../data/xml_legal_case_exemple/CA-2013-sem-06.xml"
    tree = read_xml(xml_path)

    # r = tree.xpath('//TexteJuri/P|//MetaJuri/DecisionTraitee/Date|//MetaJuri/DecisionTraitee/Numero')
    r = tree.xpath('//TexteJuri/P')

    for i in r:
        paragraph_text, extracted_text, offset = get_paragraph_text(i)
        if len(extracted_text) > 0:
            item_text = extracted_text[0]
            current_attribute = offset.get('entities')[0]
            start = current_attribute[0]
            end = current_attribute[1]
            assert item_text == paragraph_text[start:end]
