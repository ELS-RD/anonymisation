from match_text.match_header import MatchValuesFromHeaders
from match_text_unsafe.find_header_values import parse_xml_header
from resources.config_provider import get_config_default


def test_match_headers_content():
    config_training = get_config_default()
    xml_path = config_training["xml_unittest_file"]
    header_content_all_cases = parse_xml_header(path=xml_path)
    case_id = list(header_content_all_cases.keys())[0]
    header_content = header_content_all_cases[case_id]
    headers_matcher = MatchValuesFromHeaders(current_header=header_content, threshold_size=3)
    matcher_partie_pp = headers_matcher.get_matcher_of_partie_pp_from_headers()

    text1 = "C'est Catherine ***REMOVED*** qui est responsable de ces faits avec M. LEON ***REMOVED***"

    assert matcher_partie_pp.get_matches(text1, "PERS") == [(6, 22, "PERS")]

    text2 = "Me Touboul s'avance avec Patrice Cipre pendant que la greffière, Mme. Laure Metge, prend des notes"
    # TODO review tests (code is now very strict, does these tests make sense?)
    # matcher_lawyers = headers_matcher.get_matcher_of_lawyers_from_headers()
    # assert get_matches(matcher_lawyers, text2, "LAWYER") == [(3, 10, "LAWYER"),
    #                                                          (25, 32, "LAWYER"),
    #                                                          (25, 38, "LAWYER"),
    #                                                          (33, 38, "LAWYER")]

    # matcher_clerks = headers_matcher.get_matcher_of_clerks_from_headers()
    # assert get_matches(matcher_clerks, text2, "JUDGE_CLERK") == [(70, 75, "JUDGE_CLERK"),
    #                                                           (70, 81, "JUDGE_CLERK"),
    #                                                           (76, 81, "JUDGE_CLERK")]

