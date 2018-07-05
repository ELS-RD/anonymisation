from xml_parser.extract_node_value import get_paragraph_with_entities, read_xml


def test_parser():
    xml_path = "./resources/test/test.xml"

    tree = read_xml(xml_path)

    # r = tree.xpath('//TexteJuri/P|//MetaJuri/DecisionTraitee/Date|//MetaJuri/DecisionTraitee/Numero')
    r = tree.xpath('//TexteJuri/P')

    for i in r:
        paragraph_text, extracted_text, offset = get_paragraph_with_entities(i)
        if len(extracted_text) > 0:
            item_text = extracted_text[0]
            current_attribute = offset.get('entities')[0]
            start = current_attribute[0]
            end = current_attribute[1]
            assert item_text == paragraph_text[start:end]
