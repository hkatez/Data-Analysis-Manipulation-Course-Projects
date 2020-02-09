# Calculate the average stars for each business category
# Written by Dr. Yuhang Wang and Josh Gardner
'''
To run on Fladoop cluster:
spark-submit --master yarn --num-executors 16 --executor-memory 1g --executor-cores 2 si618_hw4_huanzhao.py

To get results:
hadoop fs -getmerge si618_hw4_output_huanzhao si618_hw4_output_huanzhao.tsv
'''

import json
from pyspark import SparkContext
sc = SparkContext(appName="PySparksi618f19avg_stars_per_category")

input_file = sc.textFile("hdfs:////var/umsi618/hw4/business.json")

def business_result(data):
    business_list = []
    cities = data.get('city', None)
    reviews_count = data.get('review_count', None)
    stars = data.get('stars', None)
    categories_raw = data.get('categories', None)
    if categories_raw != None:
        categories = categories_raw.split(', ')
        for c in categories:
          if stars != None:
            if stars >= 4:
                business_list.append(((cities, c), (1, reviews_count, 1)))
            else:
                business_list.append(((cities, c), (1, reviews_count, 0)))
    else:
      if stars != None:
        if stars >= 4:
          business_list.append(((cities, 'Unknown'), (1, reviews_count, 1)))
        else:
          business_list.append(((cities, 'Unknown'), (1, reviews_count, 0)))
    return business_list


business_results = input_file.map(lambda line: json.loads(line)) \
.flatMap(business_result) \
.reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1], x[2] + y[2])) \
.sortBy(lambda x: (x[0][0], -x[1][0]), numPartitions = 1) \
.map(lambda x: str(x[0][0]) + "\t" + str(x[0][1]) + "\t" + str(x[1][0]) + "\t" + str(x[1][1]) + "\t" + str(x[1][2]))


#business_results.collect()
business_results.saveAsTextFile("si618_hw4_output_huanzhao")
