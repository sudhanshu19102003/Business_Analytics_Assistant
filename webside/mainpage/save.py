from django.shortcuts import render
import mysql.connector
from bokeh.plotting import figure
from bokeh.embed import components
import numpy as np
import random
import string
from bokeh.models import HoverTool




def home(request):
    if request.method == 'POST':
        # Retrieve the input from the form
        input_text = request.POST['input_text']
        print(input_text)
        # Call some Python function with the input as a parameter
        context = some_python_function(input_text)
        # Render the template with the output
        return render(request, 'mainpage/home.html', context)
    else:
        # Render the template without any output
        return render(request, 'mainpage/home.html')

def some_python_function(input_text):
    # Parse the input_text to extract table name and column names
    table_name, column_names, graph_type = input_text.split(':')
    column_names = [c.strip() for c in column_names.split(',')]

    # Connect to the MySQL database
    cnx = mysql.connector.connect(user='root', password='19102003', host='localhost', database='test_db')
    # Construct the SQL query to retrieve data from the specified table and columns
    columns = ', '.join(column_names)
    query = f"SELECT {columns} FROM {table_name}"

    # Execute the SQL query and retrieve the data
    cursor = cnx.cursor()
    cursor.execute(query)
    data = cursor.fetchall()

    ## Check if the first column is a datetime datatype and set the x-axis datatype accordingly
    #first_column_datatype_query = f"SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{column_names[0]}'"
    #cursor.execute(first_column_datatype_query)
    #first_column_datatype = cursor.fetchone()[0]
    #if first_column_datatype == 'datetime':
    #    x_axis_type = 'datetime'
    #else:
    #    x_axis_type = 'linear'

    ## Check if the second column is a datetime datatype and set the y-axis datatype accordingly
    #second_column_datatype_query = f"SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{column_names[1]}'"
    #cursor.execute(second_column_datatype_query)
    #second_column_datatype = cursor.fetchone()[0]
    #if second_column_datatype == 'datetime':
    #    y_axis_type = 'datetime'
    #else:
    #    y_axis_type = 'linear'

    # Set common properties of the plot
    plot_title = f'{graph_type} graph from MySQL data'
    x_label = column_names[0]
    y_label = column_names[1]
    plot_kwargs = dict(title=plot_title, x_axis_label=x_label, y_axis_label=y_label,
                        background_fill_color='#161616',
                          border_fill_color='#161616',
                          sizing_mode='stretch_width',
                        width=1200,height=600,
                        tools=[HoverTool(tooltips=[('x', '@x'), ('y', '@y')])])

    # Generate a graph using the Bokeh library
    if graph_type == 'scatter':
        plot = figure(**plot_kwargs,)
        plot.scatter(x=[row[0] for row in data], y=[row[1] for row in data])
    elif graph_type == 'line':
         # Group the data by year and calculate the total sales for each year
        year_sales = {}
        for row in data:
            year = row[0]
            sales = row[1]
            if year not in year_sales:
                year_sales[year] = 0
            year_sales[year] += sales
    
        # Create a list of x-axis values and y-axis values for the line graph
        x_values = list(year_sales.keys())
        y_values = list(year_sales.values())
    
        # Create the line graph
        plot = figure(**plot_kwargs)
        plot.line(x=x_values, y=y_values)
    elif graph_type == 'bar':
        plot = figure(**plot_kwargs)
        bar_width = min(0.9, 1.5 / len([row[0] for row in data]))
        plot.vbar(x=[row[0] for row in data], top=[row[1] for row in data])
    elif graph_type == 'histogram':
        plot = figure(**plot_kwargs)
        hist, edges = np.histogram([row[1] for row in data], bins='auto')
        colors = ['#'+ ''.join(random.choices(string.hexdigits, k=6)) for i in range(len(hist))]
        plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color=colors)  
    elif graph_type == 'pie':
        plot = figure(**plot_kwargs,aspect=1)
        categories = sorted(set([row[0] for row in data]))
        counts = [sum([row[1] for row in data if row[0] == category]) for category in categories]
        colors = ['#'+ ''.join(random.choices(string.hexdigits, k=6)) for i in range(len(categories))]
        total = sum(counts)
        angles = [count/total*360 for count in counts]
        start_angle = [sum(angles[:i]) for i in range(len(angles))]
        end_angle = [sum(angles[:i+1]) for i in range(len(angles))]
        for i in range(len(angles)):
            plot.wedge(x=0, y=0, radius=0.6, start_angle=start_angle[i]*np.pi/180, end_angle=end_angle[i]*np.pi/180, color=colors[i], legend_label=f"{categories[i]} ({counts[i]})")
        plot.legend.location = "top_right"

    elif graph_type == 'area':
        plot = figure(**plot_kwargs)
        x = [row[0] for row in data]
        y = [row[1] for row in data]
        plot.patch(x + x[::-1], y + [0]*len(y), color='#0080ff', fill_alpha=0.2)
        plot.line(x, y, line_color='#0080ff')

    else:
        return {'error': 'Invalid graph type'}

    # Generate the HTML code for the graph and return it
    script, div = components(plot)
    output_html = {"plot_script": script, "plot_div": div}
    #print(output_html)
    return output_html
