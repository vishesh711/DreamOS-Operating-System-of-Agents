"""
Database Query Tool for DreamOS
Provides natural language querying of structured data
"""
import os
import re
import json
import sqlite3
import tempfile
from typing import Dict, Any, List, Optional, Tuple, Union
import csv
import pandas as pd
import sqlalchemy
import sqlparse
from tabulate import tabulate

from ..utils.llm_utils import generate_agent_response
from ..utils.logging_utils import get_logger

# Initialize logger
logger = get_logger("database_query")

class DatabaseQueryTool:
    """Tool for querying databases and structured data using natural language."""
    
    def __init__(self):
        """Initialize the database query tool."""
        self.name = "database_query"
        self.description = "Query structured data using natural language"
        self.data_dir = os.path.join("dreamos", "memory", "databases")
        self.temp_db_path = os.path.join(self.data_dir, "temp.db")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Keep track of loaded datasets
        self.loaded_datasets = {}
        self.active_connections = {}
        
        logger.info("Database query tool initialized")
    
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a database query command.
        
        Args:
            command: The command to execute
            **kwargs: Additional arguments for the command
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Executing database query command: {command}")
        
        try:
            if command == "query":
                # Natural language query on loaded data
                query = kwargs.get("query", "")
                dataset_name = kwargs.get("dataset", "")
                
                if not query:
                    return {
                        "status": "error",
                        "error": "No query provided"
                    }
                
                if not dataset_name and not self.loaded_datasets:
                    return {
                        "status": "error",
                        "error": "No dataset specified and no datasets loaded"
                    }
                
                if not dataset_name:
                    # Use the first loaded dataset if none specified
                    dataset_name = next(iter(self.loaded_datasets))
                
                return self.natural_language_query(query, dataset_name)
            
            elif command == "load_csv":
                file_path = kwargs.get("file_path", "")
                dataset_name = kwargs.get("dataset_name", "")
                
                if not file_path:
                    return {
                        "status": "error",
                        "error": "No file path provided"
                    }
                
                if not dataset_name:
                    # Extract dataset name from filename
                    dataset_name = os.path.splitext(os.path.basename(file_path))[0]
                
                return self.load_csv_file(file_path, dataset_name)
            
            elif command == "load_json":
                file_path = kwargs.get("file_path", "")
                dataset_name = kwargs.get("dataset_name", "")
                
                if not file_path:
                    return {
                        "status": "error",
                        "error": "No file path provided"
                    }
                
                if not dataset_name:
                    # Extract dataset name from filename
                    dataset_name = os.path.splitext(os.path.basename(file_path))[0]
                
                return self.load_json_file(file_path, dataset_name)
            
            elif command == "connect_sqlite":
                db_path = kwargs.get("db_path", "")
                connection_name = kwargs.get("connection_name", "")
                
                if not db_path:
                    return {
                        "status": "error",
                        "error": "No database path provided"
                    }
                
                if not connection_name:
                    # Extract connection name from filename
                    connection_name = os.path.splitext(os.path.basename(db_path))[0]
                
                return self.connect_sqlite_db(db_path, connection_name)
            
            elif command == "execute_sql":
                sql = kwargs.get("sql", "")
                connection_name = kwargs.get("connection_name", "")
                
                if not sql:
                    return {
                        "status": "error",
                        "error": "No SQL query provided"
                    }
                
                if not connection_name and not self.active_connections:
                    return {
                        "status": "error",
                        "error": "No connection specified and no active connections"
                    }
                
                if not connection_name:
                    # Use the first active connection if none specified
                    connection_name = next(iter(self.active_connections))
                
                return self.execute_sql_query(sql, connection_name)
            
            elif command == "list_datasets":
                return self.list_loaded_datasets()
            
            elif command == "list_connections":
                return self.list_active_connections()
            
            elif command == "describe_dataset":
                dataset_name = kwargs.get("dataset_name", "")
                
                if not dataset_name and not self.loaded_datasets:
                    return {
                        "status": "error",
                        "error": "No dataset specified and no datasets loaded"
                    }
                
                if not dataset_name:
                    # Use the first loaded dataset if none specified
                    dataset_name = next(iter(self.loaded_datasets))
                
                return self.describe_dataset(dataset_name)
            
            elif command == "describe_database":
                connection_name = kwargs.get("connection_name", "")
                
                if not connection_name and not self.active_connections:
                    return {
                        "status": "error",
                        "error": "No connection specified and no active connections"
                    }
                
                if not connection_name:
                    # Use the first active connection if none specified
                    connection_name = next(iter(self.active_connections))
                
                return self.describe_database(connection_name)
            
            else:
                logger.warning(f"Unknown database query command: {command}")
                return {
                    "status": "error",
                    "error": f"Unknown command: {command}"
                }
        
        except Exception as e:
            logger.error(f"Error executing database query command: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error: {str(e)}"
            }
    
    def natural_language_query(self, query: str, dataset_name: str) -> Dict[str, Any]:
        """
        Execute a natural language query on a dataset.
        
        Args:
            query: Natural language query
            dataset_name: Name of the dataset to query
            
        Returns:
            Query results
        """
        logger.info(f"Executing natural language query on dataset '{dataset_name}': {query}")
        
        try:
            if dataset_name not in self.loaded_datasets:
                return {
                    "status": "error",
                    "error": f"Dataset '{dataset_name}' not found"
                }
            
            # Get dataset info for the context
            dataset = self.loaded_datasets[dataset_name]
            df = dataset["dataframe"]
            
            # Generate schema information for the prompt
            schema_info = self._get_dataframe_schema(df)
            
            # Sample data for context
            sample_data = df.head(5).to_string(index=False)
            
            # Create a prompt for the LLM to convert to SQL
            prompt = f"""
            You are an expert at converting natural language queries into SQL queries.
            
            You have a dataset with the following schema:
            {schema_info}
            
            Here's a sample of the data:
            {sample_data}
            
            Please convert the following natural language query into a valid SQL query:
            "{query}"
            
            Return ONLY the SQL query, with no additional explanation or comments.
            """
            
            # Generate SQL using LLM
            sql_query = generate_agent_response(
                system_prompt=prompt,
                user_input=query,
                context=""
            ).strip()
            
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Clean up the SQL (remove markdown formatting if present)
            sql_query = self._clean_sql_query(sql_query)
            
            # Execute the SQL query on the dataframe
            try:
                # First try to use pandas sql
                result_df = df.query(sql_query, engine='python')
                result_data = result_df.to_dict(orient="records")
            except Exception as pandas_error:
                logger.warning(f"Pandas query failed: {str(pandas_error)}. Trying with SQLite.")
                
                # Fall back to SQLite for more complex queries
                try:
                    # Create a temporary SQLite database
                    conn = sqlite3.connect(":memory:")
                    
                    # Write the dataframe to SQLite
                    df.to_sql(dataset_name, conn, index=False, if_exists="replace")
                    
                    # Execute the query
                    result_df = pd.read_sql_query(sql_query, conn)
                    result_data = result_df.to_dict(orient="records")
                    
                    conn.close()
                except Exception as sqlite_error:
                    logger.error(f"SQLite query failed: {str(sqlite_error)}")
                    return {
                        "status": "error",
                        "error": f"Failed to execute query: {str(sqlite_error)}",
                        "sql_query": sql_query
                    }
            
            # Format as a table for display
            table_format = tabulate(result_df, headers='keys', tablefmt='grid', showindex=False)
            
            return {
                "status": "success",
                "query": query,
                "sql_query": sql_query,
                "result_count": len(result_data),
                "result_data": result_data,
                "table_format": table_format
            }
        
        except Exception as e:
            logger.error(f"Error in natural language query: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error executing query: {str(e)}"
            }
    
    def load_csv_file(self, file_path: str, dataset_name: str) -> Dict[str, Any]:
        """
        Load a CSV file into memory.
        
        Args:
            file_path: Path to the CSV file
            dataset_name: Name to give the dataset
            
        Returns:
            Status of the operation
        """
        logger.info(f"Loading CSV file '{file_path}' as dataset '{dataset_name}'")
        
        try:
            if not os.path.exists(file_path):
                return {
                    "status": "error",
                    "error": f"File not found: {file_path}"
                }
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Store the dataset
            self.loaded_datasets[dataset_name] = {
                "source": file_path,
                "type": "csv",
                "dataframe": df,
                "row_count": len(df),
                "column_count": len(df.columns)
            }
            
            logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
            
            return {
                "status": "success",
                "dataset_name": dataset_name,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns)
            }
        
        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error loading CSV file: {str(e)}"
            }
    
    def load_json_file(self, file_path: str, dataset_name: str) -> Dict[str, Any]:
        """
        Load a JSON file into memory.
        
        Args:
            file_path: Path to the JSON file
            dataset_name: Name to give the dataset
            
        Returns:
            Status of the operation
        """
        logger.info(f"Loading JSON file '{file_path}' as dataset '{dataset_name}'")
        
        try:
            if not os.path.exists(file_path):
                return {
                    "status": "error",
                    "error": f"File not found: {file_path}"
                }
            
            # Read the JSON file
            with open(file_path, 'r') as f:
                json_data = json.load(f)
            
            # Convert to DataFrame
            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            else:
                # Try to handle nested JSON structures
                df = pd.json_normalize(json_data)
            
            # Store the dataset
            self.loaded_datasets[dataset_name] = {
                "source": file_path,
                "type": "json",
                "dataframe": df,
                "row_count": len(df),
                "column_count": len(df.columns)
            }
            
            logger.info(f"Loaded JSON with {len(df)} rows and {len(df.columns)} columns")
            
            return {
                "status": "success",
                "dataset_name": dataset_name,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns)
            }
        
        except Exception as e:
            logger.error(f"Error loading JSON file: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error loading JSON file: {str(e)}"
            }
    
    def connect_sqlite_db(self, db_path: str, connection_name: str) -> Dict[str, Any]:
        """
        Connect to a SQLite database.
        
        Args:
            db_path: Path to the SQLite database file
            connection_name: Name to give the connection
            
        Returns:
            Status of the operation
        """
        logger.info(f"Connecting to SQLite database '{db_path}' as '{connection_name}'")
        
        try:
            if not os.path.exists(db_path):
                return {
                    "status": "error",
                    "error": f"Database file not found: {db_path}"
                }
            
            # Connect to the database
            conn = sqlite3.connect(db_path)
            
            # Get table names
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Store connection
            self.active_connections[connection_name] = {
                "source": db_path,
                "type": "sqlite",
                "connection": conn,
                "tables": tables
            }
            
            logger.info(f"Connected to SQLite database with {len(tables)} tables")
            
            return {
                "status": "success",
                "connection_name": connection_name,
                "tables": tables
            }
        
        except Exception as e:
            logger.error(f"Error connecting to SQLite database: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error connecting to database: {str(e)}"
            }
    
    def execute_sql_query(self, sql: str, connection_name: str) -> Dict[str, Any]:
        """
        Execute a SQL query on a connected database.
        
        Args:
            sql: SQL query to execute
            connection_name: Name of the connection to use
            
        Returns:
            Query results
        """
        logger.info(f"Executing SQL query on connection '{connection_name}': {sql}")
        
        try:
            if connection_name not in self.active_connections:
                return {
                    "status": "error",
                    "error": f"Connection '{connection_name}' not found"
                }
            
            connection_info = self.active_connections[connection_name]
            conn = connection_info["connection"]
            
            # Execute the query
            result_df = pd.read_sql_query(sql, conn)
            result_data = result_df.to_dict(orient="records")
            
            # Format as a table for display
            table_format = tabulate(result_df, headers='keys', tablefmt='grid', showindex=False)
            
            return {
                "status": "success",
                "sql_query": sql,
                "result_count": len(result_data),
                "result_data": result_data,
                "table_format": table_format
            }
        
        except Exception as e:
            logger.error(f"Error executing SQL query: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error executing SQL query: {str(e)}"
            }
    
    def list_loaded_datasets(self) -> Dict[str, Any]:
        """
        List all loaded datasets.
        
        Returns:
            Information about loaded datasets
        """
        logger.info("Listing loaded datasets")
        
        datasets_info = []
        for name, info in self.loaded_datasets.items():
            datasets_info.append({
                "name": name,
                "source": info["source"],
                "type": info["type"],
                "row_count": info["row_count"],
                "column_count": info["column_count"]
            })
        
        return {
            "status": "success",
            "datasets_count": len(datasets_info),
            "datasets": datasets_info
        }
    
    def list_active_connections(self) -> Dict[str, Any]:
        """
        List all active database connections.
        
        Returns:
            Information about active connections
        """
        logger.info("Listing active database connections")
        
        connections_info = []
        for name, info in self.active_connections.items():
            connections_info.append({
                "name": name,
                "source": info["source"],
                "type": info["type"],
                "tables": info["tables"]
            })
        
        return {
            "status": "success",
            "connections_count": len(connections_info),
            "connections": connections_info
        }
    
    def describe_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a dataset.
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            Dataset information
        """
        logger.info(f"Describing dataset '{dataset_name}'")
        
        try:
            if dataset_name not in self.loaded_datasets:
                return {
                    "status": "error",
                    "error": f"Dataset '{dataset_name}' not found"
                }
            
            dataset = self.loaded_datasets[dataset_name]
            df = dataset["dataframe"]
            
            # Get schema information
            schema_info = self._get_dataframe_schema(df)
            
            # Get sample data
            sample_data = df.head(5).to_dict(orient="records")
            
            # Get basic stats
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            stats = {}
            
            if numeric_columns:
                stats_df = df[numeric_columns].describe().transpose()
                stats = stats_df.to_dict()
            
            return {
                "status": "success",
                "dataset_name": dataset_name,
                "source": dataset["source"],
                "type": dataset["type"],
                "row_count": dataset["row_count"],
                "column_count": dataset["column_count"],
                "schema": schema_info,
                "sample_data": sample_data,
                "stats": stats
            }
        
        except Exception as e:
            logger.error(f"Error describing dataset: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error describing dataset: {str(e)}"
            }
    
    def describe_database(self, connection_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a database.
        
        Args:
            connection_name: Name of the connection
            
        Returns:
            Database information
        """
        logger.info(f"Describing database '{connection_name}'")
        
        try:
            if connection_name not in self.active_connections:
                return {
                    "status": "error",
                    "error": f"Connection '{connection_name}' not found"
                }
            
            connection_info = self.active_connections[connection_name]
            conn = connection_info["connection"]
            tables = connection_info["tables"]
            
            # Get schema for each table
            tables_schema = {}
            for table in tables:
                # Get column info
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table});")
                columns = cursor.fetchall()
                
                table_schema = []
                for col in columns:
                    table_schema.append({
                        "name": col[1],
                        "type": col[2],
                        "notnull": bool(col[3]),
                        "pk": bool(col[5])
                    })
                
                tables_schema[table] = table_schema
            
            return {
                "status": "success",
                "connection_name": connection_name,
                "source": connection_info["source"],
                "type": connection_info["type"],
                "tables_count": len(tables),
                "tables": tables,
                "schema": tables_schema
            }
        
        except Exception as e:
            logger.error(f"Error describing database: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error describing database: {str(e)}"
            }
    
    def _get_dataframe_schema(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Get schema information for a DataFrame.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            List of column information
        """
        schema = []
        for col_name, dtype in zip(df.columns, df.dtypes):
            # Get sample values
            non_null_values = df[col_name].dropna()
            sample_values = non_null_values.head(3).tolist() if len(non_null_values) > 0 else []
            
            schema.append({
                "name": col_name,
                "type": str(dtype),
                "nullable": df[col_name].isnull().any(),
                "sample_values": sample_values
            })
        
        return schema
    
    def _clean_sql_query(self, sql: str) -> str:
        """
        Clean up an SQL query generated by an LLM.
        
        Args:
            sql: SQL query string
            
        Returns:
            Cleaned SQL query
        """
        # Remove markdown code block formatting
        sql = re.sub(r'^```sql', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'^```', '', sql, flags=re.MULTILINE)
        
        # Remove any leading/trailing whitespace
        sql = sql.strip()
        
        # Format the SQL for better readability
        try:
            formatted_sql = sqlparse.format(
                sql,
                reindent=True,
                keyword_case='upper'
            )
            return formatted_sql
        except:
            # Return original if formatting fails
            return sql
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the database query tool.
        
        Returns:
            Dictionary with tool information
        """
        return {
            "name": self.name,
            "description": self.description,
            "usage": "database_query.execute('command', **kwargs)",
            "commands": [
                "query - Execute a natural language query on a dataset",
                "load_csv - Load a CSV file as a dataset",
                "load_json - Load a JSON file as a dataset",
                "connect_sqlite - Connect to a SQLite database",
                "execute_sql - Execute a SQL query on a connected database",
                "list_datasets - List all loaded datasets",
                "list_connections - List all active database connections",
                "describe_dataset - Get detailed information about a dataset",
                "describe_database - Get detailed information about a database"
            ]
        } 