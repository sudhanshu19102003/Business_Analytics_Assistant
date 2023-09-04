import string
from django.shortcuts import render
import mysql.connector
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.models import BoxZoomTool, PanTool, ResetTool, WheelZoomTool
import numpy as np
from bokeh.palettes import Spectral,Spectral11
from math import pi
import random

# define a global list to store the previous outputs
MAX_PREVIOUS_OUTPUTS = 10
previous_outputs = []

def home(request):
    if request.method == 'POST':
        # Retrieve the input from the form
        input_text = request.POST['input_text']
        print(input_text)
        # Call some Python function with the input as a parameter
        bokeh_plot = graph(input_text)
        # Append the output to the list of previous outputs
        previous_outputs.insert(0, bokeh_plot)
        # If the list of previous outputs exceeds the maximum size, remove the oldest output
        if len(previous_outputs) > MAX_PREVIOUS_OUTPUTS:
            del previous_outputs[0]
        # Create a context dictionary with the current and previous outputs
        context = {'current_output': bokeh_plot, 'previous_outputs': previous_outputs}
        # Render the template with the outputs
        return render(request, 'mainpage/home.html', context)
    else:
        # Render the template with the previous outputs
        context = {'previous_outputs': previous_outputs}
        return render(request, 'mainpage/home.html', context)


def graph(input_text):
    table_name= "sales"
    column_names, graph_type = input_text.split(':')
    column_names = [c.strip() for c in column_names.split(',')]
    df = get_data(column_names,table_name)
    if graph_type == "scatter":
        plot = scatter_plot(df)
    elif graph_type == "line":
        plot = line_plot(df)
    elif graph_type == "bar":
        plot = bar_plot(df)
    elif graph_type == "histogram":
        plot = histogram(df)
    elif graph_type == "pie":
        plot = pie_chart(df)
    else:
        plot = None
    script, div = components(plot)
    output_html = {"plot_script": script, "plot_div": div}
    return output_html


def get_data(column_names,table_name):
    # Connect to the MySQL database
    cnx = mysql.connector.connect(user='root', password='19102003', host='localhost', database='test_db')
    # Construct the SQL query to retrieve data from the specified table and columns
    _columns = ', '.join(column_names)
    query = f"SELECT {_columns} FROM {table_name}"

    # Execute the SQL query and retrieve the data
    cursor = cnx.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=column_names)
    if column_names[0] == "ORDERDATE":
        df[column_names[0]] = pd.to_datetime(df[column_names[0]], errors='coerce')
        print("yes")
    if column_names[1] == "ORDERDATE":
        df[column_names[1]] = pd.to_datetime(df[column_names[1]], errors='coerce')
        print("yes")
    print(df)
    return df

def plot_properties(df):
    x_column, y_column = df.columns[:2]

    x_dtype = df[x_column].dtype
    y_dtype = df[y_column].dtype
    if x_dtype == "datetime64[ns]":
        x_type = 'datetime'
        print("date")
    else:
        x_type = None  

    print(x_dtype, y_dtype)

    plot_kwargs = dict(background_fill_color='#161616',
                       border_fill_color='#161616',
                       sizing_mode='stretch_width',
                       width=1200, height=600,
                       tools=[BoxZoomTool(), PanTool(), ResetTool(), WheelZoomTool(), HoverTool(tooltips=[(x_column, '@{' + x_column + '}'), (y_column, '@{' + y_column + '}')])],
                       x_axis_type=x_type
                       )
    return plot_kwargs

def scatter_plot(df):
    # Get the names of the two columns from the DataFrame
    x_column, y_column = df.columns[:2]

    # Create a ColumnDataSource from the DataFrame
    source = ColumnDataSource(df)

    plot_kwargs = plot_properties(df)

    # Create the figure and add the scatter plot
    plot = figure(title='Scatter Plot', x_axis_label=x_column, y_axis_label=y_column,**plot_kwargs,)
    plot.scatter(x=x_column, y=y_column, source=source)

    return plot 

def line_plot(df):
    # Get the names of the two columns from the DataFrame
    x_column, y_column = df.columns[:2]

    # Create a ColumnDataSource from the DataFrame
    source = ColumnDataSource(df)

    plot_kwargs = plot_properties(df)

    # Create the figure and add the line plot
    plot = figure(title='Line Plot', x_axis_label=x_column, y_axis_label=y_column, **plot_kwargs)
    plot.line(x=x_column, y=y_column, source=source)

    return plot

def bar_plot(df):
    # Get the names of the two columns from the DataFrame
    x_column, y_column = df.columns[:2]

    # Create a ColumnDataSource from the DataFrame
    source = ColumnDataSource(df)

    plot_kwargs = plot_properties(df)

    # Create the figure and add the bar plot
    plot = figure(title='Bar Plot', x_axis_label=x_column, y_axis_label=y_column, **plot_kwargs)
    plot.vbar(x=x_column, top=y_column, width=0.5, source=source)

    return plot
def histogram(df):
    # Get the names of the columns from the DataFrame
    x_column = df.columns[0]
    # Create a ColumnDataSource from the DataFrame
    source = ColumnDataSource(df)
    
    # Define plot_kwargs or pass appropriate arguments directly to figure()
    plot_kwargs = plot_properties(df)  # Update this with desired properties

    hist, edges = np.histogram(df[x_column], bins='auto')
    colors = ['#'+ ''.join(random.choices(string.hexdigits, k=6)) for i in range(len(hist))]
    # Create the figure and add the histogram
    plot = figure(title='Histogram', x_axis_label=x_column, y_axis_label='Count', **plot_kwargs)
    plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color=colors)
    return plot

def pie_chart(df):
    # Get the names of the columns from the DataFrame
    x_column = df.columns[0]
    # Create a ColumnDataSource from the DataFrame
    source = ColumnDataSource(df)

    # Define plot_kwargs or pass appropriate arguments directly to figure()
    plot_kwargs = plot_properties(df)  # Update this with desired properties

    plot = figure(**plot_kwargs, aspect_ratio=1)
    categories = sorted(set(df[x_column]))
    counts = [sum([row[1] for row in df.iterrows() if row[1][x_column] == category]) for category in categories]
    colors = ['#' + ''.join(random.choices(string.hexdigits, k=6)) for i in range(len(categories))]
    total = sum(counts)
    angles = [count / total * 360 for count in counts]
    start_angle = [sum(angles[:i]) for i in range(len(angles))]
    end_angle = [sum(angles[:i + 1]) for i in range(len(angles))]
    for i in range(len(angles)):
        plot.wedge(x=0, y=0, radius=0.6, start_angle=start_angle[i] * np.pi / 180,
                   end_angle=end_angle[i] * np.pi / 180, color=colors[i],
                   legend_label=f"{categories[i]} ({counts[i]})")
    plot.legend.location = "top_right"

    return plot


