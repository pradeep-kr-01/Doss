import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Sample data creation
data = {
    'YearsExperience': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'EducationLevel': [1, 2, 2, 3, 3, 4, 4, 5, 5, 6],  # e.g., 1 = High School, 6 = PhD
    'Salary': [40000, 45000, 50000, 55000, 60000, 65000, 70000, 75000, 80000, 85000]
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Features and target variable
X = df[['YearsExperience', 'EducationLevel']]
y = df['Salary']

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# Example prediction
example_data = pd.DataFrame({'YearsExperience': [5], 'EducationLevel': [3]})
predicted_salary = model.predict(example_data)
print(f"Predicted Salary for 5 years experience and education level 3: ${predicted_salary[0]:,.2f}")
