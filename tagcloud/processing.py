#!/usr/bin/python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import re

class pre_processing:

    def __init__(self, filename):
        self.filename = filename

    def removeAccents(self, word): #divida
        repl = {'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a',
                'é': 'e', 'ê': 'e', 'í': 'i',
                'ó': 'o', 'ô': 'o', 'õ': 'o', 'ç': 'c',
                'ú': 'u', 'ü': 'u', 
                'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A',
                'É': 'E', 'Ê': 'E', 'Í': 'I',
                'Ó': 'O', 'Ô': 'O', 'Õ': 'O',
                'Ú': 'U', 'Ü': 'U', 'Ç': 'C'}

        new_word = ''.join([repl[c] if c in repl else c for c in word])
        return new_word
    
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
            # import unidecode

            # #convert plain text to utf-8
            # x = unidecode.unidecode(x)
            x = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',x)
            x = x.replace(",", "")
            x = x.replace("'", "")
            x = x.replace("\"", "")
            x = x.replace("\\", "")
            x = x.replace(".", "")
            x = x.replace(":", "")
            x = x.replace("[", "")
            x = x.replace("]", "")
            x = x.replace("(", "")
            x = x.replace(")", "")
            x = x.replace(";", ".")
            x = x.replace("/", "")
           

            
            x = re.sub('\d+','',x)

            import sys  

            reload(sys)  
            sys.setdefaultencoding('utf8')
            
            x = x.replace("à", "a")
            x = x.replace("á", "a")
            x = x.replace("â", "a")
            x = x.replace("ã", "a")
            x = x.replace("ã", "a")
            x = x.replace("è", "e")
            x = x.replace("ê", "e")
            x = x.replace("í", "i")
            x = x.replace("ì", "i")
            x = x.replace("ó", "o")
            x = x.replace("ô", "o")
            x = x.replace("õ", "o")
            x = x.replace("ò", "o")
            x = x.replace("ú", "u")    
            x = x.replace("ü", "u")    
            x = x.replace("ç", "c")
            x = x.replace("ñ", "n")

            x = x.upper()

            x = x.replace("À", "A")
            x = x.replace("Á", "A")
            x = x.replace("Â", "A")
            x = x.replace("Ã", "A")
            x = x.replace("É", "E")
            x = x.replace("È", "E")
            x = x.replace("Ê", "E")
            x = x.replace("Í", "I")
            x = x.replace("Ì", "I")
            x = x.replace("Ó", "O")
            x = x.replace("Ô", "O")
            x = x.replace("Ò", "O")
            x = x.replace("Õ", "O")
            x = x.replace("Ú", "U")    
            x = x.replace("Ü", "U")    
            x = x.replace("Ç", "C")
            x = x.replace("Ñ", "N")
            

            if not x.isdigit():
                
                split = x.split()
                stopWords = ['PARA', 'NAO_INFORMADO', 'NAO', 'SIM', 'DE', 'DO', 'DA', 'IMPRESSO', 'COMPLETO', 'PUBLICADO', 'AINDA', 'PELO', 'PELA', 'ENTRE', 'MAIS', 'OUTRO', 'OUTRA', 'SOBRE', 'OUTROS', 'OUTRO', 'OUTRAS', 'BEM', 'CONCLUIDO', 'COMPLETO', 'ENDERECO_RESIDENCIAL', 'LATTES_OFFLINE', 'IMPRESSO', 'RAZOAVELMENTE', 'LIVRE', 'RESUMO', 'EM_ANDAMENTO','POUCO', 'ANTERIOR', 'PARECER', 'QUAL', 'ISSO', 'PODE', '<BR>', '</B>', '<B>', 'COMO', 'TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO', 'E/OU', 'QUE', 'DESQUALIFICACAOQUALIFICACAO', 'DOS', 'DDMMAAAA', 'ROGRADEADUNESPBR~TELEDUCPAGINA_INICIALCURSOS_ALLPHP?&TIPO_CURSO=F&COD_PASTA=', 'KROGER', 'S---']
                removeStop = [w for w in split if (w not in stopWords) and (w.isupper() and len(w) > 2)]
                # lowerTags = [low for low in split if low.islower() and len(low) > 3]
                # upperTags = [up for up in split if up.isupper() and len(up) > 2 ]
                # paraTags = [para for para in split if para!="para" and len(para) > 1]

                tags = tags + removeStop

        from collections import Counter
        counts = Counter(tags)

        response = []
        for x, c in counts.most_common():
            # palavra_repetida = [t['text'] for t in response if t['text'] == x]
            # if len(palavra_repetida) > 0:
            #   print palavra_repetida

            response.append({'text': x, 'size': c})

        return response


    def getName(self):

        tree = ET.parse(self.filename)
        root = tree.getroot()
        atributes = []
       

        for child in tree.iter('DADOS-GERAIS'):
            name = child.get('NOME-COMPLETO')
            # print name
        return name

    def getAutores(self):

        tree = ET.parse(self.filename)
        root = tree.getroot()
        tags = []

        for autor in tree.iter('AUTORES'):
            nomes = autor.get('NOME-COMPLETO-DO-AUTOR')
            tags.append(nomes)

        result = []
        for item in tags:
            if item not in result:
                 result.append(item)

        for x in result:
             
            x = re.sub('\d+','',x)

            import sys  

            reload(sys)  
            sys.setdefaultencoding('utf8')
            x = x.replace("'", "")
            x = x.replace("`", "")
            x = x.replace("D'A", "")
            x = x.replace("à", "a")
            x = x.replace("á", "a")
            x = x.replace("â", "a")
            x = x.replace("ã", "a")
            x = x.replace("ã", "a")
            x = x.replace("è", "e")
            x = x.replace("ê", "e")
            x = x.replace("í", "i")
            x = x.replace("ì", "i")
            x = x.replace("ó", "o")
            x = x.replace("ô", "o")
            x = x.replace("õ", "o")
            x = x.replace("ò", "o")
            x = x.replace("ú", "u")    
            x = x.replace("ü", "u")    
            x = x.replace("ç", "c")
            x = x.replace("ñ", "n")

            x = x.upper()

            
            x = x.replace("À", "A")
            x = x.replace("Á", "A")
            x = x.replace("Â", "A")
            x = x.replace("Ã", "A")
            x = x.replace("É", "E")
            x = x.replace("È", "E")
            x = x.replace("Ê", "E")
            x = x.replace("Í", "I")
            x = x.replace("Ì", "I")
            x = x.replace("Ó", "O")
            x = x.replace("Ô", "O")
            x = x.replace("Ò", "O")
            x = x.replace("Õ", "O")
            x = x.replace("Ú", "U")    
            x = x.replace("Ü", "U")    
            x = x.replace("Ç", "C")
            x = x.replace("Ñ", "N")

        print result
  
        return result
        # return response

    def getTitulos(self):

        tree = ET.parse(self.filename)
        root = tree.getroot()
        tags = []

        for titulo in tree.iter('DADOS-BASICOS-DO-TRABALHO'):
            titulos = titulo.get('TITULO-DO-TRABALHO')
            tags.append(titulos)

        result = []
        for item in tags:
            if item not in result:
                 result.append(item)

        for x in result:
             
            x = re.sub('\d+','',x)

            import sys  

            reload(sys)  
            sys.setdefaultencoding('utf8')
            x = x.replace("'", "")
            x = x.replace("`", "")
            x = x.replace("D'A", "")
            x = x.replace("à", "a")
            x = x.replace("á", "a")
            x = x.replace("â", "a")
            x = x.replace("ã", "a")
            x = x.replace("ã", "a")
            x = x.replace("è", "e")
            x = x.replace("ê", "e")
            x = x.replace("í", "i")
            x = x.replace("ì", "i")
            x = x.replace("ó", "o")
            x = x.replace("ô", "o")
            x = x.replace("õ", "o")
            x = x.replace("ò", "o")
            x = x.replace("ú", "u")    
            x = x.replace("ü", "u")    
            x = x.replace("ç", "c")
            x = x.replace("ñ", "n")

            x = x.upper()


            x = x.replace("À", "A")
            x = x.replace("Á", "A")
            x = x.replace("Â", "A")
            x = x.replace("Ã", "A")
            x = x.replace("É", "E")
            x = x.replace("È", "E")
            x = x.replace("Ê", "E")
            x = x.replace("Í", "I")
            x = x.replace("Ì", "I")
            x = x.replace("Ó", "O")
            x = x.replace("Ô", "O")
            x = x.replace("Ò", "O")
            x = x.replace("Õ", "O")
            x = x.replace("Ú", "U")    
            x = x.replace("Ü", "U")    
            x = x.replace("Ç", "C")
            x = x.replace("Ñ", "N")

        print result
  
        return result




