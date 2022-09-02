import requests 
import json
import os
import re
import datetime
import argparse
from query_processor.parsing import *
from query_processor.scoring import Model, rule_features, score, rule_features_2, rule_features_3
from flask import Flask, request, render_template, Response
from waitress import serve
from collections import defaultdict
import itertools
from types import FunctionType
from query_processor.preprocessing import Preprocess
from query_processor.app_config import App_Config
from query_processor.annotator import Annotator, NumberAnnotator, TokenAnnotator, \
                    AlphaNumAnnotator, EntityAnnotator, OptionalWordsAnnotator
from query_processor.tagger import NERTagger, POS_NERTagger
from query_processor.domain_rules import rules_1, weights
from query_processor.postprocessing import FieldConverter, fields_1
from query_processor.intent_map import intent_map_ext, intent_field_map, filter_separator_map
import tensorflow as tf


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("command", type=str, 
                        help="use 'start' to run the app")
arg_parser.add_argument('-p', '--port', default=5001,
                        help="port for the app to use")
args = arg_parser.parse_args()

# To suppress warning messages printed on screen

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
tf.logging.set_verbosity(tf.logging.ERROR)

config = App_Config()
USE_SPELL_CORRECTOR = True
MAX_CELL_CAPACITY = 10000

entity_db = []

rules = rules_1
preprocess = Preprocess(use_spell_corrector=USE_SPELL_CORRECTOR, download=False)
entity_annotator = EntityAnnotator(entity_db)

ner_tagger = NERTagger(download=False)
pos_ner_tagger = POS_NERTagger(ner_tagger.ner_model, download=False)

grammar = Grammar(preprocess, rules=rules, 
                annotators = [entity_annotator, 
                                NumberAnnotator(), 
                                AlphaNumAnnotator(), 
                                TokenAnnotator(), 
                                OptionalWordsAnnotator()], 
                                taggers=[ner_tagger, pos_ner_tagger], 
                                start_symbol='$ROOT')
parsing_model = Model(grammar=grammar, feature_fn=rule_features_3, weights=weights)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/parse_query', methods=['GET', 'POST'])
def my_form_post():
    text = request.args.get('query', default='no query specified', type=str)
    print ('Input query: {}'.format(text))
    parses = parsing_model.parse_input(text)
    out_dict = {}
    try:
        # print(parses[0])
        out_dict = parses[0].semantics

        parse_sem = parses[0].semantics.copy()
    except:
        pass
    # print(out_dict)
    return_dict = {}
    odata_link_with_filter = ''
    if 'TYPE' in out_dict:
        intent = out_dict['TYPE']

        fc = FieldConverter(fields=fields_1)
        fc.field_selection(parse_sem)
        fc.convert_fields(parse_sem)
        query_filter = filter_separator_map[intent].join(fc.generate_filter(parse_sem))
        # print (parse_sem)
        print ('Generated filters: {}'.format(query_filter))
        try:
            data_host_addr = config.data_host_addr
            data_host_port = config.data_host_port
        except AttributeError as e:
            print (e)
            return "Please provide host and port for odata generation using the endpoint '/read_data'"
            
        odata_link = 'https://' \
                    + data_host_addr + ':' + data_host_port \
                    + config.get_value_from_dict(intent_map_ext, parse_sem['TYPE'])
        odata_link_with_filter = odata_link.format(query_filter) # + '?$filter=(' + query_filter + ')'
        
        return_dict['intent'] = intent
        return_dict['odata'] = odata_link_with_filter
        
    else:
        return_dict['fall_back_code'] = 1
        return_dict['message'] = "Sorry, I can't understand this query. Please try another query"
    return Response(json.dumps(return_dict), headers={'Content-Type':'text/json; charset=utf-8'})
#    
def read_request_body(data):
    data_dict = json.loads(data)
    print (data_dict.keys())
    try:
        print (data_dict['host'], data_dict['port'], dadata_dictta['d']['results'])
    except:
        raise KeyError

@app.route('/read_data', methods=['POST'])
def read_data():
    data = request.data
    if data:
        try:
            data_dict = json.loads(data)
        except:
            return "[ERROR] Data sent was not in json format."
        else:
            config.push_entities_data(data_dict)
            global rules
            global entity_db
            global entity_annotator
            entity_db = config.programs_db \
                        + config.agencies_db \
                        + config.benefits_db \
                        + config.reasontext_db \
                        + config.identifier_db
            entity_annotator = EntityAnnotator(entity_db)
            global preprocess
            preprocess.load_include_set(rules)
            global grammar
            global parsing_model
            grammar = Grammar(preprocess, 
                                rules=rules, 
                                annotators = [entity_annotator, 
                                                NumberAnnotator(), 
                                                AlphaNumAnnotator(), 
                                                TokenAnnotator(), 
                                                OptionalWordsAnnotator()], 
                                                taggers=[ner_tagger, pos_ner_tagger], 
                                                start_symbol='$ROOT')
            parsing_model = Model(grammar=grammar, feature_fn=rule_features_3, weights=weights)
            return '[Success] Data was received.'
    else:
        return "no data provided. Please provide json in 'data' parameter"

def waitress_serve():
    return app

def main():
    if args.command == "start":
        serve(app, host="0.0.0.0", port=int(os.environ.get('PORT', args.port)))

if __name__ == '__main__':
   serve(app, host="0.0.0.0", port=int(os.environ.get('PORT', args.port)))