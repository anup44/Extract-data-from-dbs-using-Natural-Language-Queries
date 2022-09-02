# import xlrd
import requests
from query_processor.parsing import Rule
import re


class App_Config():
    """ Class to load intital configuration data"""
    def __init__(self, config_files=['intent_map.xlsx']):
        self.config_vars = {'data_host_addr': [self.load_data_host_addr, None, -1, None],
                            'data_host_port':[self.load_data_host_port, None, -1, None],
                            # 'intent_map': [self.load_intent_map, None, -1, None],
                            'agencies_db': [self.load_agencies_db, None, -1, None],
                            'benefits_db': [self.load_benefits_db, None, -1, None],
                            'programs_db': [self.load_programs_db, None, -1, None],
                            'reasontext_db': [self.load_reasontext_db, None, -1, None],
                            'identifier_db': [self.load_identifier_db, None, -1, None],
                            # 'rules': [self.load_rules, None, -1, None]
                           }
        self.request_data_paths = [('host', ('data_host_addr',)),
                                   ('port', ('data_host_port',)),
                                   ('Agencydata.d.results', ('agencies_db', 'benefits_db', 'programs_db')),
                                   ('Reasondata.d.results', ('reasontext_db',)),
                                   ('BPIdType.d.results', ('identifier_db',))]
        self.words_to_remove = ['account', 'detected', 'subsidy', 'allowance', 'benefit', 'payment']
        self.pattern_to_remove = r'\s*\b' + '|'.join(self.words_to_remove) + r'\b\s*'
        self.paths_file = 'config_tables/config_paths.xlsx'
        self.req_data = None
        # self.prepare_file_paths()
        # self.get_entities_data()
        # self.intent_map = {}
        self.config_files = config_files
        self.load_config()
        
    def __getattr__(self, attr):
        if attr in self.config_vars.keys():
            print ("Data not found for attribute {}.".format(attr))
            raise AttributeError(f'Please provide data for {self.__class__.__name__}.{attr} before calling this function.')
        else:
            raise AttributeError()

    def validate_json(self):
        data_dict = self.req_data
        pass

    def process_search_text(self, text):
        return re.sub(self.pattern_to_remove, ' ', text.lower()).strip()

    # def prepare_file_paths(self):
    #     sheet = xlrd.open_workbook(self.paths_file).sheet_by_index(0)
    #     for i in range(sheet.nrows):
    #         self.config_vars[sheet.cell_value(i, 0)][1] = sheet.cell_value(i, 1)
    #         self.config_vars[sheet.cell_value(i, 0)][2] = int(sheet.cell_value(i, 2))
        
    def push_entities_data(self, data_dict):
        self.req_data = data_dict
        for key_path, ent_vars in self.request_data_paths:
            var_data = self.get_value_from_dict(self.req_data, key_path)
            for ent in ent_vars: self.config_vars[ent][3] = var_data
        # for ent in self.request_data_vars:
        #     self.config_vars[ent][3] = req_data
        print ('data fetched')
        self.load_config()

    def load_config(self, c_vars=None):
        c_vars = self.config_vars.keys() if not c_vars else c_vars
        for key in c_vars:
            if key in self.config_vars.keys():
                if self.config_vars[key][3]:
                    print ("Preparing '{}' data from received data".format(key))
                    self.config_vars[key][0](key)
                    self.config_vars[key][3] = None
                elif self.config_vars[key][1]:
                    print ("Received data did not contain data for '{}'. Data will be prepared from locally stored files.".format(key))
                    self.config_vars[key][0](key)
                else:
                    print ("No data found for '{}'".format(key))
            else:
                print ('no config set for name: {}'.format(key))
        
    # def load_intent_map(self, key):
    #     intent_map = {}
    #     if not self.config_vars[key][3]:
    #         sheet = xlrd.open_workbook(self.config_vars[key][1]).sheet_by_index(self.config_vars[key][2])
    #         for i in range(1, sheet.nrows):
    #             intent_map[sheet.cell_value(i, 0)] = sheet.cell_value(i, 1)
    #     else:
    #         print ('ERROR: intent map not found')
    #     self.__setattr__(key, intent_map)

    def load_data_host_addr(self, key):
        if self.config_vars[key][3]:
            data_host_addr = self.config_vars[key][3]
            self.__setattr__(key, data_host_addr)

    def load_data_host_port(self, key):
        if self.config_vars[key][3]:
            data_host_port = self.config_vars[key][3]
            self.__setattr__(key, data_host_port)
        
    def load_agencies_db(self, key):
        agencies_db = []
        if self.config_vars[key][3]:
            agencies_db = [(r['ObjectId'], '$AGENCY', self.process_search_text(r['ObjectName'])) 
                                for r in self.config_vars[key][3] if r['ObjectType'] == 'CN']\
                        + [(r['ObjectId'], '$AGENCY', r['ObjectId'].lower()) 
                                for r in self.config_vars[key][3] if r['ObjectType'] == 'CN']
        # else:
        #     sheet = xlrd.open_workbook(self.config_vars[key][1]).sheet_by_index(self.config_vars[key][2])
        #     headers = sheet.row_values(0)
        #     entity_icol = headers.index('SHORT')
        #     search_text_icol = headers.index('STEXT')
        #     entity_col = sheet.col_values(entity_icol, 1)
        #     search_text_col = map(lambda text: text.lower(), sheet.col_values(search_text_icol, 1))
        #     agencies_db = list(zip(entity_col, ['$AGENCY' for i in range(len(entity_col))], search_text_col))
        else:
            print ('ERROR agencies DB not loaded')
        self.__setattr__(key, agencies_db)

    def load_benefits_db(self, key):
        benefits_db = []
        if self.config_vars[key][3]:
            benefits_db = [(r['ObjectId'], '$BENEFIT', self.process_search_text(r['ObjectName']))
                                for r in self.config_vars[key][3] if r['ObjectType'] == 'PY']\
                        + [(r['ObjectId'], '$BENEFIT', r['ObjectId'].lower()) 
                                for r in self.config_vars[key][3] if r['ObjectType'] == 'PY']
        # else:
        #     sheet = xlrd.open_workbook(self.config_vars[key][1]).sheet_by_index(self.config_vars[key][2])
        #     headers = sheet.row_values(0)
        #     entity_icol = headers.index('EXTERNALID')
        #     search_text_icol = headers.index('OBJECTNAME')
        #     entity_col = sheet.col_values(entity_icol, 1)
        #     search_text_col = map(lambda text: text.lower(), sheet.col_values(search_text_icol, 1))
        #     benefits_db = list(zip(entity_col, ['$BENEFIT' for i in range(len(entity_col))], search_text_col))
        else:
            print ('ERROR benefits DB not loaded')
        self.__setattr__(key, benefits_db)
        
    def load_programs_db(self, key):
        programs_db = []
        if self.config_vars[key][3]:
            programs_db = [(r['ObjectId'], '$BENEFIT', self.process_search_text(r['ObjectName'])) 
                                for r in self.config_vars[key][3] if r['ObjectType'] == 'PS']\
                        + [(r['ObjectId'], '$BENEFIT', r['ObjectId'].lower()) 
                                for r in self.config_vars[key][3] if r['ObjectType'] == 'PS']
        else:
            print ('ERROR programs DB not loaded')
        self.__setattr__(key, programs_db)
        
    def load_reasontext_db(self, key):
        reasontext_db = []
        if self.config_vars[key][3]:
            reasontext_db = [(r['ReasonText'], '$LOCKREASON', self.process_search_text(r['ReasonText'])) 
                                for r in self.config_vars[key][3]]
        else:
            print ('ERROR: reasontext not loaded')
        self.__setattr__(key, reasontext_db)
        
    def load_identifier_db(self, key):
        identifier_db = []
        if self.config_vars[key][3]:
            identifier_db = [(r['BPIdType'], '$IDType', r['description'].lower()) 
                                for r in self.config_vars[key][3]]\
                        + [(r['BPIdType'], '$IDType', r['BPIdType'].lower()) 
                                for r in self.config_vars[key][3]]
        else:
            print ('ERROR: identifier type not loaded')
        # print(identifier_db)
        self.__setattr__(key, identifier_db)

    # def load_rules(self, key):
    #     sheet = xlrd.open_workbook(self.config_vars['rules'][1]).sheet_by_index(self.config_vars['rules'][2])
    #     rules = []
    #     for i in range(1, sheet.nrows):
    #         rules.append(Rule(sheet.cell_value(i, 0), sheet.cell_value(i, 1)))
    #     self.__setattr__('rules', rules)
        
    def get_value_from_dict(self, d, path):
        val = d
        for k in path.split('.'):
            if isinstance(val, dict):
                val = val.get(k)
            elif isinstance(val, list) and k.isdigit():
                val = val[int(k)]
            else:
                val = None
                break
        return val
