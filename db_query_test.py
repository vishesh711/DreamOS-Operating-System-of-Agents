#!/usr/bin/env python3
"""
Database Query Test Script for DreamOS
"""
import os
import sys
import argparse
import json
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from dreamos.tools.database_query import DatabaseQueryTool
from dreamos.utils.logging_utils import setup_logger

# Setup logging
logger = setup_logger("db_query_test")

def create_sample_data():
    """Create sample data files for testing."""
    # Create sample CSV
    sample_csv_path = os.path.join("dreamos", "memory", "databases", "sample_employees.csv")
    with open(sample_csv_path, 'w') as f:
        f.write("id,name,department,salary,hire_date\n")
        f.write("1,John Smith,Engineering,85000,2020-01-15\n")
        f.write("2,Sarah Johnson,Marketing,72000,2019-05-20\n")
        f.write("3,Michael Brown,Engineering,90000,2018-11-10\n")
        f.write("4,Emily Davis,HR,65000,2021-03-08\n")
        f.write("5,David Wilson,Sales,78000,2020-07-22\n")
    
    # Create sample JSON
    sample_json_path = os.path.join("dreamos", "memory", "databases", "sample_products.json")
    products = [
        {"id": 1, "name": "Laptop", "category": "Electronics", "price": 1200, "stock": 45},
        {"id": 2, "name": "Smartphone", "category": "Electronics", "price": 800, "stock": 75},
        {"id": 3, "name": "Desk Chair", "category": "Furniture", "price": 250, "stock": 30},
        {"id": 4, "name": "Coffee Table", "category": "Furniture", "price": 350, "stock": 15},
        {"id": 5, "name": "Headphones", "category": "Electronics", "price": 150, "stock": 100}
    ]
    with open(sample_json_path, 'w') as f:
        json.dump(products, f, indent=2)
    
    print(f"Created sample CSV: {sample_csv_path}")
    print(f"Created sample JSON: {sample_json_path}")
    
    return sample_csv_path, sample_json_path

def main():
    """Main entry point for database query testing."""
    parser = argparse.ArgumentParser(description="DreamOS Database Query Test")
    parser.add_argument("--load-csv", type=str, help="Path to CSV file to load")
    parser.add_argument("--load-json", type=str, help="Path to JSON file to load")
    parser.add_argument("--query", type=str, help="Natural language query to execute")
    parser.add_argument("--dataset", type=str, help="Dataset name to query")
    parser.add_argument("--sample", action="store_true", help="Create and use sample data")
    parser.add_argument("--list-datasets", action="store_true", help="List loaded datasets")
    parser.add_argument("--describe", type=str, help="Describe a dataset")
    parser.add_argument("--execute-sql", type=str, help="Execute SQL query")
    args = parser.parse_args()
    
    try:
        # Initialize the database query tool
        print("Initializing database query tool...")
        db_tool = DatabaseQueryTool()
        print("Database query tool initialized successfully!")
        
        sample_csv_path = None
        sample_json_path = None
        
        # Create sample data if requested
        if args.sample:
            print("Creating sample data...")
            sample_csv_path, sample_json_path = create_sample_data()
            
            # Load sample CSV
            csv_result = db_tool.execute("load_csv", file_path=sample_csv_path, dataset_name="employees")
            if csv_result["status"] == "success":
                print(f"Loaded CSV dataset: {csv_result['dataset_name']} with {csv_result['row_count']} rows")
            else:
                print(f"Error loading CSV: {csv_result['error']}")
            
            # Load sample JSON
            json_result = db_tool.execute("load_json", file_path=sample_json_path, dataset_name="products")
            if json_result["status"] == "success":
                print(f"Loaded JSON dataset: {json_result['dataset_name']} with {json_result['row_count']} rows")
            else:
                print(f"Error loading JSON: {json_result['error']}")
        
        # Load CSV if specified
        if args.load_csv:
            result = db_tool.execute("load_csv", file_path=args.load_csv)
            if result["status"] == "success":
                print(f"Loaded CSV dataset: {result['dataset_name']} with {result['row_count']} rows")
            else:
                print(f"Error loading CSV: {result['error']}")
        
        # Load JSON if specified
        if args.load_json:
            result = db_tool.execute("load_json", file_path=args.load_json)
            if result["status"] == "success":
                print(f"Loaded JSON dataset: {result['dataset_name']} with {result['row_count']} rows")
            else:
                print(f"Error loading JSON: {result['error']}")
        
        # List datasets if requested
        if args.list_datasets:
            result = db_tool.execute("list_datasets")
            if result["status"] == "success":
                print(f"\nLoaded Datasets ({result['datasets_count']}):")
                for dataset in result["datasets"]:
                    print(f"  - {dataset['name']}: {dataset['row_count']} rows, {dataset['column_count']} columns")
            else:
                print(f"Error listing datasets: {result['error']}")
        
        # Describe dataset if requested
        if args.describe:
            result = db_tool.execute("describe_dataset", dataset_name=args.describe)
            if result["status"] == "success":
                print(f"\nDataset: {result['dataset_name']}")
                print(f"Source: {result['source']}")
                print(f"Type: {result['type']}")
                print(f"Rows: {result['row_count']}, Columns: {result['column_count']}")
                
                print("\nSchema:")
                for col in result["schema"]:
                    print(f"  - {col['name']} ({col['type']})")
                    if col['sample_values']:
                        print(f"    Sample values: {col['sample_values']}")
                
                print("\nSample Data:")
                for i, row in enumerate(result["sample_data"][:3]):
                    print(f"  Row {i+1}: {row}")
            else:
                print(f"Error describing dataset: {result['error']}")
        
        # Execute SQL if specified
        if args.execute_sql and args.dataset:
            # This is a bit of a hack since we don't have a direct SQL executor for datasets
            # First we need to create a temporary SQLite database
            import sqlite3
            import pandas as pd
            
            dataset_name = args.dataset
            if dataset_name in db_tool.loaded_datasets:
                df = db_tool.loaded_datasets[dataset_name]["dataframe"]
                
                # Create a temporary in-memory database
                conn = sqlite3.connect(":memory:")
                df.to_sql(dataset_name, conn, index=False, if_exists="replace")
                
                # Execute the query
                result_df = pd.read_sql_query(args.execute_sql, conn)
                
                print(f"\nSQL Query: {args.execute_sql}")
                print(f"Results ({len(result_df)} rows):")
                print(result_df.to_string(index=False))
                
                conn.close()
            else:
                print(f"Error: Dataset '{dataset_name}' not found")
        
        # Execute natural language query if specified
        if args.query:
            dataset_name = args.dataset
            result = db_tool.execute("query", query=args.query, dataset=dataset_name)
            
            if result["status"] == "success":
                print(f"\nQuery: {result['query']}")
                print(f"SQL: {result['sql_query']}")
                print(f"Results ({result['result_count']} rows):")
                print(result['table_format'])
            else:
                print(f"Error executing query: {result['error']}")
        
        # If no specific action was requested, show usage
        if not (args.sample or args.load_csv or args.load_json or args.list_datasets or 
                args.describe or args.execute_sql or args.query):
            parser.print_help()
            print("\nExample usage:")
            print("  python db_query_test.py --sample")
            print("  python db_query_test.py --list-datasets")
            print("  python db_query_test.py --query \"Find employees in Engineering department\"")
            print("  python db_query_test.py --query \"List products with price greater than 300\" --dataset products")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Error in database query test: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 