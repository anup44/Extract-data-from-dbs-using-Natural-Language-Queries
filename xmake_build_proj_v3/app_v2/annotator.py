import re
from collections import defaultdict
from fuzzywuzzy import fuzz, process


class Annotator:
    """A base class for annotators."""
    def annotate(self, tokens):
        """Returns a list of pairs, each a category and a semantic representation."""
        return []


class TokenAnnotator(Annotator):
    def annotate(self, tokens):
        if len(tokens) == 1:
            return [('$Token', tokens[0])]
        else:
            return []


class NumberAnnotator(Annotator):
    def annotate(self, tokens):
        if len(tokens) == 1:
            try:
                value = float(tokens[0])
                if int(value) == value:
                    value = int(value)
                return [('$Number', value)]
            except ValueError:
                pass
        return []


class AlphaNumAnnotator(Annotator):
    def __init__(self):
        # self.regex = r'^\w*\d+\w*[-_]\w*\d+\w*$'
        self.regex = r'^[\w-]*\d+[\w-]*$'

    def annotate(self, tokens):
        phrase = ' '.join(tokens)
        match = re.match(self.regex, phrase)
        if match:
            return [('$AlphaNum', match.group())]
        else:
            return []


class EntityAnnotator(Annotator):
    """ takes a database that is a list of tuples containing category and entity name """
    def __init__(self, database):
        self.database = database
        self.category_index = defaultdict(set)
        self.entity_id_index = {}
        self.search_index = defaultdict(set)
        self.search_terms = defaultdict(set)
        self.index_database(database)

    def index_database(self, database):
        for entity_tup in database:
            self.category_index[entity_tup[1]].add(entity_tup[0])
            self.entity_id_index[entity_tup[0]] = entity_tup[1]
            self.search_index[entity_tup[2]].add(entity_tup[:2])
            self.search_terms[entity_tup[0]].add(entity_tup[2])

    def fuzzy_match(self, phrase, score_cutoff=80):
        p_tokens = phrase.split()
        max_score = -1
        best_match = None
        for ent_phrase in self.search_index.keys():
            e_tokens = ent_phrase.split()
            common = [t for t in p_tokens if t in e_tokens]
            common = ' '.join(common)
            p_tokens = sorted(set(p_tokens) - set(common))
            e_tokens = sorted(set(e_tokens) - set(common))
            match_score = fuzz.ratio(common + ' '.join(p_tokens), common + ' '.join(e_tokens))
            if match_score >= score_cutoff and match_score > max_score:
                max_score = match_score
                best_match = ent_phrase 
        return (best_match, max_score) if best_match else best_match

    def search_phrase(self, phrase):
        # return self.search_index[phrase]
        best_match = None
        try:
            best_match = process.extractOne(phrase, 
                                            self.search_index.keys(), 
                                            scorer=fuzz.ratio, 
                                            score_cutoff=80)
        except:
            print ('[Warning] No data in entitiy DB. Please update entities using /read_data endpoint.')
        # best_match = process.extractOne(phrase, self.search_index.keys(), scorer=fuzz.token_sort_ratio, score_cutoff=80)
        # best_match = self.fuzzy_match(phrase, score_cutoff=80)
        # print (phrase, best_match)
        if best_match:
            return self.search_index[best_match[0]]
        else:
            try:
                best_match = process.extractOne(phrase, 
                                                self.search_index.keys(), 
                                                scorer=fuzz.token_sort_ratio, 
                                                score_cutoff=80)
            except:
                print ('[Warning] No data in entitiy DB. Please update entities using /read_data endpoint.')
            if best_match:
                return self.search_index[best_match[0]]
            else:
                return []

    def annotate(self, tokens):
        if len(tokens) <= 3:
            phrase = ' '.join(tokens)
            phrase = phrase.lower()
            entity_names = self.search_phrase(phrase)
            return [(entity_name[1], entity_name[0]) for entity_name in entity_names]
        else:
            return []


class OptionalWordsAnnotator(Annotator):
    """ Annotates the extra words like to,from,get etc """
    def __init__(self, words=[]):
        self.words = set(words)

    def annotate(self, tokens):
        return [('$Optionals', None)]


if __name__ == '__main__':
    annotators = [TokenAnnotator(), NumberAnnotator(), OptionalWordsAnnotator()]
    tokens = 'four score and 30 years ago'.split()
    for j in range(1, len(tokens) + 1):
        for i in range(j - 1, -1, -1):
            annotations = [a for anno in annotators for a in anno.annotate(tokens[i:j])]
            print('(%d, %d): %s => %s' % (i, j, ' '.join(tokens[i:j]), annotations))
