# This script generates PlantUML diagram for tables visible to Spark.
# The diagram is stored in the db_schema.puml file, so just run
# 'java -jar plantuml.jar db_schema.puml' to get PNG file

from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException

# Variables

# list of databases/namespaces to analyze.  Could be empty, then all existing databases/namespaces will be processed
databases = ["a", "airbnb"] # put databases/namespace to handle
# change this if you want to include temporary tables as well
include_temp = False

# implementation
spark = SparkSession.builder.appName("Database Schema Generator").getOrCreate()

# if databases aren't specified, then fetch list from the Spark
if len(databases) == 0:
    databases = [db["namespace"] for db in spark.sql("show databases").collect()]

with open(f"db_schema.puml", "w") as f:
    f.write("\n".join(
        ["@startuml", "skinparam packageStyle rectangle", "hide circle",
         "hide empty methods", "", ""]))

    for database_name in databases[:3]:
        f.write(f'package "{database_name}" {{\n')
        tables = spark.sql(f"show tables in `{database_name}`")
        for tbl in tables.collect():
            table_name = tbl["tableName"]
            db = tbl["database"]
            if include_temp or not tbl["isTemporary"]: # include only not temporary tables
                lines = []
                try:
                    lines.append(f'class {table_name} {{')
                    cols = spark.sql(f"describe table `{db}`.`{table_name}`")
                    for cl in cols.collect():
                        col_name = cl["col_name"]
                        data_type = cl["data_type"]
                        lines.append(f'{{field}} {col_name} : {data_type}')

                    lines.append('}\n')
                    f.write("\n".join(lines))
                except AnalysisException as ex:
                    print(f"Error when trying to describe {tbl.database}.{table_name}: {ex}")

        f.write("}\n\n")

    f.write("@enduml\n")