# DreamOS Data Visualization

The data visualization feature in DreamOS allows you to create charts and visualize data directly from the command line or through the terminal agent.

## Features

- Create various types of charts (bar, line, scatter, pie, histogram)
- Parse data from text or files in different formats (JSON, CSV, space/tab-separated values)
- Save visualizations to files
- Integration with the DreamOS terminal agent

## Usage

### Command Line Interface

You can use the data visualization feature directly from the command line using the `data_viz_test.py` script:

```bash
# Create a sample visualization
python data_viz_test.py --sample

# Create a specific chart
python data_viz_test.py --chart bar --data '{"Categories": ["A", "B", "C"], "Values": [10, 20, 30]}' --title "My Chart" --xlabel "Categories" --ylabel "Values"

# Parse data from a file and create a chart
python data_viz_test.py --parse data.csv --chart line --title "Data from CSV"
```

### Terminal Agent Commands

When running DreamOS, you can use the following commands:

```
# Show data visualization help
viz help

# Create a chart
viz create bar {"Categories": ["A", "B", "C"], "Values": [10, 20, 30]} --title=My Chart --xlabel=Categories --ylabel=Values

# Parse data from text or file
viz parse data.csv
```

## Enabling Data Visualization

To enable data visualization in DreamOS, use the `--dataviz` flag when starting DreamOS:

```bash
python run_dreamos.py --dataviz
```

## Requirements

- matplotlib
- pandas
- numpy

These dependencies are included in the requirements.txt file.

## Output Directory

By default, charts are saved to the `dreamos/memory/visualizations` directory.

## Examples

### Creating a Bar Chart

```
viz create bar {"Categories": ["Product A", "Product B", "Product C"], "Values": [125, 89, 234]} --title=Sales by Product --xlabel=Product --ylabel=Units Sold
```

### Creating a Line Chart

```
viz create line {"X": [1, 2, 3, 4, 5], "Y1": [10, 15, 13, 17, 20], "Y2": [8, 12, 15, 13, 18]} --title=Performance Over Time --xlabel=Time --ylabel=Performance
```

### Creating a Pie Chart

```
viz create pie {"Segments": [25, 30, 45]} --title=Market Share
```

### Parsing CSV Data

```
viz parse "A,B,C\n10,20,30\n15,25,35"
``` 