# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ### SILVER LAYER SCRIPT

# COMMAND ----------

# MAGIC %md
# MAGIC ### # DATA ACCESS USING APP 

# COMMAND ----------

spark.conf.set("fs.azure.account.auth.type.advenworkdatalake.dfs.core.windows.net", "OAuth")
spark.conf.set("fs.azure.account.oauth.provider.type.advenworkdatalake.dfs.core.windows.net", "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
spark.conf.set("fs.azure.account.oauth2.client.id.advenworkdatalake.dfs.core.windows.net", "e6987ad2-514d-4cf9-ad00-99dbf92b21b3")
spark.conf.set("fs.azure.account.oauth2.client.secret.advenworkdatalake.dfs.core.windows.net", "nEH8Q~TKhPuOdKAhMPllpVxDyOUUPS65lIq11c5X")
spark.conf.set("fs.azure.account.oauth2.client.endpoint.advenworkdatalake.dfs.core.windows.net", "https://login.microsoftonline.com/9da36bbb-7597-4d9d-b5a8-777e703fe193/oauth2/token")

# COMMAND ----------

# MAGIC %md
# MAGIC ### READ DATA 

# COMMAND ----------

df_cal = spark.read.format("csv").option("header",True).option("inferSchema",True).load('abfss://bronze@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Calendar')

# COMMAND ----------

df_cus = spark.read.format("csv").option("header",True).option("inferSchema",True).load('abfss://bronze@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Customers')

# COMMAND ----------

df_prodcat = spark.read.format("csv").option("header",True).option("inferSchema",True).load('abfss://bronze@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Product_Categories')

# COMMAND ----------

df_prods = spark.read.format("csv").option("header",True).option("inferSchema",True).load('abfss://bronze@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Products')

# COMMAND ----------

df_ret = spark.read.format("csv").option("header",True).option("inferSchema",True).load('abfss://bronze@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Returns')

# COMMAND ----------

df_sales = spark.read.format("csv").option("header",True).option("inferSchema",True).load('abfss://bronze@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Sales*')

# COMMAND ----------

df_terr = spark.read.format("csv").option("header",True).option("inferSchema",True).load('abfss://bronze@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Territories')

# COMMAND ----------

df_subCat = spark.read.format("csv").option("header",True).option("inferSchema",True).load('abfss://bronze@advenworkdatalake.dfs.core.windows.net/Product_Subcategories')

# COMMAND ----------

# MAGIC %md
# MAGIC ### TRANSFORMATION
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC #### Calendar

# COMMAND ----------

df_cal.display()

# COMMAND ----------

df_cal = df_cal.withColumn('Month',month(col('Date'))) \
                   .withColumn('Year',year(col('Date'))) 
#df_cal.display()


# COMMAND ----------

df_cal.write.format('parquet')\
    .mode('append')\
        .option("path", "abfss://silver@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Calendar")\
            .save()

# COMMAND ----------

# MAGIC %md
# MAGIC #### Customers

# COMMAND ----------

df_cus.display()

# COMMAND ----------

df_cus = df_cus.withColumn('fullName', concat_ws(' ', col('Prefix'), col('FirstName'), col('LastName')))

# COMMAND ----------

df_cus.write.format('parquet')\
    .mode('append')\
        .option("path", "abfss://silver@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Customers")\
            .save()


# COMMAND ----------

# MAGIC %md
# MAGIC #### Sub Categories

# COMMAND ----------

df_subCat.display()

# COMMAND ----------

df_subCat.write.format('parquet')\
    .mode('append')\
        .option("path", "abfss://silver@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Product_SubCategories")\
            .save()


# COMMAND ----------

# MAGIC %md
# MAGIC #### Products
# MAGIC

# COMMAND ----------

df_prods = df_prods.withColumn('ProductSKU',split(col('ProductSKU'),'-')[0]) \
    .withColumn('ProductName',split(col('ProductName'),' ')[0])

# COMMAND ----------

df_prods.write.format('parquet')\
    .mode('append')\
        .option("path", "abfss://silver@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Products")\
            .save()

# COMMAND ----------

# MAGIC %md
# MAGIC #### Returns

# COMMAND ----------

df_ret.display()    


# COMMAND ----------

df_ret.write.format('parquet')\
    .mode('append')\
        .option("path", "abfss://silver@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Returns")\
            .save()

# COMMAND ----------

# MAGIC %md
# MAGIC #### Territories

# COMMAND ----------

df_terr.display()

# COMMAND ----------

df_terr.write.format('parquet')\
    .mode('append')\
        .option("path", "abfss://silver@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Territories")\
            .save()

# COMMAND ----------

# MAGIC %md
# MAGIC #### Sales
# MAGIC

# COMMAND ----------

df_sales.display()

# COMMAND ----------

df_sales = df_sales.withColumn('StockDate',to_timestamp('StockDate'))

# COMMAND ----------

df_sales = df_sales.withColumn('OrderNumber',regexp_replace(col('OrderNumber'), "S", "T"))

# COMMAND ----------

df_sales = df_sales.withColumn('multiply',col('OrderLineItem')*col('OrderQuantity'))

# COMMAND ----------

df_sales.write.format('parquet')\
    .mode('append')\
        .option("path", "abfss://silver@advenworkdatalake.dfs.core.windows.net/AdventureWorks_Sales")\
            .save()

# COMMAND ----------

# MAGIC %md
# MAGIC #### Sales Analysis

# COMMAND ----------

df_sales.groupBy('OrderDate').agg(count('OrderNumber').alias('total_order')).display()

# COMMAND ----------

df_prodcat.display()

# COMMAND ----------

df_terr.display()