#!/usr/bin/env python3
"""
Data Visualization Test Script for DreamOS
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

from dreamos.tools.data_viz import DataVizTool
from dreamos.utils.logging_utils import setup_logger

# Setup logging
logger = setup_logger("data_viz_test")

def main():
    """Main entry point for data visualization testing."""
    parser = argparse.ArgumentParser(description="DreamOS Data Visualization Test")
    parser.add_argument("--chart", choices=["bar", "line", "scatter", "pie", "histogram"], 
                        help="Type of chart to create")
    parser.add_argument("--data", type=str, help="Data in JSON format or path to CSV file")
    parser.add_argument("--title", type=str, default="", help="Chart title")
    parser.add_argument("--xlabel", type=str, default="", help="X-axis label")
    parser.add_argument("--ylabel", type=str, default="", help="Y-axis label")
    parser.add_argument("--parse", type=str, help="Parse data from text input or file")
    parser.add_argument("--output", type=str, default="", help="Output filename")
    parser.add_argument("--sample", action="store_true", help="Run with sample data")
    args = parser.parse_args()
    
    try:
        # Initialize the data visualization tool
        print("Initializing data visualization tool...")
        viz_tool = DataVizTool()
        print("Data visualization tool initialized successfully!")
        
        if args.sample:
            # Run with sample data
            print("Creating charts with sample data...")
            
            # Sample bar chart
            sample_data = {
                "Categories": ["A", "B", "C", "D", "E"],
                "Values": [23, 45, 56, 78, 42]
            }
            
            result = viz_tool.create_chart(
                chart_type="bar",
                data=sample_data,
                title="Sample Bar Chart",
                x_label="Categories",
                y_label="Values",
                save=True,
                filename="sample_bar_chart.png"
            )
            
            if result["status"] == "success":
                print(f"Sample bar chart created: {result['filepath']}")
            else:
                print(f"Error creating sample bar chart: {result['error']}")
            
            # Sample pie chart
            sample_pie_data = {
                "Slices": [25, 30, 45]
            }
            
            result = viz_tool.create_chart(
                chart_type="pie",
                data=sample_pie_data,
                title="Sample Pie Chart",
                save=True,
                filename="sample_pie_chart.png"
            )
            
            if result["status"] == "success":
                print(f"Sample pie chart created: {result['filepath']}")
            else:
                print(f"Error creating sample pie chart: {result['error']}")
            
            # Sample line chart
            sample_line_data = {
                "X": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "Y1": [10, 15, 13, 18, 20, 17, 16, 19, 22, 24],
                "Y2": [8, 12, 14, 15, 17, 19, 16, 18, 20, 22]
            }
            
            result = viz_tool.create_chart(
                chart_type="line",
                data=sample_line_data,
                title="Sample Line Chart",
                x_label="X Values",
                y_label="Y Values",
                save=True,
                filename="sample_line_chart.png"
            )
            
            if result["status"] == "success":
                print(f"Sample line chart created: {result['filepath']}")
            else:
                print(f"Error creating sample line chart: {result['error']}")
        
        elif args.parse:
            # Parse data from text or file
            text = args.parse
            
            # Check if it's a file path
            if os.path.exists(text):
                with open(text, 'r') as f:
                    text = f.read()
                print(f"Read data from file: {args.parse}")
            
            # Parse the data
            result = viz_tool.execute("parse_data", text=text)
            
            if result["status"] == "success":
                print(f"Successfully parsed data as {result['format']}")
                print("Parsed data:")
                print(json.dumps(result["data"], indent=2))
                
                # Create a chart if requested
                if args.chart:
                    chart_result = viz_tool.create_chart(
                        chart_type=args.chart,
                        data=result["data"],
                        title=args.title,
                        x_label=args.xlabel,
                        y_label=args.ylabel,
                        save=True,
                        filename=args.output
                    )
                    
                    if chart_result["status"] == "success":
                        print(f"Chart created: {chart_result['filepath']}")
                    else:
                        print(f"Error creating chart: {chart_result['error']}")
            else:
                print(f"Error parsing data: {result['error']}")
        
        elif args.chart and args.data:
            # Create a chart with provided data
            data = args.data
            
            # Check if it's a file path
            if os.path.exists(data):
                with open(data, 'r') as f:
                    content = f.read()
                    
                # Try to parse as JSON
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    # Might be a CSV, let the tool handle it
                    parse_result = viz_tool.execute("parse_data", text=content)
                    if parse_result["status"] == "success":
                        data = parse_result["data"]
                    else:
                        print(f"Error parsing data file: {parse_result['error']}")
                        return 1
            else:
                # Try to parse as JSON string
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    print("Error: Data must be valid JSON or a path to a file")
                    return 1
            
            # Create the chart
            result = viz_tool.create_chart(
                chart_type=args.chart,
                data=data,
                title=args.title,
                x_label=args.xlabel,
                y_label=args.ylabel,
                save=True,
                filename=args.output
            )
            
            if result["status"] == "success":
                print(f"Chart created: {result['filepath']}")
            else:
                print(f"Error creating chart: {result['error']}")
        
        else:
            # Default behavior: show help
            parser.print_help()
            print("\nExample usage:")
            print("  python data_viz_test.py --sample")
            print("  python data_viz_test.py --chart bar --data '{\"A\": [1, 2, 3], \"B\": [4, 5, 6]}'")
            print("  python data_viz_test.py --parse data.csv --chart line")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Error in data visualization test: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 