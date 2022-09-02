import os
import re
import itertools
import spacy
import deeppavlov
from collections import defaultdict
from query_processor.parsing import Rule, Parse, print_chart
from types import FunctionType


class NERTagger:
    """ Class defined to tag the date and name in input query string """
    def __init__(self, config_model='ner_ontonotes_bert', download=False):
        self.ner_model = deeppavlov.build_model(deeppavlov.configs.ner[config_model], 
                                                download=download)
        self.category_map = defaultdict(lambda: '$NULL')
        self.category_map.update({'DATE': '$NERDATE', 'MONEY': '$NERMONEY'})
        # 'DATE': '$DATE', 'MONEY': '$MONEY', 'PERSON': '$NAME'
    
    def annotate_query(self, query, chart):
        result = self.ner_model([query])
        tokens, labels = result[0][0], result[1][0]
        tokens, labels = self.adjust_indexing(query, tokens, labels)
        start_ind = -1
        curr_label = None
        for i, label in enumerate(labels):
            if label[0] == 'B' or label == 'O':
                if curr_label:
                    if self.category_map[curr_label] != '$NULL':
                        rule = Rule(self.category_map[curr_label], 
                                    tuple(tokens[start_ind: i]), ' '.join(tokens[start_ind: i]))
                        chart[(start_ind, i)].append(Parse(rule, tokens[start_ind: i]))
                    curr_label = None
                    start_ind = -1
            if label[0] == 'B':
                curr_label = label[2:]
                start_ind = i
        if curr_label:
            if self.category_map[curr_label] != '$NULL':
                rule = Rule(self.category_map[curr_label], 
                            tuple(tokens[start_ind: len(tokens)]), ' '.join(tokens[start_ind: len(tokens)]))
                chart[(start_ind, len(tokens))].append(Parse(rule, tokens[start_ind: len(tokens)]))
            curr_label = None
            start_ind = -1
        # print (chart, len(tokens))
        
    def adjust_indexing(self, query, tokens, labels):
        actual_tokens = query.split()
        actual_labels = []
        curr_ind = 0
        for i, act_token in enumerate(actual_tokens):
            if act_token == tokens[curr_ind]:
                actual_labels.append(labels[curr_ind])
                curr_ind += 1
            else:
                curr = tokens[curr_ind]
                actual_labels.append(labels[curr_ind])
                while(act_token != curr):
                    curr_ind += 1
                    curr += tokens[curr_ind]
                curr_ind += 1
        return actual_tokens, actual_labels
                    

class POS_NERTagger:
    """ Class defined to tag the name in case NER fails to identify the name """
    def __init__(self, ner_model, download=False):
        # self.pos = deeppavlov.build_model(deeppavlov.configs.morpho_tagger.UD2_0.morpho_en,download=download)
        self.nlp_model = spacy.load('en_core_web_lg')
        self.ner_model = ner_model
        self.nlp_tokenizer = spacy.tokenizer.Tokenizer(self.nlp_model.vocab)
        self.nlp_ner_model = self.nlp_model.get_pipe('ner')
        self.category_map = defaultdict(lambda: '$NULL')
        self.category_map.update({'PERSON': '$NAMEPOS'})

    def annotate_query(self, query, chart):
        nlp_result = self.nlp_model(query)
        if 'PERSON' in set([e.label_ for e in nlp_result.ents]):
            result = ([t.text for t in nlp_result], 
                    [t.ent_iob_ + '-' + t.ent_type_ 
                        if t.ent_type_ else t.ent_iob_ for t in nlp_result])
            # print ('1.......', result)
        else:
            pos_tokens, pos_tags = self.adjust_indexing(query, 
                                                        [t.text for t in nlp_result], 
                                                        [t.pos_ for t in nlp_result])
            mod_tokens = [t.title() if pos == 'PROPN' else t.lower() 
                                    for t, pos in zip(pos_tokens, pos_tags)]
            # mod_tokens = [t.text.title() if t.pos_ == 'PROPN' else t.text for t in nlp_result]
            mod_query = ' '.join(mod_tokens)
            query = mod_query
            ner_result = self.ner_model([mod_query])
            result = (ner_result[0][0], ner_result[1][0])
            result_labels = [r.split('-')[-1] for r in result[1]]
            if not (self.category_map.keys()) & set(result_labels):
                # spacy_tokenizer = spacy.tokenizer.Tokenizer(self.nlp_model.vocab)
                spacy_doc = self.nlp_tokenizer(query)
                # spacy_ner = self.nlp_model.get_pipe('ner')
                ner_result = self.nlp_ner_model(spacy_doc)
                # ner_result = self.nlp_model(query)
                result = ([t.text for t in ner_result], 
                        [t.ent_iob_ + '-' + t.ent_type_ 
                            if t.ent_type_ else t.ent_iob_ for t in ner_result])
            # print ('2........', result)
        tokens, labels = result[0], result[1]
        tokens, labels = self.adjust_indexing(query, tokens, labels)
        # print ('mod_or_not', query, tokens, labels)
        start_ind = -1
        curr_label = None
        for i, label in enumerate(labels):
            if label[0] == 'B' or label == 'O':
                if curr_label:
                    if self.category_map[curr_label] != '$NULL':
                        rule = Rule(self.category_map[curr_label], 
                                    tuple(tokens[start_ind: i]), ' '.join(tokens[start_ind: i]))
                        chart[(start_ind, i)].append(Parse(rule, tokens[start_ind: i]))
                    curr_label = None
                    start_ind = -1
            if label[0] == 'B':
                curr_label = label[2:]
                start_ind = i
        if curr_label:
            if self.category_map[curr_label] != '$NULL':
                rule = Rule(self.category_map[curr_label], 
                            tuple(tokens[start_ind: len(tokens)]), ' '.join(tokens[start_ind: len(tokens)]))
                chart[(start_ind, len(tokens))].append(Parse(rule, tokens[start_ind: len(tokens)]))
            curr_label = None
            start_ind = -1
        # print_chart(chart)
        # print (len(tokens))

    def adjust_indexing(self, query, tokens, labels):
        actual_tokens = query.split()
        actual_labels = []
        curr_ind = 0
        for i, act_token in enumerate(actual_tokens):
            if act_token == tokens[curr_ind]:
                actual_labels.append(labels[curr_ind])
                curr_ind += 1
            else:
                curr = tokens[curr_ind]
                actual_labels.append(labels[curr_ind])
                while(act_token != curr):
                    curr_ind += 1
                    curr += tokens[curr_ind]
                curr_ind += 1
        return actual_tokens, actual_labels