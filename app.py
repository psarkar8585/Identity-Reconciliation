from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        user='postgres',
        password='root',
        dbname='EMotorad'
    )

# Route to handle identity reconciliation
@app.route('/identify', methods=['POST'])
def identify():
    data = request.get_json()
    email = data.get('email')
    phone_number = data.get('phoneNumber')

    # Ensure either email or phone number is provided
    if not email and not phone_number:
        return jsonify({"error": "Email or phone number required"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            # Find existing contacts matching either email or phone number
            query = """
                SELECT * FROM Contact
                WHERE email = %s OR phoneNumber = %s
            """
            cursor.execute(query, (email, phone_number))
            matching_contacts = cursor.fetchall()

            if not matching_contacts:
                # Create a new primary contact if no matches found
                insert_query = """
                    INSERT INTO Contact (phoneNumber, email, linkPrecedence, createdAt, updatedAt)
                    VALUES (%s, %s, 'primary', NOW(), NOW())
                    RETURNING id
                """
                cursor.execute(insert_query, (phone_number, email))
                primary_contact_id = cursor.fetchone()[0]
                connection.commit()

                return jsonify({
                    "primaryContactId": primary_contact_id,
                    "emails": [email] if email else [],
                    "phoneNumbers": [phone_number] if phone_number else [],
                    "secondaryContactIds": []
                }), 200

            # Consolidate contacts: separate primary and secondary contacts
            primary_contact = None
            secondary_contacts = []
            emails = set()
            phone_numbers = set()

            for contact in matching_contacts:
                link_precedence = contact.get('linkPrecedence')
                if link_precedence == 'primary':
                    primary_contact = contact
                elif link_precedence == 'secondary':
                    secondary_contacts.append(contact)

                if contact.get('email'):
                    emails.add(contact['email'])
                if contact.get('phoneNumber'):
                    phone_numbers.add(contact['phoneNumber'])

            if not primary_contact:
                # Promote the first matching contact to primary
                primary_contact = matching_contacts[0]
                update_query = """
                    UPDATE Contact
                    SET linkPrecedence = 'primary', updatedAt = NOW()
                    WHERE id = %s
                """
                cursor.execute(update_query, (primary_contact['id'],))
                connection.commit()

            # Add new secondary contact if necessary
            if (email and email not in emails) or (phone_number and phone_number not in phone_numbers):
                insert_query = """
                    INSERT INTO Contact (phoneNumber, email, linkedId, linkPrecedence, createdAt, updatedAt)
                    VALUES (%s, %s, %s, 'secondary', NOW(), NOW())
                    RETURNING id
                """
                cursor.execute(insert_query, (phone_number, email, primary_contact['id']))
                new_secondary_id = cursor.fetchone()[0]
                connection.commit()
                secondary_contacts.append({"id": new_secondary_id})

            # Prepare the response with consolidated contact information
            response = {
                "primaryContactId": primary_contact['id'],
                "emails": list(emails),
                "phoneNumbers": list(phone_numbers),
                "secondaryContactIds": [contact['id'] for contact in secondary_contacts]
            }

            return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
