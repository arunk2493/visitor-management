import os
import random
import string
import csv
from flask_mail import Message
from app import mail
from filelock import FileLock
from datetime import datetime
import logging

# Define CSV file paths
CSV_FILE_PATH = "visitor_details.csv"
LOCK_FILE_PATH = "visitor_details.csv.lock"
FLAT_EMAIL_MAPPING_PATH = "flat_email_mapping.csv"

def generate_token():
    """Generate a token with the format: TOKEN-YYYYMMDD-XXXXX"""
    date_str = datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    token = f"TOKEN-{date_str}-{random_part}"
    return token

def append_to_csv(visitor_name, resident_name, resident_contact, visitor_contact, 
                  purpose_of_visit, num_guests, date, entry_exit, flat_no, token):
    """Append visitor details and token to a CSV file, and set the status to 'Active'."""
    try:
        lock = FileLock(LOCK_FILE_PATH)

        with lock:
            file_exists = os.path.exists(CSV_FILE_PATH)
            temp_file_path = CSV_FILE_PATH + '.tmp'

            with open(temp_file_path, mode='a', newline='') as temp_file:
                writer = csv.writer(temp_file)

                if not file_exists:
                    writer.writerow(['Visitor Name', 'Resident Name', 'Resident Contact', 
                                     'Visitor Contact', 'Purpose of Visit', 'No. of Guests', 
                                     'Date', 'Entry/Exit', 'Flat No', 'Token', 'Status'])

                writer.writerow([visitor_name, resident_name, resident_contact, 
                                 visitor_contact, purpose_of_visit, num_guests, 
                                 date, entry_exit, flat_no, token, 'Active'])

            os.rename(temp_file_path, CSV_FILE_PATH)

        logging.info(f"Visitor details for {visitor_name} appended to CSV file with status 'Active'.")
    except Exception as e:
        logging.error(f"Error appending visitor details for {visitor_name}: {e}")
        raise InternalServerError("Failed to store visitor details in CSV.")

def send_email(resident_email, token):
    """Send an email to the resident with the generated token."""
    try:
        msg = Message("Visitor Registration Token", recipients=[resident_email])
        msg.body = f"Your visitor registration token is: {token}"
        mail.send(msg)
        logging.info(f"Token sent to {resident_email}.")
    except Exception as e:
        logging.error(f"Error sending email to {resident_email}: {e}")

def get_email_by_flat_id(flat_id):
    """Retrieve resident email from flat_id (from a predefined mapping)."""
    try:
        with open(FLAT_EMAIL_MAPPING_PATH, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if row[0] == flat_id:
                    return row[1]
    except FileNotFoundError:
        logging.error(f"File '{FLAT_EMAIL_MAPPING_PATH}' not found.")
    return None

def validate_token(token):
    """Validate token status."""
    try:
        with open(CSV_FILE_PATH, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if row[9] == token and row[10] == 'Active':
                    return True
    except FileNotFoundError:
        logging.error(f"File '{CSV_FILE_PATH}' not found.")
    return False

def update_token_status(token, new_status):
    """Update the status of a token."""
    try:
        rows = []
        with open(CSV_FILE_PATH, mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)

        for row in rows:
            if row[9] == token:
                row[10] = new_status

        with open(CSV_FILE_PATH, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        logging.info(f"Token {token} marked as {new_status}.")
    except FileNotFoundError:
        logging.error(f"File '{CSV_FILE_PATH}' not found.")
