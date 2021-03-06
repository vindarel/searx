#!/usr/bin/env python

'''
searx is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

searx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with searx. If not, see < http://www.gnu.org/licenses/ >.

(C) 2014 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>
'''

from searx.languages import language_codes
from searx.engines import (
    categories, engines, engine_shortcuts
)
import string
import re


class Query(object):
    """parse query"""

    def __init__(self, query, disabled_engines):
        self.query = query
        self.disabled_engines = []

        if disabled_engines:
            self.disabled_engines = disabled_engines

        self.query_parts = []
        self.engines = []
        self.languages = []
        self.specific = False

    # parse query, if tags are set, which
    # change the serch engine or search-language.
    def parse_query(self):
        self.query_parts = []

        # split query, including whitespaces
        raw_query_parts = re.split(r'(\s+)', self.query)

        raw_query_parts = [it.strip() for it in raw_query_parts if it.strip()]
        bangs = [it for it in raw_query_parts if it[0] in ['!', '?']]
        languages = [it for it in raw_query_parts if it[0] in [':']]
        query_parts = list(set(raw_query_parts) - set(bangs) - set(languages))

        if languages:
            # check if any language-code is equal with
            # declared language-codes
            lang = languages[0][1:].lower()
            for lc in language_codes:
                lang_id, lang_name, country = map(str.lower, lc)

                # if correct language-code is found
                # set it as new search-language
                if lang == lang_id\
                   or lang_id.startswith(lang)\
                   or lang == lang_name\
                   or lang.replace('_', ' ') == country:
                    parse_next = True
                    self.languages.append(lang)
                    break

        if bangs:
            # this forces a engine or category
            prefix = bangs[0][1:].replace('_', ' ')

            # check if prefix is equal with engine shortcut
            if prefix in engine_shortcuts:
                parse_next = True
                self.engines.append({'category': 'none',
                                     'name': engine_shortcuts[prefix]})

            # check if prefix is equal with engine name
            elif prefix in engines:
                parse_next = True
                self.engines.append({'category': 'none',
                                        'name': prefix})

            # check if prefix is equal with categorie name
            elif prefix in categories:
                # using all engines for that search, which
                # are declared under that categorie name
                parse_next = True
                self.engines.extend({'category': prefix,
                                        'name': engine.name}
                                    for engine in categories[prefix]
                                    if (engine.name, prefix) not in self.disabled_engines)

        # append query part to query_part list
        self.query_parts = [' '.join([it for it in query_parts])]

    def changeSearchQuery(self, search_query):
        if len(self.query_parts):
            self.query_parts[-1] = search_query
        else:
            self.query_parts.append(search_query)

    def getSearchQuery(self):
        if len(self.query_parts):
            return self.query_parts[-1]
        else:
            return ''

    def getFullQuery(self):
        # get full querry including whitespaces
        return string.join(self.query_parts, '')
