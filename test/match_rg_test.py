from generate_trainset.match_rg import MatchRg


def test_rg():
    text1 = "CA-aix-en-provence-20130208-1022871-jurica"
    matcher = MatchRg(case_id=text1)
    assert matcher.get_rg_from_case_id() == "1022871"
    assert matcher.get_rg_offset_from_text(text=text1) == [(28, 35, 'RG')]
    text2 = "Le numéro RG est celui-ci 102 /2871."
    assert matcher.get_rg_offset_from_text(text=text2) == [(26, 35, 'RG')]
