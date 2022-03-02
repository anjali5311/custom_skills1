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
#sample
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
    logging.info('Python HTTP trigger function processed a request.')
    content = req.params.get('content')
    if not content:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            content = req_body['content']

    if content:
        noun_phrases=get_noun_phrases(content)
        return func.HttpResponse(json.dumps({'noun_phrases':noun_phrases}),status_code=200)
    else:
        return func.HttpResponse(json.dumps({'noun_phrases':[]}),status_code=404)
