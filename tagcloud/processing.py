# all the imports
import xml.etree.ElementTree as ET
import re

class pre_processing:

	def __init__(self, filename):
		self.filename = filename

	def readXML(self):
		tree = ET.parse(self.filename)
		root = tree.getroot()
		atributes = []
		tags = []
		
		for child in tree.iter():
			for attr, val in child.attrib.iteritems():
				atributes.append(val)

		for child in tree.iter():
			if not child and child.text is not None:
				atributes.append(child.text)
				
		for x in atributes:
			
			x = x.replace(",", "")
			x = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',x)
			x = re.sub('\d+','',x)

			if not x.isdigit():
				
				split = x.split()
				stopWords = ['para', 'NAO_INFORMADO', 'NAO', 'SIM', 'de', 'do', 'da', 'impresso', 'completo', 'publicado', 'ainda', 'pelo', 'pela', 'entre', 'mais', 'outro', 'outra',
				'sobre', 'outros', 'OUTROS', 'OUTRO', 'outras', 'bem', 'BEM', 'CONCLUIDO', 'COMPLETO', 'ENDERECO_RESIDENCIAL', 'LATTES_OFFLINE', 'IMPRESSO', 'RAZOAVELMENTE', 'LIVRE', 'RESUMO', 'EM_ANDAMENTO'
				,'POUCO', 'ANTERIOR', 'PARECER', 'qual', 'isso', 'pode', '<BR>', '</B>', 'como', 'TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO', 'e/ou']
				removeStop = [w for w in split if w not in stopWords and (w.islower() and len(w) > 3 or w.isupper() and len(w) > 2)]
				# lowerTags = [low for low in split if low.islower() and len(low) > 3]
				# upperTags = [up for up in split if up.isupper() and len(up) > 2 ]
				# paraTags = [para for para in split if para!="para" and len(para) > 1]

				tags = tags + removeStop

		from collections import Counter
		counts = Counter(tags)

		response = []
		for x, c in counts.most_common():

			response.append({'text': x, 'size': c})

		return response