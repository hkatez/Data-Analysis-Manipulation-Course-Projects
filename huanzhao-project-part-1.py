# transform csv to json
beers = pd.read_csv("beers.csv", encoding='utf-8').to_json("beers.json", orient='records', lines=True)
breweries = pd.read_csv("breweries.csv", encoding='utf-8').to_json("breweries.json", orient='records', lines=True)

#ssh -l huanzhao cavium-thunderx.arc-ts.umich.edu
#pyspark --master yarn --conf spark.ui.port="$(shuf -i 10000-60000 -n 1)"

from pyspark import SparkContext
from pyspark import SQLContext
import csv
import json

#sc = SparkContext()

# read file
beerraw = sc.textFile("hdfs:////user/huanzhao/beers.json")
breweryraw = sc.textFile("hdfs:////user/huanzhao/breweries.json")

# examine data
#beerraw.take(5)
#breweryraw.take(5)

data1 = sqlContext.read.json("hdfs:////user/huanzhao/beers.json")
#data1.printSchema()
data2 = sqlContext.read.json("hdfs:////user/huanzhao/breweries.json")
#data2.printSchema()

data1.dropna().registerTempTable("beer")
data2.dropna().registerTempTable("brewery")


# task1: The characterics of beers
# Explore the ibu and abv for beer styles
# ibu for styles
q1 = sqlContext.sql('select style, avg(ibu) from beer where ibu is not null group by style order by avg(ibu) desc')
#q1.show()
q1.registerTempTable("avg_ibu_style")
rdd_q1 = q1.rdd.map(lambda x: (x[0]).encode('utf-8', 'ignore') + '\t' + (str(x[1])))
rdd_q1.saveAsTextFile('si618_project1_avgibu')
#hadoop fs -getmerge si618_project1_avgibu si618_project1_avgibu.csv


# abv for styles
q2 = sqlContext.sql('select style, avg(abv) from beer where abv is not null group by style order by avg(abv) desc')
#q2.show()
q2.registerTempTable("avg_abv_style")
rdd_q2 = q2.rdd.map(lambda x: (x[0]).encode('utf-8', 'ignore') + '\t' + (str(x[1])))
rdd_q2.saveAsTextFile('si618_project1_avgabv')
#hadoop fs -getmerge si618_project1_avgabv si618_project1_avgabv.csv


q_ia = sqlContext.sql('select style, ibu, abv from beer order by style')
#q_ia.show()
q_ia.registerTempTable("ibu_abv_style")
rdd = q_ia.rdd.map(lambda x: (x[0]).encode('utf-8', 'ignore') + '\t' + (str(x[1])) + '\t' + (str(x[2])))
rdd.saveAsTextFile('si618_project1_ibuabvstyle')
#hadoop fs -getmerge si618_project1_ibuabvstyle si618_project1_ibuabvstyle.csv


# Explore the ibu and abv for beers
# ibu for beers
q3 = sqlContext.sql('select id, name, style, ibu from beer where ibu is not null order by ibu desc')
#q3.show()
q3.registerTempTable("ibu_beer")
rdd1 = q3.rdd.map(lambda x: (str(x[0])) + '\t' + (x[1]).encode('utf-8', 'ignore') + '\t' + (x[2]).encode('utf-8', 'ignore') + '\t' +  (str(x[3])))
rdd1.saveAsTextFile('si618_project1_ibubeer')
# hadoop fs -rm -r si618_project1_ibubeer
#hadoop fs -getmerge si618_project1_ibubeer si618_project1_ibubeer.csv

# abv for beers
q4 = sqlContext.sql('select id, name, style, abv from beer where abv is not null order by abv desc')
#q4.show()
q4.registerTempTable("abv_beer")
rdd2 = q4.rdd.map(lambda x: (str(x[0])) + '\t' + (x[1]).encode('utf-8', 'ignore') + '\t' + (x[2]).encode('utf-8', 'ignore') + '\t' +  (str(x[3])))
rdd2.saveAsTextFile('si618_project1_abvbeer')
#hadoop fs -getmerge si618_project1_abvbeer si618_project1_abvbeer.csv

# guessing market sales with ibu and abv combo
q5 = sqlContext.sql('select id, name, ibu, abv, concat(ibu, abv) as ibu_abv from beer where ibu is not null and abv is not null')
#q5.show()
q5.registerTempTable("ibu_abv_combine")

q6 = sqlContext.sql('select t.id, t.name, t.ibu, t.abv from ibu_abv_combine t join (select ibu_abv, count(*) as cnt from ibu_abv_combine t group by ibu_abv) tt on t.ibu_abv = tt.ibu_abv order by tt.cnt desc, t.ibu_abv')
#q6.show()
q6.registerTempTable("task1_salesguess")
rdd3 = q6.rdd.map(lambda x: (str(x[0])) + '\t' + (x[1]).encode('utf-8', 'ignore') + '\t' +  (str(x[2])) + '\t' +  (str(x[3])))
rdd3.saveAsTextFile('si618_project1_salesguess')
#hadoop fs -getmerge si618_project1_salesguess si618_project1_salesguess.csv




# task2: Combining beers with breweries
# which brewery produces the largest variety of beers
q7 = sqlContext.sql('select br.name, count(b.name) from beer b left join brewery br on b.brewery_id = br.brewery_row group by br.name order by count(b.name) desc')
#q7.show()
q7.registerTempTable("brewery_beer")
rdd4 = q7.rdd.map(lambda x: (x[0]).encode('utf-8', 'ignore') + '\t' +  (str(x[1])))
rdd4.saveAsTextFile('si618_project1_beerforbr')
#hadoop fs -getmerge si618_project1_beerforbr si618_project1_beerforbr.csv

# what is the distribution of breweries for each style
q8 = sqlContext.sql('select b.style, count(br.name) from brewery br left join beer b on b.brewery_id = br.brewery_row where style is not null group by b.style order by count(br.name) desc')
#q8.show()
q8.registerTempTable('style_brewery')

q9 = sqlContext.sql('select b.style, br.name from brewery br left join beer b on b.brewery_id = br.brewery_row where style is not null')
#q9.show()
q9.registerTempTable('sfb')

q10 = sqlContext.sql('select style, count(name) bcount, name b from sfb group by style, name order by count(name) desc')
#q10.show()
q10.registerTempTable('sfb1')

q11 = sqlContext.sql('select style, max(bcount) bcount from sfb1 group by style order by style')
#q11.show()
q11.registerTempTable('sfb2')

q12 = sqlContext.sql('select sfb2.style, sfb1.b, sfb2.bcount from sfb2 join sfb1 on sfb1.style = sfb2.style and sfb2.bcount= sfb1.bcount order by bcount desc, style')
#q12.show()
q12.registerTempTable('task2_largest_breweries')
rdd5 = q12.rdd.map(lambda x: (x[0]).encode('utf-8', 'ignore') + '\t' + (x[1]).encode('utf-8', 'ignore') + '\t' +  (str(x[2])))
rdd5.saveAsTextFile('si618_project1_brforstyle')
#hadoop fs -getmerge si618_project1_brforstyle si618_project1_brforstyle.csv



# task 3: geographical analysis
# state that has most breweries
q13 = sqlContext.sql('select state, count(brewery_row) from brewery group by state order by count(brewery_row) desc')
#q13.show()
q13.registerTempTable('state_breweries')
rdd6= q13.rdd.map(lambda x: (x[0]).encode('utf-8', 'ignore') + '\t' + (str(x[1])))
rdd6.saveAsTextFile('si618_project1_statebrewery')
#hadoop fs -getmerge si618_project1_statebrewery si618_project1_statebrewery.csv

# city that has most breweries
q14 = sqlContext.sql('select city, count(brewery_row) from brewery group by city order by count(brewery_row) desc')
#q14.show()
q14.registerTempTable('city_breweries')
rdd7= q14.rdd.map(lambda x: (x[0]).encode('utf-8', 'ignore') + '\t' + (str(x[1])))
rdd7.saveAsTextFile('si618_project1_citybrewery')
# hadoop fs -rm -r si618_project1_citybrewery
#hadoop fs -getmerge si618_project1_citybrewery si618_project1_citybrewery.csv

# Taste
# Will different states have similar tastes
# average ibu and abv for each state
q15 = sqlContext.sql('select br.state, avg(b.ibu), avg(b.abv) from beer b left join brewery br on b.brewery_id = br.brewery_row group by br.state order by state')
#q15.show()
q15.registerTempTable('task3_stateia')
rdd8 = q15.rdd.map(lambda x: (str(x[0])) + '\t' + (str(x[1])) + '\t' + (str(x[2])))
rdd8.saveAsTextFile('si618_project1_stateia')
#hadoop fs -getmerge si618_project1_stateia si618_project1_stateia.csv















