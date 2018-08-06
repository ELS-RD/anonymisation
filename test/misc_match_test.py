from match_text.match_extension_of_entity_name import get_all_name_variation
from match_text.match_first_name_dictionary import FirstName


def test_match_sub_pattern():
    texts = ["Je suis avec Jessica BENESTY et elle est sympa.",
             "Jessica n'est pas là.",
             "Ou est Mme. Benesty ?",
             "La SARL TOTO forme avec la SCI TOTO un groupe de sociétés.",
             "Condamné CEK PARTICIPATIONS à payer à la SCI CEK PARTICIPATIONS la somme"]
    offsets = [[(13, 28, "PERS")], [], [], [(3, 12, "ORGANIZATION")], [(41, 63, "ORGANIZATION")]]
    assert get_all_name_variation(texts, offsets, threshold_span_size=4) == [[(13, 20, "PERS"),
                                                                              (13, 28, "PERS"),
                                                                              (21, 28, "PERS"),
                                                                              (13, 28, "PERS")],
                                                                             [(0, 7, "PERS")],
                                                                             [(12, 19, "PERS")],
                                                                             [(3, 12, "ORGANIZATION"),
                                                                              (8, 12, "ORGANIZATION"),
                                                                              (31, 35, "ORGANIZATION"),
                                                                              (3, 12, "ORGANIZATION")],
                                                                             [(9, 27, "ORGANIZATION"),
                                                                              (41, 63, "ORGANIZATION"),
                                                                              (45, 63, "ORGANIZATION"),
                                                                              (41, 63, "ORGANIZATION")]]


def test_get_first_name_dict():
    matcher = FirstName(ignore_case=False)
    assert len(matcher.first_name_dict) == 12464
    assert "Michaël" in matcher.first_name_dict


def test_get_phrase_matcher():
    text = "Aujourd'hui, Michaël et Jessica écrivent des unit tests dans la joie et la bonne humeur, " \
           "mais où sont donc les enfants ?"
    matcher = FirstName(ignore_case=False)
    assert matcher.get_matches(text=text) == [(13, 19, "PERS"), (24, 30, "PERS")]
    assert matcher.contain_first_names(text=text) is True

