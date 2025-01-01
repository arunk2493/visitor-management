from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_mail import Message
from app.forms import VisitorForm
from app import mail
import csv
import random
import string

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = VisitorForm()
    token = None  # Initialize token variable

    if form.validate_on_submit():
        if form.entry_exit.data == 'Entry':
            # Generate token and save entry form data
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            save_to_csv(form.data, token, 'active')
            # Retrieve resident email from the flat_email_mapping.csv
            resident_email = get_resident_email(form.flat_no.data)
            
            if resident_email:
                # Send the token to the resident's email
                send_token_email(resident_email, token)
            else:
                flash("No email found for the given flat number.", "error")
        elif form.entry_exit.data == 'Exit':
            # Validate token and mark it as expired
            token = form.token.data
            if validate_and_expire_token(token):
                flash("Token validated and marked as expired.", "success")
            else:
                flash("Invalid or already expired token.", "error")

        return render_template('index.html', form=form, token=token)  # Pass token after form submission

    return render_template('index.html', form=form, token=None)  # No token shown on initial load

def get_resident_email(flat_no):
    """
    Retrieve the resident's email from the flat_email_mapping.csv file based on the flat number.
    """
    with open('flat_email_mapping.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['flat_no'] == flat_no:
                return row['email']
    return None


def send_token_email(resident_email, token):
    """
    Send the generated token to the resident's email address.
    """
    try:
        msg = Message("Visitor Token Generated", recipients=[resident_email])
        msg.body = f"Your visitor token is: {token}\nPlease use this token for exit verification."
        
        # Debugging: print message details to check before sending
        print(f"Sending email to {resident_email} with token: {token}")

        mail.send(msg)  # Send the email
        print("Email sent successfully!")  # Confirm email is sent
    except Exception as e:
        print(f"Error sending email: {e}")  # Print the error if sending fails

# Function to save form data to CSV
def save_to_csv(data, token, status):
    data['token'] = token
    data['status'] = status
    with open('visitor_details.csv', mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        writer.writerow(data)

# Function to validate token and mark as expired
def validate_and_expire_token(token):
    updated_rows = []
    token_found = False
    with open('visitor_details.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['token'] == token and row['status'] == 'active':
                row['status'] = 'expired'
                token_found = True
            updated_rows.append(row)

    if token_found:
        with open('visitor_details.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=updated_rows[0].keys())
            writer.writeheader()
            writer.writerows(updated_rows)
    return token_found