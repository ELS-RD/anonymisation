from generate_trainset.build_dict_from_recognized_entities import get_frequent_entities_matches, \
    get_frequent_entities_matcher


def test_frequent_entities():
    freq_entities = {"benesty": "LAWYER", "jessica": "PERS"}
    matcher = get_frequent_entities_matcher(content=freq_entities)
    text = "Me Benesty rencontre son client Jessica."
    assert get_frequent_entities_matches(matcher=matcher, frequent_entities_dict=freq_entities, text=text) == \
           [(3, 10, "LAWYER"), (32, 39, "PERS")]
