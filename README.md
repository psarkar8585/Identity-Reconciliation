# Identity-Reconciliation


# Overview
This Flask-based web service is designed to handle identity reconciliation by consolidating contact details (email and phone number) into a unified structure. It processes incoming requests to identify whether the provided contact details belong to an existing entity in the database. If no match is found, it creates a new primary contact. If a match is found, it updates or creates secondary contacts to maintain a comprehensive and linked record of identities.

# Features
Primary Contact Management: Creates a primary contact when no matching records exist.
Secondary Contact Linking: Adds secondary contacts for new information linked to an existing entity.
Dynamic Consolidation: Promotes contacts to "primary" or "secondary" based on incoming data.
Comprehensive Response: Returns consolidated data, including all emails, phone numbers, and linked contacts.
Robust Error Handling: Gracefully manages missing input or unexpected database errors.

# Prerequisites
Python: Version 3.12.3 or later.
PostgreSQL: Database server installed and running.
Python Dependencies:
    Flask
    psycopg2


# Database Setup
1. Ensure a PostgreSQL database named EMotorad exists with a table called Contact. 
Use the following schema:

CREATE TABLE Contact (
    id SERIAL PRIMARY KEY,
    phoneNumber VARCHAR(20),
    email VARCHAR(100),
    linkPrecedence VARCHAR(20),
    createdAt TIMESTAMP,
    updatedAt TIMESTAMP,
    linkedId INT,
    FOREIGN KEY (linkedId) REFERENCES Contact(id)
);

2. create a file "app.py" where write whole code 
3. install virtual enviornment (env) , flask and psycopg2

# Configure Database Connection
4. Update the get_db_connection function in app.py with your PostgreSQL credentials:

def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        user='postgres',
        password='root',
        dbname='EMotorad'
    )
# Run the Application:
5. python3 app.py


# database design

 image.png