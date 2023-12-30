import pywhatkit as py
search = input("Enter your query: ")
try:
    py.search(search)
except:
    print("Unexpected Error")