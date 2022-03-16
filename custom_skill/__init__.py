import logging

import azure.functions as func
from nltk import word_tokenize, pos_tag, ne_chunk
import nltk
import json
from nltk import RegexpParser
from nltk import Tree
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')


#Function to extract nouns from a given content
def get_noun_phrases(text, chunk_func=ne_chunk):
    continuous_chunk=[]
    if isinstance(text,str):
        chunked = chunk_func(pos_tag(word_tokenize(text)))
        continuous_chunk = []
        current_chunk = []

        for subtree in chunked:
            if type(subtree) == Tree:
                current_chunk.append(" ".join([token for token, pos in subtree.leaves()]))
            elif current_chunk:
                named_entity = " ".join(current_chunk)
                if named_entity not in continuous_chunk:
                    continuous_chunk.append(named_entity)
                    current_chunk = []
            else:
                continue

    return continuous_chunk

def main(req: func.HttpRequest) -> func.HttpResponse:
    # refer the link to see the input schema https://docs.microsoft.com/en-us/azure/search/cognitive-search-custom-skill-web-api#sample-input-json-structure

    try:
            
            req_body = req.get_json()
            values=req_body.get('values')
            print(values)
            
    except Exception as e:
            return func.HttpResponse(json.dumps(outputs),mimetype="application/json",status_code=404)
    
    # refer to see this output schema https://docs.microsoft.com/en-us/azure/search/cognitive-search-custom-skill-web-api#sample-output-json-structure
    # The response should follow the format mentioned in the above link
    outputs={'values':[]}
    for item in values:
        try:
            item_results={'recordId':-1,'data':dict(),'errors':[],"warnings":None}
            assert 'recordId' in item.keys()
            item_results['recordId']=item['recordId']
            assert 'data' in item.keys()
            content = item['data']['content'] 
            assert content != None
            noun_phrases=get_noun_phrases(content) #calls the function to get the nouns from the given content
            
            item_results['data']['noun_phrases']=noun_phrases 
            #The 'noun_phrases' key name has to match with 'names' key-value mentioned in skillset definition 
            
            item_results['data']['email_metadata']={"noun_phrases":noun_phrases,"noun":noun_phrases} 
            #The 'email_metadata' key name has to match with the 'names' key-value mentioned in the skillset definition. 
            #Also the key names 'noun_phrases','noun' in the dictionary has to match with the sub-field names of the main field email_metadata as defined while indexing.
            
        except Exception as e:
            item_results['errors']={'messages':str(e)}
        outputs['values'].append(item_results)

    return func.HttpResponse(json.dumps(outputs),mimetype="application/json",status_code=200)
