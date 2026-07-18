import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

print("1. Downloading dataset (this may take a minute)...")
# We use the same reliable open-source dataset
url = "https://raw.githubusercontent.com/lutzhamel/fake-news/master/data/fake_or_real_news.csv"
df = pd.read_csv(url)

print(f"Dataset loaded successfully with {len(df)} articles.")

# Drop rows that are missing titles or labels
df = df.dropna(subset=['title', 'label'])

print("2. Building vocabulary specifically for SHORT TEXT (Titles/Headlines)...")
# We are training on the 'title' column instead of the 'text' column
tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
tfidf_train = tfidf_vectorizer.fit_transform(df['title'])

print("3. Training the Logistic Regression model...")
classifier = LogisticRegression(max_iter=1000)
classifier.fit(tfidf_train, df['label'])

print("4. Saving the updated model...")
joblib.dump(tfidf_vectorizer, 'vectorizer.pkl')
joblib.dump(classifier, 'model.pkl')

print("Success! Your AI is now optimized for Short Text and Headlines.")