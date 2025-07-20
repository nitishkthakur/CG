# CG
Database class
- init - dbname, dbuser, dbpass, dbhost, dbport (if dbname does not exist, it will be created, else, we log on to that db)
- create_table - table_name, columns (list of tuples with column name and type)
- insert - table_name, data (list of tuples or dictionary with column names as keys)
- select - table_name, columns (list of column names), where (optional, dictionary with column names as keys)
- update - table_name, data (dictionary with column names as keys), where (dictionary with column names as keys)
- delete - table_name, where (dictionary with column names as keys)
- drop_table - table_name

## Pyspark class


## MongoDB class
- init - dbname, dbuser, dbpass, dbhost, dbport
- create_collection - collection_name
- insert - collection_name, data (list of dictionaries)
- find - collection_name, query (dictionary with search criteria)
- update - collection_name, query (dictionary with search criteria), update_data (dictionary with new values)
- delete - collection_name, query (dictionary with search criteria)

