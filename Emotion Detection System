import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Example dataset (replace this with your actual dataset)
data = {
    'text': [
        "I'm so happy today!", 
        "This is so frustrating.", 
        "I love my life!", 
        "I feel terrible...", 
        "Why is this happening to me?", 
        "Everything is awesome!"
    ],
    'emotion': ['happy', 'angry', 'happy', 'sad', 'angry', 'happy']
}
df = pd.DataFrame(data)

# Preprocessing function
def preprocess_text(text):
    tokens = word_tokenize(text.lower())  # Convert to lowercase and tokenize
    tokens = [word for word in tokens if word.isalpha()]  # Remove punctuation
    tokens = [word for word in tokens if word not in stopwords.words('english')]  # Remove stopwords
    return ' '.join(tokens)

# Apply preprocessing to the text data
df['text'] = df['text'].apply(preprocess_text)

# Vectorize the text data using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df['text']).toarray()
y = df['emotion']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Logistic Regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Predict on the test data
y_pred = model.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))

# Predict the emotion of a new text
new_text = "I am feeling fantastic!"
new_text_preprocessed = preprocess_text(new_text)
new_text_vectorized = vectorizer.transform([new_text_preprocessed]).toarray()

predicted_emotion = model.predict(new_text_vectorized)
print(f"Predicted Emotion: {predicted_emotion[0]}")
