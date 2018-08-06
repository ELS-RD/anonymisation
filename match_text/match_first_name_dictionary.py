from match_text_unsafe.match_acora import get_acora_object, get_matches
from modify_text.change_case import get_title_case
from resources.config_provider import get_config_default


class FirstName:
    first_name_dict = None
    matcher = None

    def __init__(self, ignore_case: bool):
        """
        Build a matcher of first name based on a French names dictionary
        :type ignore_case: True to ignore case during matching
        :return: Acora matcher
        """
        config = get_config_default()

        file1 = config["first_name_dict_1"]
        file2 = config["first_name_dict_2"]

        firs_name = set()
        with open(file1) as f1:
            for line in f1.readlines():
                fields = line.split(";")
                # all names start with a Upcase letter and finishes with a space
                text = fields[3].strip()
                if len(text) >= 4:
                    firs_name.add(text)

        with open(file2, encoding="ISO-8859-1") as f2:
            for line in f2.readlines():
                fields = line.split(";")
                text = fields[0].strip()
                if len(text) >= 4:
                    firs_name.add(get_title_case(text))

        to_remove = ["Elle", "France", "Mercedes", "Paris", "Alger", "Oran", "Sans"]

        for item_to_remove in to_remove:
            firs_name.remove(item_to_remove)

        self.first_name_dict = firs_name
        self.matcher = get_acora_object(list(self.first_name_dict),
                                        ignore_case=ignore_case)

    def get_matches(self, text: str) -> list:
        """
        Find match of first name in a text
        :param text: original text
        :return: list of offsets
        """
        offsets = get_matches(self.matcher, text, "PERS")
        # names include a space so we fix the point by removing 1 to the offset
        results = [(start, end - 1, type_name) for start, end, type_name in offsets]
        return results

    def contain_first_names(self, text: str) -> bool:
        """
        Check if a text contains a known first name
        :param text: original text
        :return: True if it contains a first name
        """
        matches = self.get_matches(text=text)
        for start, end, _ in matches:
            if (end == len(text) - 1) or (not text[end + 1].isalpha()):
                return True

        return False
