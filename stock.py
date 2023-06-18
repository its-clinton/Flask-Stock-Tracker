from flask import Flask, render_template, request, redirect, url_for,session
import requests
import json
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from io import BytesIO
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
# create flask app

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

app.app_context().push()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), unique=False, nullable=False)

    
    def __repr__(self):
        return '<User %r>' % self.email
        
# admin view
admin = Admin(app)
admin.add_view(ModelView(User, db.session))

# login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return render_template('auth/index.html')
    else:
        return render_template('home2.html')

# register view
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db.session.add(User(email=request.form['email'], password=request.form['password']))
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('auth/index.html', message="User Already Exists")
    else:
        return render_template('auth/register.html')

# login view
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    else:
        e = request.form['email']
        p = request.form['password']
        data = User.query.filter_by(email=e, password=p).first()
        if data is not None:
            session['logged_in'] = True
            return redirect(url_for('home'))
        return render_template('auth/error.html', error="Incorrect Details")


# main page
@app.route('/home')
def home():
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
 

    return render_template('home2.html',  api_data=api_data)


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
    fig = go.Figure()
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

# logout view
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return render_template('auth/index.html')

# run the app
if __name__ == '__main__':
    app.secret_key = "ThisIsNotASecret:p"
    db.create_all()
    app.run(debug=True)
    