import plotly.graph_objects as go
import plotly.express as px
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['kabu']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Save the data to MongoDB
        data = {col: request.form[col] for col in request.form}
        db.form_data.insert_one(data)

        return redirect(url_for('index'))

    return render_template('form.html')

@app.route('/excel', methods=['GET', 'POST'])
def excel_upload():
    if request.method == 'POST':
        # Read the uploaded Excel file and save the data to MongoDB
        file = request.files['file']
        if file.filename.endswith('.xlsx'):
            data_df = pd.read_excel(file)
            data = data_df.to_dict(orient='records')
            db.excel_data.insert_many(data)

            return redirect(url_for('index'))

    return render_template('excel_upload.html')

@app.route('/piechart')
def pie_chart():
    # Fetch data from MongoDB for pie charts
    data = list(db.form_data.find({}, {'_id': 0}))

    # Create a list to store pie chart HTML
    pie_charts = []

    # Check if there is data in the 'form_data' collection
    if data:
        # Create a pie chart for each column
        for column in data[0]:
            column_counts = {item[column] for item in data if item[column]}
            labels = list(column_counts)
            values = [len([item for item in data if item[column] == label]) for label in labels]
            fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
            pie_chart_html = fig.to_html(full_html=False)
            pie_charts.append(pie_chart_html)

    return render_template('pie_chart.html', pie_charts=pie_charts)

@app.route('/bargraph')
def bar_graph_route():
    # Fetch data from MongoDB for bar graphs
    data = list(db.form_data.find({}, {'_id': 0}))

    # Create a list to store bar graph HTML
    bar_graphs = []

    # Check if there is data in the 'form_data' collection
    if data:
        # Create bar graphs for each column
        for column in data[0]:
            column_counts = {item[column] for item in data if item[column]}
            labels = list(column_counts)
            values = [len([item for item in data if item[column] == label]) for label in labels]
            fig = px.bar(x=labels, y=values, title=f'Bar Graph for {column}')
            bar_graph_html = fig.to_html(full_html=False)
            bar_graphs.append(bar_graph_html)

    return render_template('bar_graph.html', bar_graphs=bar_graphs)

@app.route('/scatterplot')
def scatter_plot():
    # Fetch data from MongoDB for scatter plot
    data = list(db.form_data.find({}, {'_id': 0}))

    # Create a scatter plot for each pair of columns
    scatter_plots = []
    for i in range(len(data[0])):
        for j in range(i + 1, len(data[0])):
            x_data = [item[list(data[0])[i]] for item in data]
            y_data = [item[list(data[0])[j]] for item in data]

            fig = go.Figure(data=go.Scatter(x=x_data, y=y_data, mode='markers'))
            scatter_plot_html = fig.to_html(full_html=False)
            scatter_plots.append(scatter_plot_html)

    return render_template('scatter_plot.html', scatter_plots=scatter_plots)

@app.route('/view_visualizations')
def view_visualizations():
    return render_template('view_visualizations.html')

if __name__ == '__main__':
    app.run(debug=True)
