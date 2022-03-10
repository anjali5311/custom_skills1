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

"""
{
    "values": [
      {
        "recordId": "0",
        "data":
           {
             "content": "This is sample text",
           }
      }
}"""

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
    # {'content':'this is sample text'}

    try:
            
            req_body = req.get_json()
            values=req_body.get('values')
            print(values)
            
    except Exception as e:
            return func.HttpResponse(json.dumps(outputs),mimetype="application/json",status_code=404)

    outputs={'values':[]}
    for item in values:
        try:
            item_results={'recordId':-1,'data':dict(),'errors':[],"warnings":None}
            assert 'recordId' in item.keys()
            item_results['recordId']=item['recordId']
            assert 'data' in item.keys()
            content = item['data']['content']
            assert content != None
            noun_phrases=get_noun_phrases(content)
            item_results['data']['noun_phrases']=noun_phrases
            item_results['data']['email_metadata']={"noun_phrases":noun_phrases,"noun":noun_phrases}
        except Exception as e:
            item_results['errors']={'messages':str(e)}
        outputs['values'].append(item_results)

    return func.HttpResponse(json.dumps(outputs),mimetype="application/json",status_code=200)
