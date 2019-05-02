#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

import regex

from match_text_unsafe.match_acora import AcoraMatcher
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
        self.matcher = AcoraMatcher(content=list(self.court_names),
                                    ignore_case=True)

    def get_matches(self, text: str) -> list:
        """
        Find match of French court names in a text
        :param text: original text
        :return: list of offsets
        """
        return self.matcher.get_matches(text=text, tag="COURT")


# List of French courts: http://www.justice.gouv.fr/organisation-de-la-justice-10031/lordre-judiciaire-10033/
juridiction_pattern_1 = regex.compile(r"((?i)Tribunal de grande instance|Tribunal d'instance|"
                                      r"Conseil de prud.*hommes(.{0,10}formation (paritaire|de départage))?|"
                                      r"Tribunal( mixte)? de commerce|Tribunal des affaires de sécurité sociale|"
                                      r"Tribunal paritaire des baux ruraux|Cour d'assises|Tribunal correctionnel|"
                                      r"Tribunal de police|Juge de proximit.|Juge des enfants|Tribunal pour enfants|"
                                      r"Cour d'assises des mineurs|Cour d'appel|"
                                      r"Tribunal administratif|Cour administrative d'appel|"
                                      r"Cour nationale du droit d'asile|"
                                      r"\bT(\.| )*G(\.| )*I(\.| )*|T(\.| )*I(\.| )*\\b|"
                                      r"\bT(\.| )*A(\.| )*S(\.| )*S(\.| )*\\b)"
                                      "[^A-Z]{0,5}"
                                      r"("
                                      r"(?!\bDU\b\s)"
                                      r"[A-ZÉÈ]+[\w\-']*\s*"
                                      # "((de|d'|en|des|du|à)\s*)?"
                                      r"((de\s+|d'|en\s+|des\s+|du\s+|à\s+)(?![[:lower:]]))?"
                                      r")+"
                                      r"(?!(?i)\b(en|le|du)\b)",
                                      flags=regex.VERSION1)

# http://fr.jurispedia.org/index.php/Liste_des_juridictions_(fr)
juridiction_pattern_2 = regex.compile("Cour de cassation|Conseil d'.tat|INPI|Conseil des prises maritimes|"
                                      "Commission des recours des r.fugi.s|Commissions d.partementales d'aide sociale|"
                                      "Commision d'indemnisation des rapatri.s|Conseil sup.rieur de la magistrature|"
                                      "Tribunal des conflits|Haute cour de justice|Cour de justice de la R.publique|"
                                      "Conseil constitutionnel",
                                      flags=regex.VERSION1 | regex.IGNORECASE)


def get_juridictions(text: str) -> list:
    """
    Extract Courts name from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result1 = [(t.start(), t.end(), "COURT_1") for t in juridiction_pattern_1.finditer(text)]
    result2 = [(t.start(), t.end(), "COURT_1") for t in juridiction_pattern_2.finditer(text)]
    return result1 + result2
