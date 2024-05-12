from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load your trained model and CountVectorizer
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('vectorizer.pkl', 'rb') as f:
    cv = pickle.load(f)

analyzer = SentimentIntensityAnalyzer()

# Dummy user storage
users = {'user@example.com': {'password': 'securepassword'}}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

    @classmethod
    def get(cls, id):
        if id in users:
            return cls(id)
        return None

    def check_password(self, password):
        return users.get(self.id)['password'] == password

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/cyberbullying')
@login_required
def cyberbullying():
    return render_template('cyberbullying.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

from flask import send_from_directory

from flask import send_from_directory

@app.route('/download-dataset')
@login_required
def download_dataset():
    directory = "https://drive.google.com/file/d/1b74BeAGqcm9coDpGNIyE4aiarUF8Jz3m/view?usp=sharing"  # Adjust this to the actual path where your dataset is stored
    filename = "labeled_data.csv"
    return send_from_directory(directory, filename, as_attachment=True, download_name=filename)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get(form.username.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

import requests

@app.route('/cyber-crime-news')
@login_required
def cyber_crime_news():
    api_key = "d31c9f7ea1244535a46d9503173fc144"
    # Enhanced search query to focus on "cyber crime"
    url = f"https://newsapi.org/v2/everything?q=cybercrime OR \"cyber crime\"&sortBy=relevance&language=en&apiKey={api_key}"
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return render_template('cyber.html', articles=articles)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')  

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    if request.method == 'POST':
        message = request.form['message']
        data = [message]
        vect = cv.transform(data).toarray()
        prediction = model.predict(vect)
        
        sentiment = analyzer.polarity_scores(message)
        sentiment_result = "Positive" if sentiment['compound'] > 0.05 else "Neutral" if sentiment['compound'] > -0.05 else "Negative"

        return render_template('result.html', prediction=prediction[0], sentiment=sentiment_result)

if __name__ == '__main__':
    app.run(debug=True)
