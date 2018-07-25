import acora
from acora import AcoraBuilder

from generate_trainset.match_acora import get_matches
from generate_trainset.modify_strings import get_first_last_name


class MatchValuesFromHeaders:
    matcher_partie_pm = None
    matcher_partie_pp = None
    matcher_lawyers = None
    matcher_president = None
    matcher_conseiller = None
    matcher_clerks = None
    current_header = dict()
    threshold_size = 0

    def __init__(self, current_header: dict, threshold_size: int):
        """
        Build a matcher of values from headers
        :param current_header: : original dict build from values from headers
        :param threshold_size: minimum size of a word to be added to a matcher
        """
        self.current_header = current_header
        self.threshold_size = threshold_size

        self.matcher_partie_pm = self.get_matcher_of_partie_pm_from_headers()
        self.matcher_partie_pp = self.get_matcher_of_partie_pp_from_headers()
        self.matcher_lawyers = self.get_matcher_of_lawyers_from_headers()
        self.matcher_president = self.get_matcher_of_president_from_headers()
        self.matcher_conseiller = self.get_matcher_of_conseiller_from_headers()
        self.matcher_clerks = self.get_matcher_of_clerks_from_headers()

    def get_matched_entities(self, current_paragraph: str) -> list:
        current_doc_offsets = get_matches(self.matcher_partie_pp, current_paragraph, "PARTIE_PP")
        current_doc_offsets += get_matches(self.matcher_partie_pm, current_paragraph, "PARTIE_PM")
        current_doc_offsets += get_matches(self.matcher_lawyers, current_paragraph, "AVOCAT")
        current_doc_offsets += get_matches(self.matcher_president, current_paragraph, "MAGISTRAT")
        current_doc_offsets += get_matches(self.matcher_clerks, current_paragraph, "GREFFIER")

        return current_doc_offsets

    def get_matcher_of_partie_pp_from_headers(self) -> acora._cacora.UnicodeAcora:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        # this way of init assure that the matcher doesn't expect binary data
        # this may happen if we load empty arrays through update function for instance
        matcher = AcoraBuilder("@!#$%")

        for full_content, short_content in zip(
                self.current_header['defendeur_fullname'] + self.current_header['demandeur_fullname'],
                self.current_header['defendeur_hidden'] + self.current_header['demandeur_hidden']):
            if short_content is not None:
                matcher.add(full_content)
                first_name, last_name = get_first_last_name(full_content)
                if len(first_name) > self.threshold_size:
                    matcher.add(first_name)
                if len(last_name) > self.threshold_size:
                    matcher.add(last_name)

        return matcher.build(ignore_case=True)

    def get_matcher_of_partie_pm_from_headers(self) -> acora._cacora.UnicodeAcora:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        matcher = AcoraBuilder("@!#$%")

        for full_content, short_content in zip(
                self.current_header['defendeur_fullname'] + self.current_header['demandeur_fullname'],
                self.current_header['defendeur_hidden'] + self.current_header['demandeur_hidden']):
            if short_content is None:
                matcher.add(full_content)

        return matcher.build(ignore_case=True)

    def get_matcher_of_lawyers_from_headers(self) -> acora._cacora.UnicodeAcora:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        header_content = self.current_header['avocat']
        matcher = AcoraBuilder("@!#$%")
        matcher.update(header_content)
        for content in header_content:
            first_name, last_name = get_first_last_name(content)
            if len(first_name) > self.threshold_size:
                matcher.add(first_name)
            if len(last_name) > self.threshold_size:
                matcher.add(last_name)
        return matcher.build(ignore_case=True)

    def get_matcher_of_president_from_headers(self) -> acora._cacora.UnicodeAcora:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        header_content = self.current_header['president']
        matcher = AcoraBuilder("@!#$%")
        matcher.update(header_content)
        for content in header_content:
            first_name, last_name = get_first_last_name(content)
            if len(first_name) > self.threshold_size:
                matcher.add(first_name)
            if len(last_name) > self.threshold_size:
                matcher.add(last_name)
        return matcher.build(ignore_case=True)

    def get_matcher_of_conseiller_from_headers(self) -> acora._cacora.UnicodeAcora:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        header_content = self.current_header['conseiller']
        matcher = AcoraBuilder("@!#$%")
        matcher.update(header_content)
        for content in header_content:
            first_name, last_name = get_first_last_name(content)
            if len(first_name) > self.threshold_size:
                matcher.add(first_name)
            if len(last_name) > self.threshold_size:
                matcher.add(last_name)
        return matcher.build(ignore_case=True)

    def get_matcher_of_clerks_from_headers(self) -> acora._cacora.UnicodeAcora:
        """
        Create variations of items to search
        :return: a matcher of string which ignore case
        """
        header_content = self.current_header['greffier']
        matcher = AcoraBuilder("@!#$%")
        matcher.update(header_content)
        for content in header_content:
            first_name, last_name = get_first_last_name(content)
            if len(first_name) > self.threshold_size:
                matcher.add(first_name)
            if len(last_name) > self.threshold_size:
                matcher.add(last_name)
        return matcher.build(ignore_case=True)
