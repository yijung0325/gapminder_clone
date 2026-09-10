import pandas as pd
import sqlite3

class CreateGapminderDB:
    def __init__(self):
      self.file_names = ["ddf--datapoints--gdp_pcap--by--country--time", 
                    "ddf--datapoints--lex--by--country--time", 
                    "ddf--datapoints--pop--by--country--time", 
                    "ddf--entities--geo--country"]
      self.table_names = ["gdp_per_capita", "life_expectancy", "population", "geography"]

    def import_data(self):
        df_dict = {}
        for file_name, table_name in zip(self.file_names, self.table_names):
            file_path = f"data/{file_name}.csv"
            df = pd.read_csv(file_path)
            df_dict[table_name] = df
        return df_dict

    def create_database(self):
        df_dict = self.import_data()
        connection = sqlite3.connect("data/gapminder.db")
        for k, v in df_dict.items():
            v.to_sql(k, connection, if_exists="replace", index=False)
        drop_view_sql = """
        DROP VIEW IF EXISTS plotting;
        """
        create_view_sql = """
        CREATE VIEW plotting AS
        SELECT geography.name AS country_name,
              gdp_per_capita.time AS dt_year,
              gdp_per_capita.gdp_pcap AS gdp_per_capita,
              geography.world_4region AS continent,
              life_expectancy.lex AS life_expectancy,
              population.pop AS population
          FROM gdp_per_capita
          JOIN geography
            ON gdp_per_capita.country = geography.country
          JOIN life_expectancy
            ON gdp_per_capita.country = life_expectancy.country AND
              gdp_per_capita.time = life_expectancy.time
          JOIN population
            ON gdp_per_capita.country = population.country AND
              gdp_per_capita.time = population.time
        WHERE gdp_per_capita.time < 2024;
        """
        cur = connection.cursor()
        cur.execute(drop_view_sql)
        cur.execute(create_view_sql)
        connection.close()

create_gapminder_db = CreateGapminderDB()
create_gapminder_db.create_database()
