from datetime import datetime
from pymongo import MongoClient
from PyQt5.QtWidgets import QMessageBox
from global_state import GlobalState
import random
import smtplib
from random import randint

# Database connection (singleton pattern reused)
class Database:
    _client = None

    @staticmethod
    def get_client():
        if Database._client is None:
            cluster_link = "mongodb+srv://krizenix:*krizenix01@krizenixtrading.wq7zj.mongodb.net/"
            Database._client = MongoClient(cluster_link)
        return Database._client

    @staticmethod
    def get_collection(db_name, collection_name):
        client = Database.get_client()
        db = client[db_name]
        return db[collection_name]

def fetch_access_history():
    """
    Fetches username and last_access from the 'account' collection,
    sorted by last_access in ascending order.
    """
    try:
        collection = Database.get_collection("myDB", "account")
        access_history = list(collection.find({},
                                             {"_id": 0, "username": 1, "last_access": 1})
                                .sort("last_access", 1))  # Sort by last_access ascending
        return access_history
    except Exception as e:
        print(f"Error fetching access history: {e}")
        return []

def format_time_difference(last_access):
    """
    Formats the time difference between now and the given last_access datetime.
    """
    now = datetime.now()
    diff = now - last_access

    seconds = diff.seconds
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days
    weeks = days // 7
    years = days // 365

    # Calculate months based on days
    months = days // 30  # Approximate each month as 30 days

    if years > 0:
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif months > 0:
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif weeks > 0:
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif days > 0:
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return f"{seconds} second{'s' if seconds > 1 else ''} ago"

# Login verification
def verify_user_data(parent):
    """
    Verifies if the username and password match any entry in the database.
    Returns:
        - 0 if the user's role is 'HEAD ADMIN'.
        - 1 if the user's role is 'ADMIN'.
        - 2 if the user's role is 'SUPPLY MGMT'.
        - 3 if the user's role is 'BOOKKEEPING'.
        - 4 if the user's role is 'WAITING FOR APPROVAL'.
        - 5 otherwise (e.g., invalid credentials).
    """
    username = parent.username_lineEdit.text().strip()
    password = parent.password_lineEdit.text().strip()

    if not username or not password:
        QMessageBox.warning(parent, "Error","Username and password must not be empty.")
        return 5  # Invalid credentials

    try:
        collection = Database.get_collection("myDB", "account")
        user = collection.find_one({"username": username, "password": password})

        if user:
            role = user.get("role", "").upper()

            # Update last access time
            collection.update_one(
                {"username": username},
                {"$set": {"last_access": datetime.now()}}
            )
            GlobalState.user = username
            GlobalState.role = role  # Set the user's role in GlobalState

            # Map roles to return values
            role_mapping = {
                "HEAD ADMIN": 0,
                "ADMIN": 1,
                "SUPPLY MANAGEMENT": 2,
                "BOOKKEEPING SERVICES": 3,
                "WAITING FOR APPROVAL": 4
            }
            return role_mapping.get(role, 5)  # Default to 5 if role is unrecognized
        else:
            QMessageBox.warning(parent, "Error", "Invalid username or password.")
            return 5  # Invalid credentials
    except Exception as e:
        QMessageBox.warning(parent, "Error", f"An error occurred: {e}.")
        return 5



# Password change verification
def verify_changePass_data(parent):
    """
    Verifies username, email, and code, then updates the password for an existing user.
    Returns:
        0 if the password change is successful, 1 otherwise.
    """
    username = parent.change_username_lineEdit.text().strip()
    new_password = parent.change_password_lineEdit.text().strip()
    confirm_password = parent.change_confirm_password_lineEdit.text().strip()
    email = getattr(parent, "email_used_for_code", None)
    code = getattr(parent, "generated_code", None)

    if not username or not new_password or not confirm_password or not email or not code:
        QMessageBox.warning(parent, "Error", "All fields, including verification, must be completed.")
        return 1

    if new_password != confirm_password:
        QMessageBox.warning(parent, "Error", "Passwords do not match.")
        return 1

    try:
        collection = Database.get_collection("myDB", "account")

        # Verify if user exists with the given email
        user = collection.find_one({"email": email})
        if not user:
            QMessageBox.warning(parent, "Error", "No account found for the provided email.")
            return 1

        # Verify the username matches the email's account
        if user.get("username") != username:
            QMessageBox.warning(parent, "Error", "The username does not match the email's account.")
            return 1

        # Verify the code matches
        input_code = parent.code_changePass_lineEdit.text().strip()
        if str(input_code) != str(code):
            QMessageBox.warning(parent, "Error", "The verification code is incorrect.")
            return 1

        # Confirm password change
        confirm_dialog = QMessageBox(parent)
        confirm_dialog.setWindowTitle("Confirm Password Change")
        confirm_dialog.setStyleSheet("background-color: white;")
        confirm_dialog.setText(
            f"Are you sure you want to change your password?")
        confirm_dialog.setIcon(QMessageBox.Warning)
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_dialog.setDefaultButton(QMessageBox.No)
        response = confirm_dialog.exec_()

        if response != QMessageBox.Yes:
            return 1

        # Update the password
        collection.update_one(
            {"username": username},
            {"$set": {"password": new_password, "last_access": datetime.now()}}
        )
        QMessageBox.information(parent, "Success", "Your password has been successfully changed.")
        return 0
    except Exception as e:
        QMessageBox.warning(parent, "Error", f"An unexpected error occurred: {e}")
        return 1


def check_account_existence():
    """
    Check if there is any account data in the database.
    Returns True if accounts exist, otherwise False.
    """
    try:
        collection = Database.get_collection("myDB", "account")
        account_count = collection.count_documents({})
        return account_count > 0
    except Exception as e:
        print(f"Error checking account existence: {e}")
        return False

def is_email_unique(email):
    """
    Check if an email is unique in the account collection.
    Returns True if unique, otherwise False.
    """
    try:
        collection = Database.get_collection("myDB", "account")
        return collection.count_documents({"email": email}) == 0
    except Exception as e:
        print(f"Error checking email uniqueness: {e}")
        return False

def generate_user_id():
    """
    Generates a sequential user_id starting from 1.
    Increments based on the maximum existing user_id in the database.
    """
    account_collection = Database.get_collection("myDB", "account")

    # Find the maximum user_id in the collection
    max_user = account_collection.find({}, {"user_id": 1}).sort("user_id", -1).limit(1)
    last_user = next(max_user, None)

    if last_user and "user_id" in last_user:
        return last_user["user_id"] + 1  # Increment the highest user_id
    else:
        return 1  # Start at 1 if no accounts exist


def register_user(username, password, confirm_password, email, role):
    """
    Validates and inserts a new user account into the database.
    Checks if the email is a valid Gmail account and prevents duplicate emails.
    """
    if not username or not password or not confirm_password or not email:
        QMessageBox.warning(None, "Error", "All fields must be filled.")
        return 1

    if not username.isalnum():
        QMessageBox.warning(None, "Error", "Username must contain only letters and numbers.")
        return 1

    if password != confirm_password:
        QMessageBox.warning(None, "Error", "Passwords do not match.")
        return 1

    # Check if the email is a Gmail account
    if not email.lower().endswith("@gmail.com"):
        QMessageBox.warning(None, "Error", "Only Gmail accounts are accepted.")
        return 1


    try:
        collection = Database.get_collection("myDB", "account")

        # Confirm registration dialog
        confirm_dialog = QMessageBox()
        confirm_dialog.setWindowTitle("Confirm Register")
        confirm_dialog.setStyleSheet("background-color: white;")
        confirm_dialog.setText(
            f"Are you sure you want to register '{username}' with email '{email}'?"
        )
        confirm_dialog.setIcon(QMessageBox.Warning)
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_dialog.setDefaultButton(QMessageBox.No)
        response = confirm_dialog.exec_()

        if response != QMessageBox.Yes:
            return 1

        # Check if username already exists
        if collection.find_one({"username": username}):
            QMessageBox.warning(None, "Error", "Username already exists.")
            return 1

        # Check if email already exists
        if collection.find_one({"email": email}):
            QMessageBox.warning(None, "Error", "Email already exists.")
            return 1

        # Generate a unique user_id
        user_id = generate_user_id()

        # Insert new account with user_id, email, and role
        collection.insert_one({
            "user_id": user_id,
            "username": username,
            "password": password,
            "email": email,
            "role": role,
            "last_access": datetime.now(),
            "date_registered": datetime.now()  # Add date_registered field
        })

        # Determine message based on role
        if role == "HEAD ADMIN":
            QMessageBox.information(None, "Success", "Registration successful!")
        else:
            QMessageBox.information(None, "Registration Pending", "Registration successful! Please wait for approval.")

        return 0
    except Exception as e:
        QMessageBox.warning(None, "Error", f"An error occurred: {e}")
        return 1


def get_user_role(username):
    """
    Fetches the role of a given username from the database.
    Returns the role as a string or None if the user is not found.
    """
    try:
        account_collection = Database.get_collection("myDB", "account")
        user = account_collection.find_one({"username": username}, {"_id": 0, "role": 1})
        return user.get("role", "").upper() if user else None
    except Exception as e:
        print(f"Error fetching user role: {e}")
        return None


def fetch_accounts_for_user(user_role):
    """
    Fetches account data based on the user's role.
    - HEAD ADMIN: Excludes 'HEAD ADMIN' users.
    - ADMIN: Excludes both 'HEAD ADMIN' and 'ADMIN' users.
    Returns a list of accounts with 'user_id', 'username', 'email', and 'role'.
    """
    try:
        account_collection = Database.get_collection("myDB", "account")

        # Build query based on the role
        query = {}
        if user_role == "HEAD ADMIN":
            query = {"role": {"$ne": "HEAD ADMIN"}}
        elif user_role == "ADMIN":
            query = {"role": {"$nin": ["HEAD ADMIN", "ADMIN"]}}

        # Fetch the account data
        accounts = list(account_collection.find(
            query,
            {"_id": 0, "user_id": 1, "username": 1, "email": 1, "role": 1}
        ))
        return accounts
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return []

def fetch_filtered_accounts(search_term="", role_filter="DEFAULT", current_user_role=""):
    """
    Fetch accounts filtered by username, role, and current user's permissions.
    :param search_term: (str) Text to search for in usernames (case-insensitive).
    :param role_filter: (str) Role to filter by. 'DEFAULT' shows all roles.
    :param current_user_role: (str) The role of the currently logged-in user.
    :return: (list) Filtered accounts with user_id, username, email, and role.
    """
    try:
        collection = Database.get_collection("myDB", "account")
        query = {}

        # Exclude roles based on current_user_role
        if current_user_role == "HEAD ADMIN":
            query["role"] = {"$ne": "HEAD ADMIN"}  # Exclude HEAD ADMIN
        elif current_user_role == "ADMIN":
            query["role"] = {"$nin": ["HEAD ADMIN", "ADMIN"]}  # Exclude HEAD ADMIN and ADMIN

        # Apply role filter (if not DEFAULT)
        if role_filter != "DEFAULT":
            query["role"] = role_filter

        # Apply search term filter
        if search_term:
            query["username"] = {"$regex": search_term, "$options": "i"}  # Case-insensitive search

        # Fetch filtered accounts
        return list(collection.find(query, {"_id": 0, "user_id": 1, "username": 1, "email": 1, "role": 1, "date_registered":1}))
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return []


def get_available_roles(user_role):
    """
    Determine the available roles for the current user.
    :param user_role: (str) Role of the logged-in user.
    :return: (list) Roles the user can view.
    """
    if user_role == "HEAD ADMIN":
        return ["DEFAULT", "ADMIN", "SUPPLY MANAGEMENT", "BOOKKEEPING SERVICES", "WAITING FOR APPROVAL"]
    elif user_role == "ADMIN":
        return ["DEFAULT", "SUPPLY MANAGEMENT", "BOOKKEEPING SERVICES","WAITING FOR APPROVAL"]
    return ["DEFAULT"]

def delete_account(user_id):
    """
    Deletes a user from the database.
    Args:
        user_id (int): The ID of the user to delete.

    Returns:
        bool: True if the deletion is successful, False otherwise.
    """
    try:
        collection = Database.get_collection("myDB", "account")
        result = collection.delete_one({"user_id": int(user_id)})  # Match by user_id
        return result.deleted_count > 0  # Check if any document was deleted
    except Exception as e:
        print(f"Error deleting account: {e}")
        return False

def update_account_role(user_id, new_role):
    """
    Updates the role of a user in the database.
    """
    try:
        collection = Database.get_collection("myDB", "account")
        result = collection.update_one({"user_id": int(user_id)}, {"$set": {"role": new_role}})
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating account role: {e}")
        return False

def get_current_user_role(username):
    """
    Fetches the role of the current logged-in user.
    Args:
        username (str): Username of the logged-in user.

    Returns:
        str: Role of the user (e.g., 'HEAD ADMIN', 'ADMIN'), or None if not found.
    """
    try:
        collection = Database.get_collection("myDB", "account")
        user = collection.find_one({"username": username}, {"_id": 0, "role": 1})
        return user["role"] if user else None
    except Exception as e:
        print(f"Error fetching current user role: {e}")
        return None

def verify_gmail_account(email):
    """
    Verifies if an email exists using SMTP (free method).
    Returns True if the email is valid, False otherwise.
    """
    if not email.lower().endswith("@gmail.com"):
        return False  # Only check Gmail accounts

    try:
        # Connect to Gmail's SMTP server
        smtp_server = "smtp.gmail.com"
        smtp = smtplib.SMTP(smtp_server, 587)
        smtp.ehlo()
        smtp.starttls()

        # Perform a fake login to verify email without sending a message
        smtp.mail("example@gmail.com")  # Use a placeholder sender email
        code, response = smtp.rcpt(email)  # Check the recipient email
        smtp.quit()

        return code == 250  # Code 250 means the email exists
    except smtplib.SMTPRecipientsRefused:
        return False
    except Exception as e:
        print(f"Error verifying email: {e}")
        return False

def send_change_password_code(parent):
    """
    Checks if the provided email exists in the 'account' collection.
    Sends a random 6-digit code to the email if it exists.
    Returns the generated code if successful, otherwise None.
    """
    email = parent.email_changePass_lineEdit.text().strip()

    if not email:
        QMessageBox.warning(parent, "Error", "Email field must not be empty.")
        return None

    try:
        # Check if email exists in the database
        collection = Database.get_collection("myDB", "account")
        account = collection.find_one({"email": email})

        if not account:
            QMessageBox.warning(parent, "Error", "Email does not exist.")
            return None

        # Generate a random 6-digit code
        verification_code = randint(100000, 999999)

        # Send the code and username to the email
        sender_email = "joeljayponcearcipe@gmail.com"
        sender_password = "ygwt gfdu ckqv gtnc"
        receiver_email = email
        username = account.get("username", "User")

        subject = "Password Change Verification Code"
        body = f"""
        Dear {username},

        Your verification code is: {verification_code}

        Please use this code to proceed with changing your password.

        Best regards,
        Krizenix Trading
        """

        message = f"Subject: {subject}\n\n{body}"

        # Set up the SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message)

        QMessageBox.information(parent, "Success", "A verification code has been sent to your email.")
        return verification_code

    except smtplib.SMTPRecipientsRefused as e:
        # This handles the case when Gmail limits the number of emails sent
        QMessageBox.warning(parent, "Error", "Daily email limit exceeded. Please try again later.")
        return None
    except smtplib.SMTPException as e:
        # Handle other SMTP-related exceptions (e.g., authentication errors)
        QMessageBox.warning(parent, "Error", f"Failed to send email: {str(e)}")
        return None
    except Exception as e:
        # Handle any other exceptions
        QMessageBox.warning(parent, "Error", f"An unexpected error occurred: {e}")
        return None

def verify_change_password_code(parent, email, input_code):
    """
    Verifies if the input verification code matches the stored one.
    Args:
        parent: The parent widget (for showing messages).
        email: The email associated with the code.
        input_code: The code entered by the user.
    Returns:
        True if the code matches, False otherwise.
    """
    try:
        # Retrieve the stored code and email
        stored_code = getattr(parent, "generated_code", None)
        stored_email = getattr(parent, "email_used_for_code", None)

        # Validate email and code
        if not stored_code or not stored_email:
            QMessageBox.warning(parent, "Error", "No verification code found. Please try again.")
            return False

        if stored_email != email:
            QMessageBox.warning(parent, "Error", "The email does not match the one used earlier.")
            return False

        if str(stored_code) != str(input_code):
            QMessageBox.warning(parent, "Error", "The verification code is incorrect.")
            return False

        # Verification successful
        return True
    except Exception as e:
        QMessageBox.warning(parent, "Error", f"An unexpected error occurred: {e}")
        return False
