from collections import defaultdict
from query_processor.parsing import Parse
from query_processor.domain_rules import zero_value_categories

# zero_value_categories = ['$Optionals', '$Token', '$Optional']

def rule_features(parse):
    """
    Returns a map from (string representations of) rules to how often they were
    used in the given parse.
    """
    def collect_rule_features(parse, features):
        feature = str(parse.rule)
        features[feature] += 1.0
        for child in parse.children:
            if isinstance(child, Parse):
                collect_rule_features(child, features)
    features = defaultdict(float)
    collect_rule_features(parse, features)
    return features


def rule_features_2(parse):
    def collect_rule_features(parse, features):
        feature = (parse.rule.lhs, parse.rule.rhs)
        features[feature] += 1.0
        for child in parse.children:
            if isinstance(child, Parse):
                collect_rule_features(child, features)
    features = defaultdict(float)
    collect_rule_features(parse, features)
    return features


def rule_features_3(parse):
    def collect_rule_features(parse, features):
        token_len = 0.0
        # if (parse.rule.lhs not in zero_value_categories):
        for child in parse.children:
            if isinstance(child, Parse):
                child_token_len = collect_rule_features(child, features)
                # get the actual value for zero_value_categories, 
                # but these values dont translate upwards
                if not child.rule.lhs in zero_value_categories:
                    token_len += child_token_len
            else:
                token_len += 1.0
        feature = (parse.rule.lhs, parse.rule.rhs)
        features[feature] += token_len**1.1
        return token_len
    features = defaultdict(float)
    _ = collect_rule_features(parse, features)
    return features


def score(parse=None, feature_fn=None, weights=None):
    """Returns the inner product of feature_fn(parse) and weights."""
    assert parse and feature_fn and weights != None
    return sum(weights[feature] * value for feature, value in list(feature_fn(parse).items()))


class Model:
    def __init__(self,
                 grammar=None,
                 feature_fn=lambda parse: defaultdict(float),
                 weights=defaultdict(float),
                 executor=None):
        assert grammar
        self.grammar = grammar
        self.feature_fn = feature_fn
        self.weights = weights
        self.executor = executor

    def parse_input(self, input):
        parses = self.grammar.parse_input(input)
        for parse in parses:
            if self.executor:
                parse.denotation = self.executor(parse.semantics)
            parse.score = score(parse, self.feature_fn, self.weights)
        return sorted(parses, key=lambda parse: parse.score, reverse=True)
