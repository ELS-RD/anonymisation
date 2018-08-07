from acora import AcoraBuilder


class AcoraMatcher:
    matcher = None

    def __init__(self, content: list, ignore_case: bool):
        """
        Acora matcher factory
        :param content: a list of items to search
        :param ignore_case: True to match any case
        :return: a built matcher
        """
        # start with a string in case content is empty
        # otherwise it builds a binary Acora matcher
        builder = AcoraBuilder("!@#$%%^&*")
        builder.update(content)
        self.matcher = builder.build(ignore_case=ignore_case)

    def get_matches(self, text: str, tag: str):
        """
        Apply the matcher and return offsets
        :param text: original string where to find the matches
        :param tag: the type of offset
        :return: list of offsets
        """
        # matcher not loaded with any pattern
        if self.matcher.__sizeof__() == 0:
            return []
        results = self.matcher.findall(text)
        return [(start_offset, start_offset + len(match_text), tag)
                for match_text, start_offset in results if
                self.__filter_fake_match(start=start_offset, end=start_offset + len(match_text), text=text)]

    def findall(self, text):
        return self.matcher.findall(text)

    @staticmethod
    def __filter_fake_match(start: int, end: int, text: str) -> bool:
        """
        Predicate to detect if candidate offset is aligned with word boundary
        :param start: begin of the offset
        :param end: end of the offset
        :param text: original text
        :return: True if matches a word boundary
        """
        if start == 0:
            previous_token_ok = True
        else:
            previous_token_ok = not text[start - 1].isalnum()

        if end == len(text):
            next_token_ok = True
        else:
            next_token_ok = not text[end].isalnum()
        return previous_token_ok and next_token_ok
