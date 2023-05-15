# routes.py
from flask import Blueprint, render_template
from flask import request, jsonify
from pymongo import MongoClient
import spacy
import csv

main = Blueprint('main', __name__)

# Load spaCy's language model
nlp = spacy.load("en_core_web_sm")

# Replace with your MongoDB connection string
client = MongoClient(
    'mongodb+srv://BabarJawad:UawWvf1V6YAVRqWF@cluster0.v5rvh.mongodb.net/Virtual-Wakeel?retryWrites=true&w=majority')

# Replace 'virtual_lawyer' with your database name
db = client['Virtual-Wakeel']
# collection = db["uploads.files"]
# documents = collection.find()
# print(documents)
# for document in documents:
#     print(document)

def search(query):
    
   
    keywords = get_keywords(query)

    print(keywords)

    res = read_csv(keywords)
    # search_cases = db.cases.find({"$text": {"$search": " ".join(keywords)}})
    # search_lawyers = db.lawyers.find({"$text": {"$search": " ".join(keywords)}})

    # cases = [case for case in search_cases]
    # lawyers = [lawyer for lawyer in search_lawyers]

    # search_results = {
    #     "cases": cases,
    #     "lawyers": lawyers
    # }
    return res

def search_advocates(query):
    keywords = get_keywords(query)
    adv_collection = db["advroles"]
    documents = adv_collection.find({'status': 'accepted'})

    data = []

    # Iterate over the documents and add them to the list
    for document in documents:
        document['_id'] = str(document['_id'])
        data.append(document)

    # filtered_data = [item for item in data if any(keyword.lower() in item['interest'].lower() for keyword in keywords)]
    filtered_data = [item for item in data if any(keyword.lower() in [interest.lower() for interest in get_keywords(item['interest'].lower())] for keyword in keywords)]
    return filtered_data


def get_keywords(query):
    doc = nlp(query)

    # Extract lemmatized tokens from the processed 'doc' and use them in your search queries
    # keywords = [token.lemma_ for token in doc]
    nouns = [token.text for token in doc if token.pos_ == 'NOUN']
    verbs = [token.text for token in doc if token.pos_ == 'VERB']
    adj = [token.text for token in doc if token.pos_ == 'ADJ']

    return nouns + verbs + adj


@main.route('/')
def index():
    return "Hello, World!"

# Handle POST requests to the /search route

# read Csv files to get results
def read_csv(keywords):
    results = []
    search_columns = ['CaseNo', 'Title']
    csv_file='cases.csv'
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for keyword in keywords:
                for column in search_columns:
                    if keyword.lower() in row[column].lower():
                        results.append(row)
                        break  # Break the inner loop if a match is found in any column
    return results



@main.route('/search', methods=['POST'])
def handle_search():
    query = request.json['query']
    search_results = search(query)
    # print(search_results)
    return jsonify({'data':search_results,'total_records':len(search_results)})

@main.route('/advocate', methods=['POST'])
def handle_advocate_search():
    query = request.json['query']
    search_results = search_advocates(query)
    print(search_results)
    # return search_results
    return jsonify({'data':search_results,'total_records':len(search_results)})
