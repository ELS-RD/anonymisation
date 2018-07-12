from generate_trainset.extract_header_values import parse_xml_header
from resources.config_provider import get_config_default


def test_header_parser():
    config_training = get_config_default()
    xml_path = config_training["xml_unittest_file"]
    header_content = parse_xml_header(path=xml_path)
    assert len(header_content) == 1
    assert header_content['CA-aix-en-provence-20130208-1022871-jurica']['defendeur_fullname'] == ['Catherine ***REMOVED***']
