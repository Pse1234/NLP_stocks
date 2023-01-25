from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import functions as F
import logging
logging.getLogger("py4j").setLevel(logging.ERROR)



"""TODO :
Changer le df et faire un path relative et mettre la data dans son propre dossier  
"""

class Preprocessing:
    
    def __init__(self, path, output_path):
        self.path = path
        self.output_path = output_path
 
    def import_df(self, path):
        print('Importing the csv')
        spark = SparkSession.builder.appName("CSVtoTable").getOrCreate()

        df = (spark.read.format("csv")
        .option('mode','DROPMALFORMED')
        .options(header = True, inferSchema = True, sep=",",multiLine=True)
        .load(self.path)
        .cache()) # Keep the dataframe in memory for faster processing 
        return df

    def change_type_column(self, df):
        print('Changing the type of columns')
        df = df.select(*[col(c).cast("integer").alias(c) if c in ['ReplyCount','RetweetCount','LikeCount'] else c for c in df.columns])
        df = df.withColumn("PostDate", to_date(df["PostDate"]))
        return df

    def cleaning_tweets(self, df):
        print('Importing the tweets')
        df = df.withColumn("TweetText", trim(regexp_replace("TweetText", "[\n]+", " ")))
        df = df.withColumn("TweetText", trim(regexp_replace("TweetText", "https?://[^ ]+", "")))
        df = df.withColumn("TweetText", trim(regexp_replace("TweetText", "@[^ ]+", "")))
        df = df.withColumn("TweetText", trim(regexp_replace("TweetText", "#[^ ]+", "")))
        df = df.withColumn("TweetText", trim(regexp_replace("TweetText", "[^A-Za-z0-9 ]", "")))
        df = df.withColumn("TweetText", regexp_extract("TweetText", "(2021|2017|2018|2019|2020|2022).*", 0))
        df = df.withColumn("TweetText", regexp_replace("TweetText", "[^a-zA-Z\\s]", ""))
        df = df.na.drop(subset="TweetText") 
        return df

    def dealing_with_na(self, df):
        print('Dealing with na values')
        df = df.na.fill(0, subset=['ReplyCount','RetweetCount','LikeCount'])
        return df

    def loosing_handle(self, df):
        print('Loosing the @ for the handles')
        df = df.withColumn("Handle", trim(regexp_replace("Handle", "@", "")))
        return df
    def creating_csv(self, df, output_path):
        print('Creating the cleaned csv!')
        df.write.format("csv").mode("overwrite").save(self.output_path)
        return df


if __name__ == "__main__":
    path = "/Users/sarrabenyahia/Documents/GitHub/NLP_stocks/Data/webscraped_VALERO_ENERGY_CORP.csv"
    output_path = "/Users/sarrabenyahia/Documents/GitHub/NLP_stocks/Data/processed_df.csv"
    preprocessing = Preprocessing(path =path, output_path=output_path)
    df = preprocessing.import_df(path)
    df = preprocessing.change_type_column(df)
    df = preprocessing.cleaning_tweets(df)
    df = preprocessing.dealing_with_na(df)
    df = preprocessing.loosing_handle(df)
    preprocessing.creating_csv(df, output_path)
    print("Here is the result :) ")
    df.show()