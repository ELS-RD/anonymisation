from match_text.match_bar import get_bar


def test_bar():
    text1 = "Le barreau de PARIS toto"
    assert get_bar(text=text1) == [(3, 19, "BAR_1")]
    text2 = "Je travaille au barreau D'AMIENS et c'est top !"
    assert get_bar(text=text2) == [(16, 32, "BAR_1")]


