import numpy as np
import pandas as pd
import re
import nltk
import string 
from nltk.corpus import stopwords

nltk.download('stopwords')
stopword = set(stopwords.words('english'))
stemmer = nltk.SnowballStemmer("english")

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# Loading data
df = pd.read_csv("labeled_data.csv")
df["labels"] = df["class"].map({0:"Hate Speech", 1:"Offensive Speech", 2:"No Hate or Offensive Speech"})
df = df[["tweet", "labels"]]

# Cleaning function
def clean(text):
    text = str(text).lower()
    text = re.sub('[,?]', '', text)
    text = re.sub('https?://\S+|www.\S+', '', text)
    text = re.sub('<,?>+', '',text)
    text = re.sub(r'[^\w\s]','',text)
    text = re.sub('\n','',text)
    text = re.sub('\w\d\w', '', text)
    text = [word for word in text.split(' ') if word not in stopword]
    text = " ".join(text)
    text = [stemmer.stem(word) for word in text.split(' ')]
    text = " ".join(text)
    return text

df["tweet"] = df["tweet"].apply(clean)

# Data preparation
x = np.array(df["tweet"])
y = np.array(df["labels"])
cv = CountVectorizer()
x = cv.fit_transform(x)

# Splitting data
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42)

# Model training
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# Predicting and evaluating
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Making a single prediction
input_text = "shut up you look like a shit"
input_text = cv.transform([input_text]).toarray()
print("Prediction:", model.predict(input_text))

import pickle

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(cv, f)