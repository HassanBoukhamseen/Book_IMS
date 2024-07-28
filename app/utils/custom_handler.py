from langchain.callbacks.base import BaseCallbackHandler
import re

class IntentCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.cleaned_query = ""
        self.intent = {}

    def process_query(self, user_input: str):
        self.cleaned_query = user_input

        # Extract year if mentioned
        year_match = re.search(r'\b\d{4}\b', user_input)
        if year_match:
            self.intent['year'] = year_match.group()
            self.cleaned_query = re.sub(r'\b\d{4}\b', '', self.cleaned_query).strip()

        # Extract author if mentioned
        author_match = re.search(r'author (.+)', user_input, re.IGNORECASE)
        if author_match:
            self.intent['author'] = author_match.group(1).strip()
            self.cleaned_query = re.sub(r'author (.+)', '', self.cleaned_query, flags=re.IGNORECASE).strip()

        return self.cleaned_query, self.intent
