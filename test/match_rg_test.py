from match_text.match_rg import MatchRg, get_rg_from_regex


def test_rg_from_case_id():
    text1 = "CA-aix-en-provence-20130208-1022871-jurica"
    matcher = MatchRg(case_id=text1)
    assert matcher.get_rg_from_case_id() == "1022871"
    assert matcher.get_rg_offset_from_text(text=text1) == [(28, 35, 'RG')]
    text2 = "Le numéro RG est celui-ci 102 /2871."
    assert matcher.get_rg_offset_from_text(text=text2) == [(26, 35, 'RG')]


def test_rg_regex():
    assert get_rg_from_regex(" RG n° 11/17073") == [(7, 15, 'RG')]
    assert get_rg_from_regex(" RG : 13/03625 D") == [(6, 15, 'RG')]
    assert get_rg_from_regex("RG numéro : 12/01503") == [(12, 20, 'RG')]
    assert get_rg_from_regex("N°RG: 13/03409") == [(6, 14, 'RG')]
    assert get_rg_from_regex("N° 13/03409") == []
    assert get_rg_from_regex("Numéro d'inscription au répertoire général : 14/01913") == [(45, 53, 'RG')]
