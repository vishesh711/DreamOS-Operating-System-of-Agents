# DreamOS Natural Language Database Querying

The database querying feature in DreamOS allows you to load structured data from CSV and JSON files, and then query that data using natural language. Behind the scenes, your natural language queries are converted to SQL.

## Features

- Load data from CSV and JSON files
- Query data using natural language
- Execute SQL queries directly on datasets
- View dataset schema and sample data
- Natural language to SQL translation
- Detailed data exploration capabilities

## Usage

### Command Line Interface

You can use the database querying feature directly from the command line using the `db_query_test.py` script:

```bash
# Create and load sample data
python db_query_test.py --sample

# List loaded datasets
python db_query_test.py --list-datasets

# Get details about a dataset
python db_query_test.py --describe employees

# Execute a natural language query
python db_query_test.py --query "Find all employees in the Engineering department" --dataset employees

# Execute a natural language query on products
python db_query_test.py --query "List products with price greater than 300" --dataset products
```

### Terminal Agent Commands

When running DreamOS, you can use the following commands:

```
# Load a CSV or JSON file
db load path/to/data.csv [dataset_name]

# Query a dataset using natural language
db query Find all employees in Engineering --dataset=employees

# List loaded datasets
db list

# Show dataset schema and details
db describe employees

# Execute SQL directly on a dataset
db execute SELECT * FROM employees WHERE department = 'Engineering' --dataset=employees

# Show database query help
db help
```

## How It Works

1. **Data Loading**: The system loads data from CSV or JSON files into pandas DataFrames
2. **Natural Language Processing**: Your natural language query is sent to an LLM
3. **SQL Generation**: The LLM converts your query to SQL
4. **Query Execution**: The SQL is executed against your dataset
5. **Results Formatting**: Results are formatted into a readable table

## Example Queries

Here are some example natural language queries you can try:

### For Employee Data
- Find all employees in the Engineering department
- What is the average salary by department?
- Who has the highest salary?
- List employees hired before 2020
- How many employees are in each department?

### For Product Data
- List all electronics products
- What is the total stock value for each category?
- Which product has the highest price?
- Find products with stock less than 20
- What is the average price by category?

## Notes

- The natural language to SQL conversion works best with clear, specific queries
- Complex queries may require SQL syntax directly using the `db execute` command
- The database is in-memory only; changes will not persist after restarting DreamOS
- Multiple datasets can be loaded simultaneously
- For best results, ensure your data has clear column names

## Requirements

- pandas
- sqlalchemy
- sqlparse
- tabulate

These dependencies are included in the requirements.txt file. 