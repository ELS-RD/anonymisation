from generate_trainset.match_acora import get_acora_object, get_matches
from resources.config_provider import get_config_default


class CourtName:
    court_names = set()
    matcher = None

    def __init__(self):
        """
        Build a matcher of French court names based on a list available in open data
        https://www.data.gouv.fr/fr/datasets/les-statistiques-par-juridiction/#_
        (the list has more data, the one store is an extraction)
        """
        config = get_config_default()
        file = config["french_court_names"]

        with open(file) as f1:
            for line in f1.readlines():
                clean_text = line.strip()
                if len(clean_text) > 0:
                    self.court_names.add(clean_text)
        assert len(self.court_names) > 1000
        self.matcher = get_acora_object(list(self.court_names),
                                        ignore_case=True)

    def get_matches(self, text: str) -> list:
        """
        Find match of French court names in a text
        :param text: original text
        :return: list of offsets
        """
        return get_matches(self.matcher, text, "JURIDICTION")
