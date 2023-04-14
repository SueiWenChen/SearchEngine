import os, json, re, time
from numpy import log
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
from functools import reduce
from color import color

# load tools and data structures
stemmer = SnowballStemmer("english")
with open('doc_id_to_name.json') as f:
    doc_id_to_name = json.load(f)
    N = len(doc_id_to_name) # number of documents
inverted_index = dict()
with open('inverted_index.txt') as f:
    for line in f:
        word = line[1:line[1:].index('"')+1]
        info = json.loads(line[line.index("{"):])
        inverted_index[word] = info

def tfidf(word, doc, docs):
    # compute the tfidf of (word, doc)
    # docs: all documents containing word
    tf, idf = docs[doc], log(N/len(docs))
    return tf * idf

def search(keywords):
    # return docs containing keywords input by user, ranked by sum of tfidf scores
    # kwd_matches: words in keywords that have matches in inverted_index
    # doc_matches: values for kwd_matches in inverted_index
    kwd_matches, doc_matches = [], []
    for word in keywords:
        word_stem = stemmer.stem(word)
        if word_stem in inverted_index:
            kwd_matches.append(word_stem)
            doc_matches.append(inverted_index[word_stem]) # dict of doc_id:word_count
    # documents containing all search keywrods
    try:
        doc_all_kwds = reduce(set.intersection, [set(d) for d in doc_matches])
    except: # some word stem has no matches
        return []
    # retain only docs that contain all kwds
    doc_matches = [{d:c for d,c in docs.items() if d in doc_all_kwds} for docs in doc_matches]
    # calculate the tf-idf scores for each (word,doc) pair
    scores = [{d:tfidf(kwd, d, docs) for d in docs} for kwd, docs in zip(kwd_matches, doc_matches)]
    final_scores = reduce(lambda x,y: {k:x[k]+y[k] for k in x}, scores) # sum of scores across docs
    final_scores = [(d,s) for d,s in final_scores.items()]
    final_scores = sorted(final_scores, key=lambda x: x[1], reverse=True)
    return final_scores

def display(doc_ids, keyword):
    # given list of doc_id and a keyword, display the titles of the documents
    # and part of the files where the keyword first appears
    doc_names = [doc_id_to_name[i] for i in doc_ids]
    doc_info = [] # information to display
    kwd = stemmer.stem(keyword) # stemmed keyword
    for d in doc_names:
        with open(f'documents/{d}.txt') as f:
            content = f.read()
            title = content[7:content.index('\n')]
            tokenized_content = word_tokenize(content)
            processed_content = list(map(stemmer.stem, tokenized_content))
            where = processed_content.index(kwd)
            snippet = " ".join(tokenized_content[where-2:where+5])
            doc_info.append((title,snippet))
    
    for doc_id, (title, snippet) in zip(doc_ids, doc_info):
        print(f'{color.BLUE}Doc#{doc_id.ljust(5)}{color.END}', end=' ')
        print(f'{color.RED}{title.ljust(40)}{color.END}', end=' ')
        print(f'{color.GREEN}... {snippet} ...{color.END}')
              
def main():
    print('Document Search Engine')
    while True:
        query = input('''Please enter search keyword(s): ''').lower()
        if len(query)==0:
            continue
        starttime = time.time()
        keywords = list(map(str.lower,word_tokenize(query) ))
        keywords = [w for w in keywords if bool(re.match('^\w[a-z\-]*$',w))]
        doc_matches = search(keywords)
        top10 = [x[0] for x in doc_matches[:10]]
        if len(top10)==0:
            print(f'No match found for "{query}"')
        else:
            print(f'Search results for "{query}"')
            display(top10, keywords[0])
            duration = time.time()- starttime
            print(f'{color.CYAN}Found {len(doc_matches)} matches (in {duration:.2f}s){color.END}')
        
        stay = input('Continue searching? [y/n]: ')
        if stay.lower()=='n':
            break
if __name__ == "__main__":
    main()