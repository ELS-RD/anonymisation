from misc.extract_first_last_name import get_last_name, get_first_last_name


def test_match_family_name():
    assert get_last_name("Mic BEN TITI") == "BEN TITI"
    assert get_last_name(" Mic BEN TITI ") == "BEN TITI"
    assert get_last_name("Mic BEN") == "BEN"
    assert get_last_name("Mic BENp") == ""
    assert get_first_last_name("Mic BEN TITI") == ("Mic", "BEN TITI")
    assert get_first_last_name(" Mic BEN TITI ") == ("Mic", "BEN TITI")

