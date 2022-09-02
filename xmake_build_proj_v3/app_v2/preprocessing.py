import re
from deeppavlov import build_model, configs
from query_processor.parsing import Rule, is_lexical

class Preprocess():
	""" Class to preprocess the query string. It includes the spelling correction model """
	def __init__(self, 
				config_path=configs.spelling_correction.brillmoore_wikitypos_en, 
				use_spell_corrector=True, 
				download=False):
		self.use_spell_corrector = use_spell_corrector
		if self.use_spell_corrector:
			self.model = build_model(config_path, download=download)
		# self.exclude=set()
		self.include=set()

	def load_include_set(self,rules):
		""" Defines a set of words which must be corrected by spelling model """
		try:
			string1=""
			for rule in rules:
				if is_lexical(rule):
					string1 += ' '.join(rule.rhs)
					string1 +=" "
			string1 = re.sub(r'[\t\n\r\f]', ' ', re.sub(r'[^a-zA-Z0-9\-\_\s]+', '', string1))
			string1 = string1.upper()
			self.include=set(string1.split())
			print("include set: ", self.include)
		except AttributeError as e:
			print("Cannot identify words to include for spelling correction... going by the standard list.")
			self.include=set(['postal','lock','locked',
								'external','payment','receive',
								'stop','block','active',
								'transaction','deduction','bank',
								'account'])

		
	def load_exclude_set(self,entity_db):
		""" Defines a set of words which must be excluded by spelling model """
		try:
			string1=""
			for rule in entity_db:
				a,b,c=rule
				string1 += a+" "+c+" "	
			string1 += "Payid"
			string1 = re.sub(r'[\t\n\r\f]', ' ', re.sub(r'[^a-zA-Z0-9\-\_\s]+', '', string1))
			string1 = string1.upper()
			self.exclude=set(string1.split())
			# print(self.exclude)
		except AttributeError as e:
			print("Cannot identify words to ignore for spelling correction... going by the standard dictionary.")
			self.exclude=set(['CRN','CENTRELINK','MEDICAREADM','PAYID','BSB','Bank','AUD','PAYGRP_CCS'])

	def initial_preprocess(self, string1):
		# print("intial prprocessing is being done")
		return re.sub(r'[\s]+', ' ', re.sub(r'[^a-zA-Z0-9\-\_\s]+', '', string1)).strip()

	def to_lower(self,string1):
		return string1.lower()

	def to_upper(self,string1):
		return string1.upper()

	def deeppavlov_spelling(self, string1):

		if self.use_spell_corrector:

			tokens1 = string1.split()
			# print (tokens1)
			out = self.model([string1])[0]
			# print("got string " + out)

			out = out.replace(' _ ', '_')
			tokens2 = out.split()
			# print (tokens2)
			for i, t in enumerate(tokens2):
				if t.upper() not in self.include:
					tokens2[i] = tokens1[i]
			out = ' '.join(t for t in tokens2)
			# print("returning string "+out)
			return out
		else:
			return string1

if __name__ == '__main__':
	query="Show details of payments with External Key AP_ForcedA4_K101"
	preprocessor = Preprocess()
	q = preprocessor.initial_preprocess(query)
	# print(preprocess(query).to_lower())
	print (preprocessor.deeppavlov_spelling(q))