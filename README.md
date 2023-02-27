# Flask-Stock-Tracker

Flask Stock Tracker
Flask Stock Tracker is a simple web application built with Flask that allows users to track the prices of their favorite stocks.

Features
User authentication: Users can create an account and log in to track their stocks.
Stock search: Users can search for stocks by symbol or name.
Stock price tracking: Users can add stocks to their portfolio and track their prices in real-time.
Portfolio performance tracking: Users can view their portfolio's current value and performance over time.
External API integration: Stock prices are retrieved using the Alpha Vantage API.
Getting Started
To run Flask Stock Tracker on your local machine, follow these steps:

Clone this repository:

git clone https://github.com/yourusername/flask-stock-tracker.git
Install the required packages:

pip install -r requirements.txt
Set environment variables:

export FLASK_APP=app
export FLASK_ENV=development
export SECRET_KEY='your_secret_key'
export API_KEY='your_api_key'
Replace your_secret_key with a random string of characters that will be used to encrypt user passwords, and your_api_key with your Alpha Vantage API key.

Initialize the database:

flask db init
flask db migrate -m "Initial migration."
flask db upgrade
Run the application:

flask run
The application should now be running at http://localhost:5000/.

Contributing
If you would like to contribute to Flask Stock Tracker, follow these steps:

Fork this repository.

Create a new branch for your feature or bug fix:

git checkout -b your-feature-branch
Make your changes and commit them with descriptive commit messages:

git add .
git commit -m "Your commit message here."
P
git push origin your-feature-branch
Submit a pull request to the main repository and wait for it to be reviewed and merged.
License
Flask Stock Tracker is licensed under the MIT License.



