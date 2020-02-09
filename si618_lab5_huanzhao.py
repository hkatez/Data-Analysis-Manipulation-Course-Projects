from pyspark import SparkContext
from pyspark import SQLContext
import json

#sc = SparkContext()
#sqlContext = SQLContext(sc)
data = sqlContext.read.json("hdfs:///var/umsi618/lab5/NFLPlaybyPlay2015.json")
#data.printSchema()
data.registerTempTable("nfl")

q1 = sqlContext.sql('select GameID, posteam, sum(YardsGained) as totalYards from nfl\
 where posteam is not null\
 group by GameID, posteam\
 order by GameID')
#q1.show()
q1.registerTempTable("teamYardsPerGame")

#data.select('GameID, posteam, sum(YardsGained) as TotalYards from nfl where posteam is not null group by GameID, posteam order by GameID')
q2 = sqlContext.sql('select t1.posteam as team1, t2.posteam as team2,\
	 t1.totalYards as team1Yards, t2.totalYards as team2Yards, (t1.totalYards-t2.totalYards) as deltaYards\
	 from teamYardsPerGame as t1\
	 join teamYardsPerGame as t2\
	 where t1.GameID = t2.GameID and t1.posteam != t2.posteam')
#q2.show()
q2.registerTempTable("deltaYardsPerGame")

q3 = sqlContext.sql('select team1, mean(deltaYards) as meanDeltaYards from deltaYardsPerGame\
 group by team1\
 order by meanDeltaYards desc')
#q3.show()
q3.registerTempTable("meanDeltaYards")

rdd1 = q3.rdd.map(lambda r: '\t'.join(str(i) for i in r))
rdd1.saveAsTextFile('si618_lab5_output_1_huanzhao')

#hadoop fs -cat si618_lab5_output_1_huanzhao/part* > si618_lab5_output_1_huanzhao.tsv


q4 = sqlContext.sql('select posteam, PlayType, count(*) as count from nfl\
 where posteam is not null and PlayType in ("Pass","Run")\
 group by posteam, PlayType')
#q4.show()
q4.registerTempTable("countPassRun")

q5 = sqlContext.sql('select pr1.posteam, pr1.count as countRun, pr2.count as countPass from countPassRun as pr1\
 join countPassRun as pr2 on pr1.posteam = pr2.posteam\
 where pr1.PlayType = "Run" and pr2.PlayType = "Pass"')
#q5.show()
q5.registerTempTable("teamPassRun")

q6 = sqlContext.sql('select posteam as teamname, countRun/countPass as runtopassratio from teamPassRun order by runtopassratio')
#q6.show()
q6.registerTempTable("runtopassratio")

rdd2 = q6.rdd.map(lambda r: '\t'.join(str(i) for i in r))
rdd2.saveAsTextFile('si618_lab5_output_2_huanzhao')

#hadoop fs -cat si618_lab5_output_2_huanzhao/part* > si618_lab5_output_2_huanzhao.tsv
