from generate_trainset.match_acora import get_acora_object, get_matches
from resources.config_provider import get_config_default


class PostalCodeCity:
    matcher = None

    def __init__(self):
        """
        Build a matcher of first name based on a French names dictionary
        """
        postal_code_city_list = list()
        config = get_config_default()
        file = config["postal_code_city"]

        with open(file) as f1:
            for line in f1.readlines():
                fields = line.split(";")
                city = fields[1].strip()
                if len(city) >= 3:
                    postal_code = fields[2].strip()
                    postal_code_city_list.append(postal_code + " " + city)
                    postal_code_city_list.append(city + " (" + postal_code + ")")
        assert len(postal_code_city_list) > 1000
        postal_code_city_list.pop(0)
        self.matcher = get_acora_object(list(postal_code_city_list),
                                        ignore_case=True)

    def get_matches(self, text: str) -> list:
        """
        Find match of postal code and city names in a text
        :param text: original text
        :return: list of offsets
        """
        return get_matches(self.matcher, text, "ADDRESS")
