# from nltk.corpus import words
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from mrjob.job import MRJob
from mrjob.step import MRStep
import os, json, re

# eng_words = set(words.words())
stemmer = SnowballStemmer("english")
with open('doc_name_to_id.json') as f:
    doc_name_to_id = json.load(f)

class MRInvertedIndex(MRJob):
    def mapper_text_to_DocidWord(self, _, v):
        for word in word_tokenize(v):
            word = word.lower()
            if bool(re.match('^[a-z][a-z\-]*$',word)):
                word_stem = stemmer.stem(word)
                fname = os.environ['map_input_file']
                fname = fname.split('/')[-1][:-4]
                yield  (doc_name_to_id[fname], word_stem), 1
    
    def reducer_DocidWord_count(self, file_word_pair, word_counts):
        yield (file_word_pair, sum(word_counts))

    def mapper_DocidWord_count_to_word_DocidCount(self, file_word_pair, word_counts):
        yield file_word_pair[1], (file_word_pair[0], word_counts)
    def reducer_word_DocidCount(self, k, vs):
        pairs = list(vs)
        yield k, {docid:count for docid,count in pairs}

    def steps(self):
        return [
            MRStep(mapper=self.mapper_text_to_DocidWord,
                   reducer=self.reducer_DocidWord_count),
            MRStep(mapper=self.mapper_DocidWord_count_to_word_DocidCount,
                   reducer=self.reducer_word_DocidCount)
        ]

if __name__ == '__main__':
    MRInvertedIndex.run()

# python3 inverted_index.py ./documents > ./inverted_index.txt