"""
Data Visualization Tool for DreamOS
Provides capabilities to create charts and visualize data
"""
import os
import io
import base64
import json
import tempfile
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from ..utils.logging_utils import get_logger

# Initialize logger
logger = get_logger("data_viz")

class DataVizTool:
    """Tool for creating data visualizations and charts."""
    
    def __init__(self):
        """Initialize the data visualization tool."""
        self.name = "data_viz"
        self.description = "Creates charts and visualizations from data"
        self.output_dir = os.path.join("dreamos", "memory", "visualizations")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("Data visualization tool initialized")
    
    def create_chart(self, chart_type: str, data: Any, title: str = "", 
                     x_label: str = "", y_label: str = "",
                     save: bool = True, filename: str = "") -> Dict[str, Any]:
        """
        Create a chart from data.
        
        Args:
            chart_type: Type of chart ('bar', 'line', 'scatter', 'pie', 'histogram')
            data: Data to visualize (can be dict, list, or pandas DataFrame)
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            save: Whether to save the chart to a file
            filename: Name for the saved file (without extension)
            
        Returns:
            Dict with chart information and path to saved file
        """
        logger.info(f"Creating {chart_type} chart: {title}")
        
        try:
            # Convert data to appropriate format
            df = self._convert_to_dataframe(data)
            
            # Create the chart
            plt.figure(figsize=(10, 6))
            
            if chart_type == "bar":
                df.plot(kind="bar", ax=plt.gca())
            elif chart_type == "line":
                df.plot(kind="line", ax=plt.gca())
            elif chart_type == "scatter":
                # For scatter, we need x and y columns
                if len(df.columns) < 2:
                    df['index'] = df.index
                    x_col = 'index'
                    y_col = df.columns[0]
                else:
                    x_col = df.columns[0]
                    y_col = df.columns[1]
                df.plot(kind="scatter", x=x_col, y=y_col, ax=plt.gca())
            elif chart_type == "pie":
                df.iloc[0].plot(kind="pie", autopct='%1.1f%%')
            elif chart_type == "histogram":
                df.plot(kind="hist", ax=plt.gca())
            else:
                logger.error(f"Unsupported chart type: {chart_type}")
                return {
                    "status": "error",
                    "error": f"Unsupported chart type: {chart_type}"
                }
            
            # Add labels and title
            plt.title(title)
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.tight_layout()
            
            # Save or return the chart
            if save:
                # Generate filename if not provided
                if not filename:
                    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{chart_type}_chart_{timestamp}"
                
                # Ensure filename has .png extension
                if not filename.endswith(".png"):
                    filename += ".png"
                
                # Save the chart
                filepath = os.path.join(self.output_dir, filename)
                plt.savefig(filepath)
                logger.info(f"Chart saved to {filepath}")
                
                return {
                    "status": "success",
                    "chart_type": chart_type,
                    "title": title,
                    "filepath": filepath
                }
            else:
                # Convert plot to base64 for display
                img_data = io.BytesIO()
                plt.savefig(img_data, format='png')
                img_data.seek(0)
                img_b64 = base64.b64encode(img_data.read()).decode()
                
                return {
                    "status": "success",
                    "chart_type": chart_type,
                    "title": title,
                    "image_data": img_b64
                }
        
        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error creating chart: {str(e)}"
            }
        finally:
            plt.close()
    
    def parse_data_from_text(self, text: str) -> Dict[str, Any]:
        """
        Parse data from text input (CSV, JSON, or plain text).
        
        Args:
            text: Input text containing data
            
        Returns:
            Dict with parsed data and format information
        """
        logger.info("Parsing data from text")
        
        try:
            # Try to parse as JSON
            try:
                data = json.loads(text)
                logger.debug("Successfully parsed as JSON")
                return {
                    "status": "success",
                    "format": "json",
                    "data": data
                }
            except json.JSONDecodeError:
                pass
            
            # Try to parse as CSV
            try:
                # Write to temp file for pandas to read
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as tmp:
                    tmp.write(text)
                    tmp_path = tmp.name
                
                df = pd.read_csv(tmp_path)
                os.unlink(tmp_path)  # Delete temp file
                
                logger.debug("Successfully parsed as CSV")
                return {
                    "status": "success",
                    "format": "csv",
                    "data": df.to_dict(orient="list")
                }
            except Exception:
                pass
            
            # Try to parse as space/tab separated values
            try:
                lines = text.strip().split('\n')
                data = []
                for line in lines:
                    if line.strip():
                        data.append(line.split())
                
                if data and len(data) > 1:
                    # Convert to dict for easier plotting
                    headers = data[0]
                    values = data[1:]
                    result = {h: [row[i] if i < len(row) else None for row in values] 
                             for i, h in enumerate(headers)}
                    
                    logger.debug("Successfully parsed as space/tab separated values")
                    return {
                        "status": "success",
                        "format": "table",
                        "data": result
                    }
            except Exception:
                pass
            
            # If all else fails, try to extract numbers
            import re
            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
            if numbers:
                data = [float(n) for n in numbers]
                logger.debug("Extracted numbers from text")
                return {
                    "status": "success",
                    "format": "numbers",
                    "data": {"values": data}
                }
            
            logger.warning("Could not parse data from text")
            return {
                "status": "error",
                "error": "Could not parse data from text. Please provide data in JSON, CSV, or table format."
            }
        
        except Exception as e:
            logger.error(f"Error parsing data from text: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error parsing data from text: {str(e)}"
            }
    
    def _convert_to_dataframe(self, data: Any) -> pd.DataFrame:
        """
        Convert input data to a pandas DataFrame.
        
        Args:
            data: Input data (dict, list, or DataFrame)
            
        Returns:
            pandas DataFrame
        """
        if isinstance(data, pd.DataFrame):
            return data
        
        if isinstance(data, dict):
            return pd.DataFrame(data)
        
        if isinstance(data, list):
            # Check if list of dicts
            if all(isinstance(item, dict) for item in data):
                return pd.DataFrame(data)
            # Check if list of lists
            elif all(isinstance(item, (list, tuple)) for item in data):
                return pd.DataFrame(data)
            # List of values
            else:
                return pd.DataFrame({"values": data})
        
        # If we can't convert, raise an error
        raise ValueError("Could not convert data to DataFrame")
    
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a data visualization command.
        
        Args:
            command: The command to execute
            **kwargs: Additional arguments for the command
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Executing data visualization command: {command}")
        
        try:
            if command == "create_chart":
                chart_type = kwargs.get("chart_type", "bar")
                data = kwargs.get("data", {})
                title = kwargs.get("title", "")
                x_label = kwargs.get("x_label", "")
                y_label = kwargs.get("y_label", "")
                save = kwargs.get("save", True)
                filename = kwargs.get("filename", "")
                
                return self.create_chart(
                    chart_type=chart_type,
                    data=data,
                    title=title,
                    x_label=x_label,
                    y_label=y_label,
                    save=save,
                    filename=filename
                )
            
            elif command == "parse_data":
                text = kwargs.get("text", "")
                
                if not text:
                    return {
                        "status": "error",
                        "error": "No text provided for parsing"
                    }
                
                return self.parse_data_from_text(text)
            
            else:
                logger.warning(f"Unknown data visualization command: {command}")
                return {
                    "status": "error",
                    "error": f"Unknown command: {command}"
                }
        
        except Exception as e:
            logger.error(f"Error executing data visualization command: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error: {str(e)}"
            }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the data visualization tool.
        
        Returns:
            Dictionary with tool information
        """
        return {
            "name": self.name,
            "description": self.description,
            "usage": "data_viz.execute('create_chart', chart_type='bar', data=data_dict)",
            "examples": [
                "data_viz.execute('create_chart', chart_type='bar', data={'A': [1, 2, 3], 'B': [4, 5, 6]})",
                "data_viz.execute('parse_data', text='A,B,C\\n1,2,3\\n4,5,6')"
            ],
            "commands": ["create_chart", "parse_data"],
            "chart_types": ["bar", "line", "scatter", "pie", "histogram"]
        } 