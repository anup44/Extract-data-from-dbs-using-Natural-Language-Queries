from query_processor.utility_functions import KeyDefaultDict
from query_processor.intent_map import intent_field_map
from query_processor.date_logic import from_to_date


class FieldConverter():
    def __init__(self, fields=[]):
        self.fields = KeyDefaultDict(lambda key: Field(key))
        self.add_fields(fields)

    def field_selection(self, parse_semantics):
        field_set = set(intent_field_map[parse_semantics['TYPE']])
        field_set.add('TYPE')
        for key in set(parse_semantics.keys()):
            if key not in field_set:
                parse_semantics.pop(key)

    def convert_fields(self, parse_semantics):
        for key, field in self.fields.items():
            if set(key) <= parse_semantics.keys():
                parse_semantics.update(field.field_conversion_func(*[parse_semantics.pop(field_name) 
                                                                    for field_name in field.field_names]))

    def add_fields(self, fields):
        for field in fields:
            self.fields[field.field_names] = field

    def generate_filter(self, parse_semantics):
        filters = []
        for key in parse_semantics:
            field = self.fields[(key,)]
            filters.append(field.transfer_func(parse_semantics[key]))
        return [f for f in filters if f]


class Field():
    def __init__(self, field_name, field_conversion_func=None, transfer_func=None):
        self.field_names = tuple(field_name.split()) if isinstance(field_name, str) else field_name
        if field_conversion_func:
            self.field_conversion_func = field_conversion_func
        else:
            self.field_conversion_func = lambda val: {field_name: val}
        if transfer_func:
            self.transfer_func = transfer_func
        else:
            self.transfer_func = lambda val: self.field_names[0] + " eq '" + str(val) + "'"

    def __str__(self):
        return 'Field' + str((' '.join(self.field_names), self.transfer_func))


fields_1 = [
    Field('IDFull', 
        lambda val:{'BPIdentificationType':val.split()[0],'BPIdentificationNumber':val.split()[1]}),
    Field('NAME', 
        lambda val: {'NAME': val.lower().split()}, 
        lambda val: "p_f_name='{}',p_m_name='',p_l_name='{}'".format(*val) if len(val) == 2 
            else "p_f_name='{}',p_m_name='{}',p_l_name='{}'".format(*val) if len(val) == 3 
            else "p_f_name='{}',p_m_name='',p_l_name=''".format(val[0])),
    Field('DATE DATE_', 
        lambda val1, val2: {'DATE': [val1.lower(), val2.lower()]}),
    Field('DATE', 
        lambda val: {'DATE': [val.lower()]} if isinstance(val, str) else {'DATE': val}, 
        lambda val: "PaymentDate ge datetime'{}' and PaymentDate le datetime'{}'".format(*from_to_date(val))),
    Field('MONEY', lambda val: {}),
    Field('Math_Operator', lambda val: {}),
    Field('name1', lambda val: {}),
    Field('name2', lambda val: {}),
    Field('TYPE DATE', 
        lambda val1, val2: {'TYPE': val1, 'DATE_' + val1: val2} 
            if val1 in ['Payment_Amount', 'Payment_Deduction'] else {'TYPE': val1, 'DATE': val2}),
    Field('DATE_Payment_Amount', None, 
        lambda val: "validfrom='{}',validto='{}'".format(*[x[:10].replace('-', '') for x in from_to_date(val)])),
    Field('POSTCODE', None, 
        lambda val: "postalcode='{}'".format(val)),
    Field('TYPE BPIdentificationNumber', 
        lambda val1, val2: {'TYPE': val1, 'BPIdentificationNumber_' + val1: val2} 
            if val1 == 'Payment_Deduction' else {'TYPE': val1, 'BPIdentificationNumber': val2}),
    Field('BPIdentificationNumber_Payment_Deduction', None, 
        lambda val: "((BPIdentificationNumber eq '"+ val +"'))"),
    Field('DATE_Payment_Deduction', None, 
        lambda val: "((StartDate ge '{}')) and ((EndDate le '{}'))".format(*[x[:10].replace('-','') 
                                                                            for x in from_to_date(val)])),
    # Field('TYPE', None, lambda val: ''),
    Field('TYPE', lambda val: {'TYPE': val + '.0'}, lambda val: ''),
    Field('TYPE BPIdentificationNumber NAME', 
        lambda val1, val2, val3: {'TYPE': val1.split('.')[0] + '.0', 'BPIdentificationNumber': val2}),
    Field('TYPE NAME', 
        lambda val1, val2: {'TYPE': val1.split('.')[0] + '.1', 'NAME': val2}),
    Field('TYPE_', lambda val: {}),
    Field('TYPE__', lambda val: {}),
    # Field('IDFull', lambda val:{'BPIdentificationType':val.split()[0],'BPIdentificationNumber':val.split()[1]})
]