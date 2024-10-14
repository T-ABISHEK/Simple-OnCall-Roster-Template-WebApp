from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, template_folder='templates')

# Connect to MongoDB database
mongodb_url = os.getenv('MONGODBURL')

# Connect to MongoDB database
client = MongoClient(mongodb_url)
db = client['Penny']
collection = db['Penny']


# Home page with two buttons and list of employees
@app.route('/')
def home():
    employees = collection.find()
    return render_template('home.html', employees=employees)


@app.route('/create', methods=['GET', 'POST'])
def create():
    error_message = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        team = request.form['team']
        role = request.form['role']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Check if start_date or end_date already exists
        if collection.find_one({
            '$or': [
                {'start_date': start_date},
                {'end_date': end_date}
            ]
        }):
            error_message = f"Employee already exists with start_date {start_date} or end_date {end_date}."
        else:
            employee = {'name': name, 'email': email, 'team': team, 'role': role, 'start_date': start_date, 'end_date': end_date}
            collection.insert_one(employee)
            return redirect(url_for('list'))
    return render_template('create.html', error_message=error_message)



# Page to list all employees
@app.route('/list')
def list():
    employees = collection.find()
    return render_template('list.html', employees=employees)


# Page to edit an existing employee
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    employee = collection.find_one({'_id': ObjectId(id)})
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        team = request.form['team']
        role = request.form['role']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Check if start_date or end_date already exists for another employee
        if collection.find_one({
            '$and': [
                {'_id': {'$ne': ObjectId(id)}},
                {
                    '$or': [
                        {'start_date': start_date},
                        {'end_date': end_date}
                    ]
                }
            ]
        }):
            error_message = f"Employee already exists with start_date {start_date} or end_date {end_date}."
            return render_template('edit.html', employee=employee, error_message=error_message)

        collection.update_one({'_id': ObjectId(id)}, {'$set': {'name': name, 'email': email, 'team': team, 'role': role, 'start_date': start_date, 'end_date': end_date}})
        return redirect(url_for('list'))
    else:
        return render_template('edit.html', employee=employee)


# Page to delete an existing employee
@app.route('/delete/<id>')
def delete(id):
    collection.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('list'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
