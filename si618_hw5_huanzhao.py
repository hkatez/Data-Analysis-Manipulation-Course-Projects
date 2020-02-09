#ssh -l huanzhao cavium-thunderx.arc-ts.umich.edu
#pyspark --master yarn --conf spark.ui.port="$(shuf -i 10000-60000 -n 1)"

from pyspark import SparkContext
from pyspark import SQLContext
import json
import csv
#sc = SparkContext()
#sqlContext = SQLContext(sc)
data1 = sqlContext.read.json("hdfs:///var/umsi618/hw5/review.json")
#data1.printSchema()
data2 = sqlContext.read.json("hdfs:///var/umsi618/hw5/business.json")
#data2.printSchema()

data1.registerTempTable("yelpreview")
data2.registerTempTable("yelpbusiness")

q1 = sqlContext.sql('select business_id, user_id, stars from yelpreview')
#q1.show()
q1.registerTempTable("reviewtable")

q2 = sqlContext.sql('select business_id, city from yelpbusiness')
#q2.show()
q2.registerTempTable("businesstable")

q3 = sqlContext.sql('select r.business_id, b.city, r.user_id, r.stars from yelpreview as r\
 left join yelpbusiness as b on b.business_id = r.business_id\
 where r.stars is not null and r.stars > 1')
#q3.show()
q3.registerTempTable("joinedtable1")

q4 = sqlContext.sql('select user_id, count(distinct city) as num_reviews from joinedtable1 group by user_id')
#q4.show()
q4.registerTempTable("usercity")

q5 = sqlContext.sql('select num_reviews as city, count(user_id) as yelp_user from usercity group by city order by yelp_user desc')
#q5.show()
q5.registerTempTable("outputwithout0")

q6 = sqlContext.sql('select city from outputwithout0 order by city desc limit 1')
#q6.show()
maxcity = q6.agg({"city": "max"}).collect()[0]["max(city)"]

q7 = q4.rdd.map(lambda x: x['num_reviews'])

rdd = q7.histogram(list(range(1,maxcity+2)))

with open('si618_hw5_huanzhao.csv','w') as f:
	csv_out = csv.writer(f)
	csv_out.writerow(['city','yelp user'])
	for row in range(0,(len(rdd[0])-1)):
		csv_out.writerow((rdd[0][row],rdd[1][row]))

#.map(lambda r: '\t'.join(str(i) for i in r))
#https://intellipaat.com/community/4448/best-way-to-get-the-max-value-in-a-spark-dataframe-column
#rdd.saveAsTextFile('si618_hw5_huanzhao')
#hadoop fs -getmerge si618_hw5_huanzhao si618_hw5_huanzhao.csv

#goodreviews
q8 = sqlContext.sql('select r.business_id, b.city, r.user_id, r.stars from yelpreview as r\
 left join yelpbusiness as b on b.business_id = r.business_id\
 where r.stars is not null and r.stars > 3')
#q8.show()
q8.registerTempTable("goodreview")

q9 = sqlContext.sql('select user_id, count(distinct city) as num_reviews_goodreview from goodreview group by user_id')
#q9.show()
q9.registerTempTable("goodreviewcount")

q10 = sqlContext.sql('select num_reviews_goodreview as city_goodreview, count(user_id) as yelp_user_goodreview from goodreviewcount group by city_goodreview order by yelp_user_goodreview desc')
#q10.show()
q10.registerTempTable("outputwithout0goodreview")

q11 = sqlContext.sql('select city_goodreview from outputwithout0goodreview order by city_goodreview desc limit 1')
#q11.show()
maxcity_good = q11.agg({"city_goodreview": "max"}).collect()[0]["max(city_goodreview)"]

q12 = q9.rdd.map(lambda x: x['num_reviews_goodreview'])

rdd1 = q12.histogram(list(range(1,maxcity_good+2)))

with open('si618_hw5_huanzhao_goodreview.csv','w') as f:
	csv_out = csv.writer(f)
	csv_out.writerow(['cities','yelp users'])
	for row in range(0,(len(rdd1[0])-1)):
		csv_out.writerow((rdd1[0][row],rdd1[1][row]))



#badreviews
q13 = sqlContext.sql('select r.business_id, b.city, r.user_id, r.stars from yelpreview as r\
 left join yelpbusiness as b on b.business_id = r.business_id\
 where r.stars is not null and r.stars < 3')
#q13.show()
q13.registerTempTable("badreview")

q14 = sqlContext.sql('select user_id, count(distinct city) as num_reviews_badreview from badreview group by user_id')
#q14.show()
q14.registerTempTable("badreviewcount")

q15 = sqlContext.sql('select num_reviews_badreview as city_badreview, count(user_id) as yelp_user_badreview from badreviewcount group by city_badreview order by yelp_user_badreview desc')
#q15.show()
q15.registerTempTable("outputwithout0badreview")

q16 = sqlContext.sql('select city_badreview from outputwithout0badreview order by city_badreview desc limit 1')
#q11.show()
maxcity_bad = q16.agg({"city_badreview": "max"}).collect()[0]["max(city_badreview)"]

q17 = q14.rdd.map(lambda x: x['num_reviews_badreview'])

rdd2 = q17.histogram(list(range(1,maxcity_bad+2)))

with open('si618_hw5_huanzhao_badreview.csv','w') as f:
	csv_out = csv.writer(f)
	csv_out.writerow(['cities','yelp users'])
	for row in range(0,(len(rdd2[0])-1)):
		csv_out.writerow((rdd1[0][row],rdd2[1][row]))