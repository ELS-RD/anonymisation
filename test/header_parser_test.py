from xml_parser.extract_header_values import parse_xml_header
import os


def test_header_parser():
    path = "./resources/test/test.xml"
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/" + path
    print(dir_path)
    result = parse_xml_header(path)
    assert len(result) == 1
    assert result['CA-aix-en-provence-20130208-1022871-jurica']['defendeur_fullname'] == ['Catherine ***REMOVED***']