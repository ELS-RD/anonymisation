from xml_parser.extract_node_values import get_paragraph_with_entities, read_xml, get_paragraph_from_file

xml_path = "./resources/test/test.xml"


def test_xml_parser():
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


def test_get_paragraph():
    result_keep_no_annotation = get_paragraph_from_file(path=xml_path, keep_paragraph_without_annotation=True)
    result_keep_with_annotation = get_paragraph_from_file(path=xml_path, keep_paragraph_without_annotation=False)
    assert len(result_keep_no_annotation) == 27
    assert len(result_keep_with_annotation) == 3
