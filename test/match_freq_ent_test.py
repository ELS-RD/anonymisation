from generate_trainset.build_dict_from_recognized_entities import FrequentEntities


def test_frequent_entities():
    freq_entities = {"benesty": "LAWYER", "jessica": "PERS"}
    frequent_entities_matcher = FrequentEntities.test_builder(content=freq_entities)
    text = "Me Benesty rencontre son client Jessica."
    assert frequent_entities_matcher.get_matches(text=text) == [(3, 10, "LAWYER"), (32, 39, "PERS")]
