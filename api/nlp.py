# %%
import os
import os.path as osp
from textblob import Word, TextBlob
from nltk.stem import PorterStemmer
import nltk
from nltk.corpus import stopwords
import re
import contractions
from collections import Counter
import unicodedata
import json
import numpy as np
import itertools
#from utils.datetime_utils import *
import inflect
from sutime import SUTime

# %% [markdown]
# ## Get nltk necessary packages

# %%
home_path = osp.expanduser('~')
stopword_folder_path = osp.join(home_path, 'nltk_data', 'corpora', 'stopwords')
punkt_folder_path = osp.join(home_path, 'nltk_data', 'corpora', 'punkt')
averaged_perceptron_tagger_path = osp.join(home_path, 'nltk_data', 'averaged_perceptron_tagger')
if not osp.exists(stopword_folder_path):
    nltk.download('stopwords')
if not osp.exists(punkt_folder_path):
    nltk.download('punkt')
    
nltk.download('averaged_perceptron_tagger')
stop_words = stopwords.words('english')

# %% [markdown]
# ## Load dictionaries

# %%
def load_dictionary(dictionary_path):
    dictionary = [line.rstrip().split(' --> ') for line in open(dictionary_path, 'r').readlines()]
    tags = [item[1] for item in dictionary]
    dictionary = [item[0] for item in dictionary]
    return dictionary, tags

# %%
time_dictionary_path = os.path.join('dict', 'time_dictionary.txt')
location_dictionary_path = os.path.join('dict', 'location_dictionary.txt')
concept_dictionary_path = os.path.join('dict', 'concept_dictionary.txt')
time_dictionary, time_tags = load_dictionary(time_dictionary_path)
location_dictionary, location_tags = load_dictionary(location_dictionary_path)
concept_dictionary, concept_tags = load_dictionary(concept_dictionary_path)

# %% [markdown]
# ---

# %%
def extract_noun_phrases(pos_tags):

    def parse_noun_phrase(indices, num_tokens):
        """
        Input of this function is the indices of possible begining positions of a noun phrases and the number of tokens
        """
        noun_phrases = []
        for index in indices:
            noun_phrase_tokens = []
            adj_phrase_tokens = []
            has_noun = False
            has_cardinal = False
            for i in range(index + 1, num_tokens):
                token, tag = pos_tags[i]
                if tag == 'DT':      # If the current token is article, then we don't count it as a part of noun phrase.
                    if has_noun is True: break
                    else: continue
#                elif tag == 'CD':
#                    if has_cardinal is True: break # It is non-sense if two cardinal digits appear together
#                    adj_phrase_tokens.append(token) # If some cardinal digit appears before a noun, it is counted as an adjective
#                    has_cardinal = True
                elif tag in ['NN', 'NNS', 'NNP', 'NNPS']:   # Obviously
                    noun_phrase_tokens.append(token)
                    has_noun = True
                elif tag == 'JJ' or tag == 'RB':       # If the current token is adjective, it is the sign of the beginning of a noun phrases.
                    if has_noun is True: break      # If some nouns appear before the adjective token, it is not correct noun phrase --> therefore, stop.
                    adj_phrase_tokens.append(token)
                elif tag == 'IN':     # If current token is preposition
                    if has_noun is True and token == 'of': # Consider the "of" preposition in the noun phrase
                        noun_phrase_tokens.append(token)
                    else: break
                elif tag == 'VBG':      # If current token is gerund, it might be a noun
                    if i + 1 == num_tokens: continue
                    next_token, next_tag = pos_tags[i+1]
                    if i < 1 and next_tag in ['NN', 'NNS', 'NNP', 'NNPS']:
                        noun_phrase_tokens.append(token)
                        continue
                    prev_token, prev_tag = pos_tags[i-1] 
                    if prev_tag == 'IN' and prev_token == 'of' or next_tag in ['NN', 'NNS', 'NNP', 'NNPS']:
                        noun_phrase_tokens.append(token)
                else: break
            noun_phrase = ' '.join(noun_phrase_tokens)
            adj_phrase = ' '.join(adj_phrase_tokens)
            if len(adj_phrase_tokens) > 0 and len(noun_phrase) > 0:
                noun_phrase = adj_phrase + ' ' + noun_phrase
            if len(noun_phrase) > 0:
                noun_phrases.append(noun_phrase)
            else: continue 
        return noun_phrases
    num_tokens = len(pos_tags)
    noun_phrases = []

    # Brute force to find noun phrases
    indices = [i-1 for i, item in enumerate(pos_tags) if item[1] in ['NN', 'NNS', 'NNP', 'NNPS'] or item[1] in ['JJ', 'JJR', 'JJS', 'RB'] or item[1] == 'VBG']
    noun_phrases += parse_noun_phrase(indices, num_tokens)
    # Tokenize all possible tokens whose tags are noun
    single_nouns = [item[0] for item in pos_tags if item[1] in ['NN', 'NNS', 'NNP', 'NNPS', 'CD', 'JJ', 'VBG'] and item[0] not in noun_phrases]
    noun_phrases += single_nouns
    return noun_phrases

# %%
def analyse(parsed_tokens, dictionary, tags, exact = False):
    tagged_tokens = []
    # Handle special case of date and time filter with query from ... to ...
    special_tokens = [token for token in parsed_tokens if '-->' in token]
    for token in special_tokens:
        begin, _ = token.split('-->')
        try:
            idx = dictionary.index(begin)
            tag = tags[idx]
            if tag == 'local_time':
                tagged_tokens.append((token, f'{tag} --> HH:mm'))
            elif tag == 'date':
                tagged_tokens.append((token, f'{tag} --> yyyy-MM-dd'))
        except: tagged_tokens.append((token, f'{tag} --> yyyy-MM'))
    if exact is False:
        filtered_tokens = parsed_tokens
        # filtered_tokens = [token for token in parsed_tokens if any(token in item for item in dictionary) is True] #Compare the noun phrases with dictionaries to find matches terms
    else:
        filtered_tokens = [token for token in parsed_tokens if token in dictionary] #Compare the noun phrases with dictionaries to find matches terms
    print('Filtered tokens: ', filtered_tokens)
    filtered_tokens = sorted(filtered_tokens, key=lambda x: len(x), reverse=True)
    token_counter = Counter(filtered_tokens)
    minus_counter = {}
    for token in token_counter.keys():
        minus_counter[token] = 0
    for token, cnt in token_counter.items():
        cnt += minus_counter[token]
        if cnt == 0: continue
        word_tokens = nltk.word_tokenize(token)
        if len(word_tokens) > 1:
            for wtoken in word_tokens: # Reduce the number of single nouns which are included in a matched noun noun_phrases
                try:
                    minus_counter[wtoken] -= 1
                except: continue
        if exact is False:
            date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
            if date_pattern.match(token) is not None:
                tagged_tokens.append((token, 'date'))
            if any(token in item for item in dictionary) is True:
                tagged_tokens += [(token, tags[idx]) for idx, term in enumerate(dictionary) if token in term]
        else:
            date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
            if date_pattern.match(token) is not None:
                tagged_tokens.append((token, 'date'))
            if token in dictionary:
                idx = dictionary.index(token)
                tagged_tokens.append((token, tags[idx])) 
    
    # Refine tagged tokens to combine fields
    tagged_tokens = sorted(list(set(tagged_tokens)))
    return tagged_tokens

# %%
def preprocess_tokens(noun_phrases):
    processed_words = []
    porter_stem = PorterStemmer()
    for word in noun_phrases:
        tokens = nltk.word_tokenize(word.lower())
        refined_tokenize_list = [unicodedata.normalize('NFKD', token).encode('ascii', 'ignore').decode('utf-8', 'ignore') for token in tokens]
        refined_tokenize_list = [word for word in refined_tokenize_list if word not in stop_words]
        # refined_tokenize_list = [porter_stem.stem(word) for word in refined_tokenize_list]
        # refined_tokenize_list = [word for word in refined_tokenize_list if len(word) > 1 and word.isalpha()]
        refined_tokenize_list = [word for word in refined_tokenize_list if len(word) > 1]
        complete_word = ' '.join(refined_tokenize_list)
        processed_words.append(complete_word)
    return processed_words

# %%
def parse(text_query, number_to_text = False):
    text_query = contractions.fix(text_query)
    if text_query[-1] != '.': # Append character . at the end of the text query to parse the noun phrases properly
        text_query += '.'
    tokens = nltk.word_tokenize(text_query)
    pos_tags = nltk.pos_tag(tokens)
    if number_to_text is True:
        p = inflect.engine()
        pos_tags = [(p.number_to_words(item[0]), 'JJ') if item[1] == 'CD' else item for item in pos_tags]
    noun_phrases = extract_noun_phrases(pos_tags)
    noun_phrases = preprocess_tokens(noun_phrases)
    return noun_phrases

# %%
def time_parse(time_phrase, filters):
    su = SUTime(mark_time_ranges = True, include_range = True)
    parsed_values = su.parse(time_phrase)
    results = []
    for value in parsed_values:
        if value['text'] in filters: continue
        if value['type'] == 'DURATION':
            begin = value['value']['begin'].replace('T', '')
            end = value['value']['end'].split('T')[-1]
            results.append(f'{begin}-->{end}')
        elif value['type'] == 'TIME':
            temp = value['value'].split('T')
            _date = temp[0]
            _time = temp[1]
            year = _date[:4]
            results += [_date, year]
            if _time != 'MO': results.append(_time)
        elif value['type'] == 'DATE':
            temp = value['value']
            if 'INTERSECT' in temp:
                temp = temp.split(' INTERSECT ')
                _date = temp[0]
                year = _date[:4]
                _time = temp[1]
                begin, end, _ = _time.split(',')
                results += [_date, year, f'{begin[2:]}-->{end[1:]}']
            else:
                _date = temp
                year = _date[:4]
                results += [_date, year]
    return results

# %%
def process_text_query(text_query):
    concepts, locations, _time = text_query.split(';')
    tagged_concepts = []
    tagged_locations = [] 
    tagged_time = []
    if len(concepts) > 0:
        parsed_concepts = parse(concepts, number_to_text = True)
        tagged_concepts = analyse(parsed_concepts, concept_dictionary, concept_tags)
    if len(locations) > 0:
        parsed_locations = parse(locations)
        tagged_locations = analyse(parsed_locations, location_dictionary, location_tags) 
    if len(_time) > 0:
        parsed_time = parse(_time)
        parsed_time += time_parse(_time, parsed_time)
        tagged_time = analyse(parsed_time, time_dictionary, time_tags, exact = True) 
    return tagged_concepts, tagged_locations, tagged_time

# %% [markdown]
# ---

