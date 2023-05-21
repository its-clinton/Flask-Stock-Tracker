from flask import Flask, render_template, request, redirect, url_for,session,flash
import requests
import json
import sqlite3
from flask_wtf.csrf import CSRFProtect
from forms import RegistrationForm
from forms import LoginForm
import yfinance as yf
import pandas as pd
# import plotly.graph_objs as go
from flask_login import login_required
from io import BytesIO


app = Flask(__name__)

# set up database
conn = sqlite3.connect('stocktracker.db', check_same_thread=False)
c = conn.cursor()
        
c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT
            );''')

c.execute('''CREATE TABLE IF NOT EXISTS stock_trackers (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                name TEXT,
                symbol TEXT,
                date_added TEXT,
                tracking_price REAL,
                num_shares INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );''')

conn.commit()


@app.route('/')
def index():
    return render_template('home.html')

    
# home page
@app.route('/home')
def home():
    # get all stocks from database
    c.execute("SELECT * FROM stock_tracker")
    rows = c.fetchall()
    
    #retrieve current stock prices from Alpha Vantage API
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=5BF635F8CRSHGB3A'

    response = requests.get(url)

    api_data = response.json()['Time Series (5min)']

    # convert api data to list of dictionaries
    api_data = [{'symbol':'IBM', 
                 'date': key, 
                 'tracking_price': float(value['4. close']),
                'num_shares': int(value['5. volume']),
                'current_price': float(value['4. close']) * int(value['5. volume']),
                'percent_change': round((float(value['4. close']) - float(value['1. open'])) / float(value['1. open']) * 100, 2),
                                        } for key, value in api_data.items()]
 
    # load stocks to be used in html
    stocks = []
    for row in rows:
        stocks.append({
            'id': row[0],
            'symbol': row[1],
            'tracking_price': row[2],
            'num_shares': row[3]
        })

    return render_template('home.html', stocks=stocks, api_data=api_data)




# add stock page
@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    if request.method == 'POST':
        # get form data
        symbol = request.form['symbol']
        tracking_price = float(request.form['tracking_price'])
        num_shares = int(request.form['num_shares'])

        # add stock to database
        c.execute("INSERT INTO stock_tracker (stock_symbol, tracking_price, num_shares) VALUES (?, ?, ?)",
                  (symbol, tracking_price, num_shares))
        conn.commit()

        # redirect to home page
        return redirect(url_for('home'))

    return render_template('add_stock.html')

# remove stock
@app.route('/remove_stock/<int:id>')
def remove_stock(id):
    # remove stock from database
    c.execute("DELETE FROM stock_tracker WHERE id=?", (id,))
    conn.commit()

    # redirect to home page
    return redirect(url_for('home'))

app.secret_key = 'mysecretkey'
        
           
@app.route('/register', methods=['POST', 'GET'])
def register():
    form =RegistrationForm()
    if form.validate_on_submit():
        # process form data
        return redirect('/login')
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # check if username and password are valid
        username = form.username.data
        password = form.password.data
        # perform login logic here
        return redirect(url_for('home'))
    return render_template('login.html', form=form)

#logout
@app.route('/logout')
def logout():
    session.clear()  # clear all session data
    return redirect(url_for('login'))


#visualization
@app.route('/plot')
def plot():
    # Fetch stock data
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=5BF635F8CRSHGB3A'
    response = requests.get(url)
    data = response.json()['Time Series (5min)']
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index = pd.to_datetime(df.index)
    df['close'] = df['4. close'].astype(float)
    # Create plotly figure
    # fig = go.Figure()
    fig.add_trace(go.Histogram(x=df['close'], nbinsx=20))
    fig.update_layout(title='IBM stock prices')
    # Convert plotly figure to HTML string
    plot_html = fig.to_html(full_html=True)
    # Render HTML template with plotly figure
    return render_template('plot.html', plot_html=plot_html)

@app.route('/visualization')
def visualization():
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=5BF635F8CRSHGB3A'
    response = requests.get(url)
    data = response.json()['Time Series (5min)']
    x = []
    y = []
    for key in data:
        x.append(key)
        y.append(float(data[key]['4. close']))

    trace = go.Scatter(x=x, y=y)
    layout = go.Layout(title='IBM Stock Price', xaxis=dict(title='Time'), yaxis=dict(title='Price'))
    fig = go.Figure(data=[trace], layout=layout)
    plot_div = fig.to_html(full_html=False)
    return render_template('visualization.html', plot_div=plot_div)



# run the app
if __name__ == '__main__':
    app.run(debug=True)
    