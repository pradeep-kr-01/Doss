# Importing necessary library
from googlesearch import search

# The query you want to search
query = input("Enter your Query: ")

# Performing the search
for url in search(query, num_results=10):
    print(url)