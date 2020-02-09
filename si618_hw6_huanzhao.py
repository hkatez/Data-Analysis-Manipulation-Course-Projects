#ssh -l huanzhao cavium-thunderx.arc-ts.umich.edu
#pyspark --master yarn --conf spark.ui.port="$(shuf -i 10000-60000 -n 1)"

import json
import math
import re
from pyspark import SparkConf, SparkContext

conf = SparkConf().setAppName('PythonYelpSentiment')
sc = SparkContext(conf=conf)

frequent_word_threshold=1000
WORD_RE = re.compile(r'\b[\w]+\b') 
def convert_dict_to_tuples(d):
        text = d['text']
        useful = d['useful']
        tokens = WORD_RE.findall(text)
        tuples = []
        for w in tokens:
                tuples.append((useful, w))
        return tuples

input_file=sc.textFile("/var/umsi618/hw6/review.json")
# convert each json review into a dictionary
step_1a = input_file.map(lambda line: json.loads(line))

# convert a review's dictionary to a list of (rating, word) tuples
step_1b = step_1a.flatMap(lambda x : convert_dict_to_tuples(x))

# count all words from all reviews
step_2a2 = step_1b.map(lambda x: (x[1], 1)).reduceByKey(lambda a, b: a + b)

# filter out all word-tuples from positive reviews
step_2b1=step_1b.filter(lambda x:x[0]>5)

# count all words from positive reviews
step_2b2 = step_2b1.map(lambda x: (x[1], 1)).reduceByKey(lambda a, b: a + b)

# filter out all word-tuples from negative reviews
step_2c1 = step_1b.filter(lambda x: x[0] == 0)

# count all words from negative reviews
step_2c2=step_2c1.map(lambda x:(x[1],1)).reduceByKey(lambda a,b:a + b)

# get total word count for all, positive, and negative reviews
all_review_word_count = step_2a2.map(lambda x: x[1]).sum()
useful_review_word_count = step_2b2.map(lambda x:x[1]).sum()
useless_review_word_count = step_2c2.map(lambda x:x[1]).sum()

# filter to keep only frequent words, i.e. those with
# count greater than frequent_word_threshold.
freq_words=step_2a2.filter(lambda x:x[1]>frequent_word_threshold).cache()
# filter to keep only those word count tuples whose word can
# be found in the frequent list
step_3useful=freq_words.join(step_2b2)
step_3useless=freq_words.join(step_2c2)

# compute the log ratio score for each positive review word
unsorted_useful_words = step_3useful.map(lambda x: (x[0], math.log(float(x[1][1])/useful_review_word_count ) - math.log(float(x[1][0])/all_review_word_count)))
# sort by descending score to get the top-scoring positive words
sorted_useful_words = unsorted_useful_words.sortBy(lambda x: x[1], ascending = False)

# compute the log ratio score for each negative review word
unsorted_useless_words = step_3useless.map(lambda x:(x[0],math.log(float(x[1][1])/useless_review_word_count) - math.log(float(x[1][0])/all_review_word_count)))
# sort by descending score to get the top-scoring negative words
sorted_useless_words = unsorted_useless_words.sortBy(lambda x: x[1], ascending = False)

# write out the top-scoring positive words to a text file
sorted_useful_words.saveAsTextFile("si618_hw6_huanzhao_usefulreview")
# write out the top-scoring negative words to a text file
sorted_useless_words.saveAsTextFile("si618_hw6_huanzhao_uselessreview")

#hadoop fs -getmerge si618_hw6_huanzhao_usefulreview si618_hw5_huanzhao_usefulreview.txt