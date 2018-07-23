import acora

from generate_trainset.match_acora import get_acora_object, get_matches
from resources.config_provider import get_config_default


def get_postal_code_city_list() -> list:
    """
    Build a dictionary of French cities
    :rtype: a set of postal code city name
    """

    results = list()
    config = get_config_default()
    file = config["postal_code_city"]

    with open(file) as f1:
        for line in f1.readlines():
            fields = line.split(";")
            city = fields[1].strip()
            if len(city) >= 3:
                postal_code = fields[2].strip()
                results.append(postal_code + " " + city)
                results.append(city + " (" + postal_code + ")")
    assert len(results) > 1000
    results.pop(0)
    return results


def get_postal_code_city_matcher() -> acora._cacora.UnicodeAcora:
    """
    Build a matcher of first name based on a French names dictionary
    :return: Acora matcher
    """
    postal_code_city_list = get_postal_code_city_list()
    return get_acora_object(list(postal_code_city_list),
                            ignore_case=True)


def get_postal_code_matches(matcher: acora._cacora.UnicodeAcora, text: str) -> list:
    """
    Find match of postal code and city names in a text
    :param matcher: Dictionary based matcher
    :param text: original text
    :return: list of offsets
    """
    return get_matches(matcher, text, "ADRESSE")
