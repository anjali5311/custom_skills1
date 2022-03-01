import logging

import azure.functions as func
import spacy
nlp = spacy.load('en_core_web_sm')

def get_noun_phrases(text):
    if isinstance(text,str):
        noun_phrases=[]
        doc = nlp(text)
        for nounpphrase in doc.noun_chunks:
            noun_phrases.append(nounpphrase.text)
        return noun_phrases
    else:
        return []

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
            content = req_body.get('content')

    if content:
        noun_phrases=get_noun_phrases(text)
        return func.HttpResponse(noun_phrases,status_code=200)
    else:
        return func.HttpResponse([], status_code=404)
