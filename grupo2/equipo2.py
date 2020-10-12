import re
import pandas as pd
import bs4
import requests
import spacy
import os


from spacy.matcher import Matcher
from spacy.tokens import Span
from spacy.pipeline import EntityRuler
from spacy.matcher import Matcher

import networkx as nx

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from tqdm import tqdm

import array as arr


pd.set_option('display.max_colwidth', 200)

nlp = spacy.load('es_core_news_lg')

matcher = Matcher(nlp.vocab)
nucleo = [{"DEP": "nsubj"}] #Caso 1 -"Los kayakistas contratan travesías en kayak."

nucleoMD = [ {"DEP": "nsubj"}, {"DEP":"amod"}] #Caso 2 - "Los kayakistas expertos contratan travesías en kayak."
nucleoMI = [ {"DEP" : "nsubj"}, {"POS":"ADP"}, {"POS":"NOUN"}] #Caso 3.1 - "Los kayakistas de Córdoba contratan travesías en kayak."
nucleoMIv1 = [ {"DEP" : "nsubj"}, {"POS":"ADP"}, {"POS":"DET"}, {"POS":"NOUN"}, {"POS":"ADJ"}]
nucleoMIv2 = [ {"DEP" : "nsubj"}, {"POS":"ADP"},  {"POS":"DET"}, {"POS":"NOUN"}] #Caso 3.2 - "Los kayakistas de la montaña contratan travesías en kayak."
nucleoMIv3 = [ {"DEP" : "nsubj"}, {"POS":"ADP"},  {"DEP":"nmod"}] #Caso 3.3 - "Los kayakistas del pantano contratan travesías en kayak."
nucleoMDMI = [ {"DEP": "nsubj"}, {"DEP":"amod"}, {"POS":"ADP"}, {"POS":"NOUN"}] #Caso 4.1 - "Los kayakistas expertos de Córdoba contratan travesías en kayak."
nucleoMDMIv2 = [ {"DEP": "nsubj"}, {"DEP":"amod"}, {"POS":"ADP"},  {"POS":"DET"}, {"POS":"NOUN"}] #Caso 4.2 - "Los kayakistas expertos de la montaña contratan travesías en kayak."
nucleoMDMIv3 = [ {"DEP": "nsubj"}, {"DEP":"amod"},{"POS":"ADP"},  {"DEP":"nmod"}] #Caso 4.3 - "Los kayakistas expertos del pantano contratan travesías en kayak."


matcher.add("Nucleo", None, nucleo)
matcher.add("NucleoMD", None, nucleoMD)
matcher.add("NucleoMI", None, nucleoMI)
matcher.add("NucleoMIv1", None, nucleoMIv1)
matcher.add("NucleoMIv2", None, nucleoMIv2)
matcher.add("NucleoMIv3", None, nucleoMIv3)
matcher.add("NucleoMDMI", None, nucleoMDMI)
matcher.add("NucleoMDMIv2", None, nucleoMDMIv2)
matcher.add("NucleoMDMIv3", None, nucleoMDMIv3)


ruler= EntityRuler(nlp)
pattern1= [{'label': 'ORG', 'pattern': 'Hoy duermo afuera'}]
pattern2= [{'label': 'ORG', 'pattern': 'travesías en kayak'}]

ruler.add_patterns(pattern1)
ruler.add_patterns(pattern2)

nlp.add_pipe(ruler)


class Tool():
    def __init__(self):
        self.__entity_pairs = []
        self.__candidate_sent = None
        self.__df = None

    def loadParagraph(self, sentences):
        self.__candidate_sent = sentences

    def loadFile(self, file):
        f = open(file, "r")
        self.__candidate_sent = f.readlines()
        f.close()

    def run(self):
        self.__buildKG()

    def printKG(self):
        print(self.__df)

    def printVisualGraph(self):
        plt.figure(figsize=(12,12))
        G = nx.from_pandas_edgelist(df=self.__df, source='Entidad1', target='Entidad2', edge_attr='relacion',
                                   create_using=nx.DiGraph())
        pos = nx.spring_layout(G, k=5)  # nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos = pos)
        nx.draw(G, pos, with_labels=True, node_color='pink', node_size=2000)
        labels = {e: G.edges[e]['relacion'] for e in G.edges}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        plt.show()

    def printUML(self):
        uml= UMLProcessing()
        uml.goWork(self.getDF())

    def getDF(self):
        return self.__df



    def __buscarPosicionVerbo(self, doc):
        posVerbo=-1
        for i in range(0, len(doc)):
            if (posVerbo == -1):
                if (doc[i].pos_ == "VERB" or doc[i].dep_ == "ROOT"):
                    posVerbo= i
                if (doc[i].lemma_ == "ser"):
                    posVerbo= i
                    if (doc[i+1].dep_ == "ROOT"):
                        posVerbo= i+1
        return posVerbo

    #Yo tengo que encontrar la forma de la oración. Si es VERBO + OD. O VERBO+OD+OI. Si supongo que tienen ese formato, entonces
    #puedo preguntar si, lo que está "a continuación del verbo" es el OD. Y si lo que está "a continuación del OD" es el OI. ¿Manejarse con las posiciones?
    #Es absolutamente necesario, PARA ESTA IMPLEMENTACIÓN que la oración termine con punto. Sino producirá error.

    def __buscarObjetos(self, doc):
        posVerbo= -1
        od=""
        oi=""
        ind=0
        posOD=0
        posOI = None
        ret=[]

        if (od==""):
            posVerbo= self.__buscarPosicionVerbo(doc)+1

            for i in range(posVerbo, len(doc)):
                if (doc[i].pos_ == "NOUN" and doc[i].dep_ == "nmod") or (doc[i].dep_ == "obj" and (doc[i].pos_ == "NOUN" or doc[i].pos_ =="PROPN" or doc[i].pos_=="PRON" or doc[i].pos_=="ADJ")) or doc[i].dep_== "obl" or (doc[i].dep_ == "ROOT" and (doc[i].pos_ =="NOUN" or doc[i].pos_=="ADJ" or doc[i].pos_ =="PROPN" )):
                    if (ind == 0): #el "ind" se está usando para marcar si había o no modificador, si hay queda en 1
                        od=doc[i].text
                        if (doc[i+1].pos_ == "ADP" and doc[i+1].text != "al" and doc[i+1].text != "a" and doc[i+1].text != "para"): #evalúa si el OD tenía al lado un modificador indirecto
                            if (doc[i+2].dep_ == "nmod"):
                                od= od+" "+doc[i+1].text+" "+doc[i+2].text
                                i=i+2
                        else:                       #o un modificador directo
                            if (doc[i+1].pos_ == "ADJ"):
                                od=od+" "+doc[i+1].text
                                i=i+1
                        ind=ind+1
                        posOD=i+1

        if (doc[posOD].text !="."): #evita error. parche. lpm
            for i in range(posOD, len(doc)):
            #Evaluará hallar un OI DESPUÉS del OD (para eso usa posOD)
                if (doc[i].text == "para" or doc[i].text == "a" or doc[i].text == "al"): #El OI está encabezado por a / para
                    posOI = i
                    break
            if (posOI != None):
                for i in range(posOI, len(doc)):
                    if (doc[i].dep_ == "ob" or doc[i].dep_ == "nmod" or doc[i].dep_=="obl"):
                        oi=doc[i].text
                        if (doc[i+1].pos_ == "ADP"): #evalúa si el OI tenía al lado un modificador indirecto
                            if (doc[i+2].dep_ == "nmod" or doc[i+2].pos_ == "NOUN"):
                                oi= oi+" "+doc[i+1].text+" "+doc[i+2].text

                        else:                       #o un modificador directo
                            if (doc[i+1].pos_ == "ADJ" or doc[i+1].dep_=="nmod" or doc[i+1].dep_=="amod"):
                                oi=oi+" "+doc[i+1].text
                        break

        return [od, oi]


    def __get_ent(self, sent):
        ent=""
        for i in sent.ents:
            ent=ent+i.text
        return ent

    def __get_entities(self, sent):
        ent1 = ""
        ent2 = ""
        obj= []
        ent = ""
        span= ""

        sent=nlp(sent)

        #Me fijo si encontré ent es porque descubrí una entidad, podría ser el núcleo? En realidad debería fijarse si es parte del sujeto esa entidad (si está antes del verbo?)
        #Hay un matcher para esto. No logré hacer que funcione, puse {"ENT_TYPE":"ORG"}
        if (ent!=""):
            ent1=ent
        else:
            #Mando a matchear con todos los patrones posibles. Devolverá el sujeto que sea correcto.
            matches = matcher(sent)
            for match_id, start, end in matches:
                string_id = nlp.vocab.strings[match_id]  # Get string representation
                span = sent[start:end]  # The matched span
            ent1=str(span)

        obj=self.__buscarObjetos(sent)
        if (obj[1]!=""): #si tiene OI, la 2da ent es el OI porque la relacion va a ser el verbo+od
            ent2=obj[1]
        else:
            ent2=obj[0] #sino, la 2da ent es el od como siempre

        return [ent1.strip(), ent2.strip()]

    # "la relación puede ser todo lo que esté entre las dos entidades"
    # ser + participio // ser // ser un // ser un + oi
    #  Verbo solo //  pron + verbo + prep // verbo + oi

    def __get_relation(self, sent):
        rel=""

        tieneOI = False
        obj = self.__buscarObjetos(nlp(sent))
        if obj[1] != "":
            tieneOI= True

        ents = self.__get_entities(sent)
        fine1 = sent.find(ents[0]) + len(ents[0]) +1
        inie2 = sent.find(ents[1]) -1

        x = sent[fine1:inie2]
        doc= nlp(x)

        # si es "es" o el verbo solo, no pierdo tiempo, ya lo retorno
        if (len(doc) == 1):
            return x.strip()

        if (tieneOI):
            pos =  0
            while (pos < len(doc)):
                if (doc[pos].text == "a" or doc[pos].text == "al" or doc[pos].text == "para"):
                    break

                if (doc[pos].pos_ != "DET"):
                    rel = rel+ " "+doc[pos].text
                pos+=1
        else:
            pos =  0
            while (pos < len(doc)):
                if (doc[pos].pos_ != "DET") or (doc[pos].pos_ == "DET" and doc[pos].text == "un"):
                    rel = rel+ " "+doc[pos].text
                pos+=1

        return(rel.strip())

    def __buildKG(self):

        for sentence in self.__candidate_sent:
            self.__entity_pairs.append(self.__get_entities(sentence))
        relations = [self.__get_relation(i) for i in self.__candidate_sent]
        source = [i[0] for i in self.__entity_pairs]
        target = [i[1] for i in self.__entity_pairs]
        self.__df = pd.DataFrame({'Entidad1': source, 'relacion': relations, 'Entidad2': target})


class Clase():
    def __init__(self):
        self.__nombre= ""
        self.__variablesInstancia= []
        self.__metodos= []
        self.__subclases= []

    def getMetodos(self):
        return self.__metodos

    def getSubclases(self):
        return self.__subclases

    def getVariablesInstancia(self):
        return self.__variablesInstancia

    def getNombre(self):
        return self.__nombre

    def addMetodo(self, metodos):
        self.__metodos.append(metodos)

    def setMetodos(self, metodos):
        self.__metodos =metodos

    def addSubclase(self, subclases):
        self.__subclases.append(subclases)

    def setSubclases(self, subclases):
        self.__subclases=subclases

    def addVariableInstancia(self, vi):
        self.__variablesInstancia.append(vi)

    def setNombre(self, nombre):
        self.__nombre= nombre

class UMLProcessing():
    def __init__(self):
        self.__lista_final= []

    #esto es para saber si la relacion es verbo +od o verbo solo
    def __determinarRelacion(self, rel, ent2):
        relacion=nlp(rel)
        temp= ""
        tieneOI = False
        for i in relacion:
            if (i.dep_ == "obj" or i.dep_ == "nsubj"):
                tieneOI= True

            if (i.dep_ == "ROOT"):
                temp= temp+" "+str(i.lemma_).strip()
            else:
                temp=temp+" "+str(i).strip()

        if not tieneOI:
            rel= temp+ " "+ent2
        else:
            rel= temp
        return rel.strip()


    def __clase_existente(self, lista_clases, nombre_clase):
        for clase in lista_clases:
            if (nombre_clase == clase.getNombre()):
                return clase
        return None

    def __es_variable(self, relacion):
        rel=nlp(relacion)
        return (rel[0].lemma_ == "tener") and (len(rel) == 1)

    def __buscar_subclases(self, lemma, lista_clases, nombre_superclase, dicLemma):
        subclases=[]
        for clase in lista_clases:
            if (not clase.getNombre() in dicLemma.values()):
                if (nlp(clase.getNombre())[0].lemma_ == lemma):
                    subclases.append(clase)
        return subclases

    def __es_subclase(self, buscada):
        for clase in self.__lista_final:
            if (buscada in clase.getSubclases()):
                return True
        return False

    def __procesamientoUNO(self, df):
        #PROCESAMIENTO 1
        #------------------------------------------------------------------------------------------------------------------
        # A partir del df, hago una lista de posibles clases, con sus respectivos métodos y variables

        lista_clases= []
        for index, row in df.iterrows():
            existe= self.__clase_existente(lista_clases, row['Entidad1'])
            if (existe == None):
                nueva= Clase()
                nueva.setNombre(row['Entidad1'])
                if (self.__es_variable(row['relacion'])):
                    nueva.addVariableInstancia(row['Entidad2'])
                else:
                    rel= self.__determinarRelacion(row['relacion'], row['Entidad2'])
                    nueva.addMetodo(rel)
                lista_clases.append(nueva)
            else:
                if (self.__es_variable(row['relacion'])):
                    existe.addVariableInstancia(row['Entidad2'])
                else:
                    rel= self.__determinarRelacion(row['relacion'], row['Entidad2'])
                    existe.addMetodo(rel)
        return lista_clases

    def __procesamientoDOS(self, lista_clases):
        #PROCESAMIENTO 2
        # ---------------------------------------------------------------------------------------------------------------------------
        #Establezco jerarquias.. Por cada una de las enntidades, voy a mirar si el ENTIDAD=LEMA.
        # Una vez que encuentro ENTIDAD=LEMA, voy a recorrer la lista buscando todas las jerarquias y reacomodando los ptros

        dicLemma = dict()
        for clase in lista_clases:
            dicLemma[clase.getNombre()]=nlp(clase.getNombre())[0].lemma_


        for clase in lista_clases:
            if (dicLemma[clase.getNombre()] == clase.getNombre()):     #procesara las de mismo lema y nombre
                clase.setSubclases(self.__buscar_subclases(dicLemma[clase.getNombre()], lista_clases, clase.getNombre(), dicLemma))
                if (len(clase.getSubclases())>0):
                    self.__lista_final.append(clase)

        #Una vez que establecí jerarquías, proceso todo lo que no sea jerarquía (ni clase, ni subclase de esa clase)
        for clase in lista_clases:
            if (not self.__es_subclase(clase) and not clase in self.__lista_final):
                cantidad_variables= len(clase.getVariablesInstancia())
                cantidad_metodos= len(clase.getMetodos())
                if ((cantidad_variables+cantidad_metodos)>1):
                    self.__lista_final.append(clase)

        #Set con todos los métodos para eliminar repeticiones
        for clase in self.__lista_final:
            for subclase in clase.getSubclases():
                subclase.setMetodos(set(subclase.getMetodos()))
            clase.setMetodos(set(clase.getMetodos()))

    def __processing(self, df):
        lista_clases= self.__procesamientoUNO(df)
        self.__procesamientoDOS(lista_clases)

    def __generateUMLFile(self):
        file = open("Test.txt", "w")
        print("\"")

        file.write("@startuml" + os.linesep) # inicio del archivo :D kk
        for clase in self.__lista_final:
            file.write("class \""+clase.getNombre()+ "\" {" + os.linesep)
            for variable in clase.getVariablesInstancia():
                file.write(variable + os.linesep)
            for metodo in clase.getMetodos():
                kk=""
                doc = nlp(metodo)
                for i in doc:
                    kk=kk+i.text+"_"
                file.write(kk+"()" + os.linesep)
            file.write("}" + os.linesep)  #cierro clase
            for subclase in clase.getSubclases():
                kk=""
                doc=nlp(subclase.getNombre())
                for i in doc:
                    kk=kk+i.text+"_"
                file.write("\""+clase.getNombre()+"\" <|-- "+"\""+subclase.getNombre()+"\""+ os.linesep)
                file.write("class \""+subclase.getNombre()+"\" {" + os.linesep)
                for variable in subclase.getVariablesInstancia():
                    file.write(variable + os.linesep)
                for metodo in subclase.getMetodos():
                    kk=""
                    doc = nlp(metodo)
                    for i in doc:
                        kk=kk+i.text+"_"
                    file.write(kk+"()"+ os.linesep)
                file.write("}" + os.linesep)
        file.write("@enduml" + os.linesep)
        file.close()

        os.system("java -jar plantuml.jar Test.txt")

    def goWork(self, df):
        self.__processing(df)
        self.__generateUMLFile()
