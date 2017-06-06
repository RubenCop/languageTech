#!/usr/bin/python3

import sys
import requests
import re
import spacy
    
def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def find_entity(entity):
    url = 'https://www.wikidata.org/w/api.php'
    params = {'action':'wbsearchentities',
              'language':'en',
              'format':'json'}
    if entity.split(' ', 1)[0] == 'a' or entity.split(' ', 1)[0] == 'the' or entity.split(' ', 1)[0] == 'an':
        entity = entity.split(' ', 1)[1]
    params['search'] = entity
    json = requests.get(url, params).json()
    if ['search']:
        returnQ = json['search'][0]['id']
        if (test_ambiguation(returnQ)):
            returnQ = json['search'][1]['id']
            return returnQ
        else:
            return returnQ
    else:
        return uri_from_anchor_texts(entity)


def find_property(property):
    url = 'https://www.wikidata.org/w/api.php'
    params = {'action':'wbsearchentities',
              'language':'en',
              'format':'json',
              'type': 'property'}
    if property.split(' ', 1)[0] == 'a' or property.split(' ', 1)[0] == 'the' or property.split(' ', 1)[0] == 'an':
        property = property.split(' ', 1)[1]
    params['search'] = property.rstrip()
    json = requests.get(url, params).json()
    if ['search'][0]:
        return json['search'][0]['id']
    return ('not found')


def test_ambiguation(returnQ):
    qNumber = returnQ
    pNumber = 'P31'
    name = fire_query(pNumber,qNumber)
    return (name.split(' ', 1)[0]  == 'Wikimedia')

def create_query(property, entity):
    if  entity and property:
        qNumber = find_entity(entity)
        pNumber = find_property(property)
    else:
        return('Could not parse entity or property')
    return fire_query(pNumber, qNumber)




def fire_query(pNumber, qNumber):
    if pNumber == 'not found' or qNumber == 'not found':
        return('Could not find the answer')
    else:
        url = 'https://query.wikidata.org/sparql'
        query = 'SELECT ?itemLabel  WHERE {wd:'+ qNumber + ' wdt:' + pNumber + ' ?item . SERVICE wikibase:label {bd:serviceParam wikibase:language "en" .}}' #create the query from the found Q and P numbers
        data = requests.get(url, params={'query': query, 'format': 'json'}).json()
        if not data['results']['bindings']: #is empty
            return('No results from query')
        else:
            for item in data['results']['bindings']:
                for var in item:
                    return('{}\t'.format(item[var]['value']))

def create_query_yesno(property, entity, answer):
    if property:
        if  entity and property and answer:
            qNumber = find_entity(entity)
            pNumber = find_property(property)
            answerNumber = find_entity(answer)
        else:
            print('No')
            return 0
        return fire_query_yesno(pNumber,qNumber,answerNumber)
    else:
        qNumber = find_entity(entity)
        answerNumber = find_entity(answer)
        if fire_query_yesno2(qNumber, answer) == 'Yes':
            return ('Yes')
        else:
            return fire_query_yesno2(answerNumber, entity)



def fire_query_yesno(pNumber, qNumber, answerNumber):
    url = 'https://query.wikidata.org/sparql'
    query = 'ASK {wd:'+qNumber+' wdt:'+pNumber+' wd:'+answerNumber+'.}'
    data = requests.get(url, params={'query': query, 'format': 'json'}).json()
    if data['boolean']:
        return('Yes')
    else:
        return('No')


def fire_query_yesno2(qNumber, answer):
    url = 'https://query.wikidata.org/sparql'
    query =  'SELECT ?valLabel WHERE { wd:'+qNumber+' ?prop ?val  SERVICE wikibase:label {bd:serviceParam wikibase:language "en"}}'
    data = requests.get(url, params={'query': query, 'format': 'json'}).json()
    if not data['results']['bindings']:  # is empty
        return ('No results from query')
    else:
        for item in data['results']['bindings']:
            for var in item:
                if format(item[var]['value']).lower() == answer.lower():
                    return ('Yes')
        return('No')




def create_query_count(property, entity):
    if  entity and property:
        qNumber = find_entity(entity)
        pNumber = find_property(property)
    else:
        print('Could not parse entity or property')
        return 0
    return fire_query_count(qNumber, pNumber)


def create_query_description(entity):
    if  entity:
        qNumber = find_entity(entity)
    else:
        print('Could not parse entity or property')
        return 0
    return fire_query_description(qNumber)


def fire_query_description(qNumber):
    if qNumber == 'not found':
        print('Could not find the answer')
    else:
        url = 'https://query.wikidata.org/sparql'
        #query = 'SELECT ?itemLabel  WHERE {wd:'+ qNumber + ' ?item . SERVICE ?item schema:description {bd:serviceParam wikibase:language "en" .}}' #create the query from the found Q and P numbers
        query = 'SELECT ?itemLabel WHERE {wd:' + qNumber + ' schema:description ?itemLabel . FILTER(LANG(?itemLabel) = "en")}'	#altered query, needs testing
        data = requests.get(url, params={'query': query, 'format': 'json'}).json()

        if data: #description is empty in wikidata, look for instance of attribute
            # check P279, subclass of
            query = 'SELECT ?food ?foodLabel WHERE { wd:' + qNumber + ' wdt:P279 ?food . SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }'
            data = requests.get(url, params={'query': query, 'format': 'json'}).json()
        if data:
            #check P31, instance of
            query = 'SELECT ?food ?foodLabel WHERE { wd:' + qNumber + ' wdt:P31 ?food . SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }'
            data = requests.get(url, params={'query': query, 'format': 'json'}).json()
        for item in data['results']['bindings']:
            for var in item:
                if isint(format(item[var]['value'])):
                    print('{}\t'.format(item[var]['value']))


def fire_query_count(qNumber, pNumber):
    if pNumber == 'not found' or qNumber == 'not found':
        print('Could not find the answer')
    else:
        url = 'https://query.wikidata.org/sparql'
        query = 'SELECT ?itemLabel  WHERE {wd:'+ qNumber + ' wdt:' + pNumber + ' ?item . SERVICE wikibase:label {bd:serviceParam wikibase:language "en" .}}' #create the query from the found Q and P numbers
        data = requests.get(url, params={'query': query, 'format': 'json'}).json()
        count = 0
        if not data['results']['bindings']: #is empty
            print('No results from query')
        else:
            for item in data['results']['bindings']:
                for var in item:
                    if isint(format(item[var]['value'])):
                        print('{}\t'.format(item[var]['value']))
                    else:
                        count +=1
            if count:
                print (count)

def parse_sentence(sentence):
    global nlp
    result = nlp(sentence)
    entity = []
    property = []
    ofCheck = 0
    for w in result:
        #print (w.text +' '+ w.tag_ +' '+ w.dep_+ ' '+w.head.text)
        if w.dep_ == "pobj" or w.dep_ == "compound":
            if  w.tag_ == 'NNP' or w.tag_ == 'NN' or w.tag_ == 'NNS' or w.tag_ == 'NNPS':
                if ofCheck == 2:
                    property.append(w.text)
                    ofCheck = 3
                else:
                    entity.append(w.text)
        elif w.dep_ == "nsubj" or w.dep_ == "nsubjpass" or w.dep_ == "dobj" or  w.dep_ == 'attr':
            if w.tag_ == 'NN' or w.tag_ == 'NNS':
                property.append(w.text)
                if w.text == 'country' or w.text == 'place' or w.text == 'date':
                    ofCheck = 1
        elif ofCheck == 1 and w.text == 'of':
            ofCheck = 2
            property.append(w.text)
        elif w.text == 'consist' and w.dep_ == 'ROOT':
            property.append(w.text)
    return " ".join(property) , " ".join(entity)

def parse_sentence_yesno(sentence):
    nlp = spacy.load('en_default')
    result = nlp(sentence)
    entity = []
    property = []
    answer = []
    ofCheck = 0

    for w in result:
        print (w.text +' '+ w.tag_ +' '+ w.dep_+ ' '+w.head.text)
    return " ".join(property) , " ".join(entity), " ".join(answer)


def parse_sentence_description(sentence):

    return entity




def determine_question_kind(sentence):
    sentence = sentence.lower()
    if sentence.split(' ', 1)[0] == 'does' or sentence.split(' ', 1)[0] == 'is' or  sentence.split(' ', 1)[0] == 'can' or sentence.split(' ', 1)[0] == 'will' or sentence.split(' ', 1)[0] == 'are' or sentence.split(' ', 1)[0] == 'do':
        return 'yes/no'
    if sentence.split(' ', 1)[0] == 'how' and sentence.split(' ', 1)[1].split(' ', 1)[0] == 'many' or sentence.split(' ', 1)[1].split(' ', 1)[0] == 'much':
        return 'count'
    sntnc = sentence.split()
    if len(sntnc) < 5 and sntnc[0] == 'what' and sntnc[1] == 'is' or sntnc[1] == 'are' :
        return 'description'
    return 'propertyEntity'

def main(argv):
    # print_example_queries()
    while(True):
        print('\nWhat would you like to know?')
        for line in sys.stdin:
        # entity = 'John Lennon'
        # answer = 'Rock music'
        # property = ''
        # print(create_query_yesno(property, entity, answer))

            questionType = determine_question_kind(line)
            print (questionType)
            if questionType == 'yes/no':
                property, entity, answer = parse_sentence(line)#_yesno(line)
                print ('property =' + property)
                print ('entity = '+ entity)
                print ('answer =' + answer)
                print(create__query_yesno(property, entity, answer))

            elif questionType == 'count':
                property, entity = parse_sentence(line)
                print(create_query_count(property, entity))

            elif questionType == 'description':
                entity = parse_sentence(line)#_description(line)
                print(create_query_description(entity))

            elif questionType == 'propertyEntity':
                property, entity = parse_sentence(line)
                print("property: ", property)
                print("entity: ", entity)
                print('answer: ',create_query(property, entity))
            break

if __name__ == "__main__":
    nlp = spacy.load('en_default') #load once for higher efficiency
    main(sys.argv)
