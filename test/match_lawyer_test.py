from generate_trainset.match_lawyer import get_lawyer_name


def test_extract_lawyer():
    text1 = "A la demande de Me Toto TOTO, avocat"
    assert get_lawyer_name(text1) == [(19, 28, "LAWYER")]
    text2 = "Me Carine Chevalier - Kasprzak"
    assert get_lawyer_name(text2) == [(3, 30, "LAWYER")]
