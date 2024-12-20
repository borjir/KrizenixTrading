from pymongo import MongoClient
from datetime import datetime, timedelta, date
import random
import dateutil.relativedelta as relativedelta

# Database Connection (Singleton)
class Database:
    _client = None

    @staticmethod
    def get_client():
        if Database._client is None:
            connection_url = "mongodb+srv://krizenix:*krizenix01@krizenixtrading.wq7zj.mongodb.net/"
            Database._client = MongoClient(connection_url)
        return Database._client

    @staticmethod
    def get_collection(db_name, collection_name):
        return Database.get_client()[db_name][collection_name]

bookkeeping_data_cache = {}

# Validation Functions
def validate_client_data(data):
    """
    Validates client data for uniqueness and proper format.
    """
    if not data["client_name"] or not data["business_name"] or not data["contact_info"]:
        return False, "All fields must be filled."

    if not data["contact_info"].isdigit() or len(data["contact_info"]) != 11:
        return False, "Contact info must be an 11-digit number."

    if not data["tin_num"].isdigit() or len(data["tin_num"]) != 12:
        return False, "TIN number must be a 12-digit number."

    client_collection = Database.get_collection("myDB", "client")
    if client_collection.find_one({"client_name": data["client_name"]}):
        return False, "Client name already exists."
    if client_collection.find_one({"business_name": data["business_name"]}):
        return False, "Business name already exists."
    if client_collection.find_one({"contact_info": data["contact_info"]}):
        return False, "Contact info already exists."
    if client_collection.find_one({"tin_num": data["tin_num"]}):  # Check for duplicate TIN numbers
        return False, "TIN number already exists."

    return True, ""


def generate_client_id():
    """
    Generates a globally unique client_id.
    The next client_id is one greater than the highest client_id in the database.
    """
    client_collection = Database.get_collection("myDB", "client")

    # Find the maximum client_id in the collection
    max_client = client_collection.find({}, {"client_id": 1}).sort("client_id", -1).limit(1)
    last_client = next(max_client, None)

    if last_client and "client_id" in last_client:
        return last_client["client_id"] + 1  # Increment the highest client_id
    else:
        return 1  # Start at 1 if no clients exist


def get_distinct_client_count():
    """
    Counts the number of distinct clients based on client_id.
    """
    print('tangina mo uy')
    try:
        client_collection = Database.get_collection("myDB", "client")

        # Use aggregate to get the count of distinct clients based on client_id
        count = client_collection.aggregate([
            {"$group": {"_id": "$client_id"}},  # Group by client_id
            {"$count": "count"}  # Count the groups
        ]).next()["count"]
        return count

    except Exception as e:
        print(f"Error counting distinct clients: {e}")
        return 0  # Return 0 in case of error

def fetch_bookkeeping_data(client_name="", payment_type="DEFAULT", payment_status="DEFAULT", limit=None, skip=0):
    """
    Fetch bookkeeping data from the cache or database with filters and pagination.
    """
    global bookkeeping_data_cache

    # Return cached data if available and no filters are applied
    if not client_name and payment_type == "DEFAULT" and payment_status == "DEFAULT" and "all_data" in bookkeeping_data_cache:
        return bookkeeping_data_cache["all_data"]

    try:
        collection = Database.get_collection("myDB", "client")

        # Build the query
        query = {}
        if client_name.strip():
            query["client_name"] = {"$regex": client_name.strip(), "$options": "i"}
        if payment_type != "DEFAULT":
            query["payment_type"] = payment_type
        if payment_status != "DEFAULT":
            query["status"] = payment_status

        # Use projection to fetch only necessary fields
        projection = {
            "_id": 0,
            "client_id": 1,
            "client_name": 1,
            "business_name": 1,
            "contact_info": 1,
            "payment_type": 1,
            "tin_num": 1,
            "payment_date": 1,
            "status": 1,
        }

        # Fetch data with limit and skip
        bookkeeping_data = list(collection.find(query, projection).skip(skip).limit(limit or 0))

        # Cache the result if no filters are applied
        if not client_name and payment_type == "DEFAULT" and payment_status == "DEFAULT":
            bookkeeping_data_cache["all_data"] = bookkeeping_data

        return bookkeeping_data
    except Exception as e:
        print(f"Error fetching bookkeeping data: {e}")
        return []


# Reuse Database connection from the existing code
def update_payment_status():
    """
    Updates the status of client records based on the current date and their payment_date:
    - 'PENDING' or 'TO BE RECEIVED' -> 'DEADLINE TO PAY' if payment_date matches today.
    - 'PENDING', 'TO BE RECEIVED', or 'DEADLINE TO PAY' -> 'OVERDUE' if today exceeds payment_date.
    - 'COMPLETED' -> 'TO BE RECEIVED' and updates payment_date to the next scheduled date.
    - For 'DTI', if 'COMPLETED' and today exceeds payment_date, payment_date is set to +5 years.
    - For Business Permit-related types, if 'COMPLETED' and today exceeds payment_date, payment_date is set to +1 year.
    """
    try:
        client_collection = Database.get_collection("myDB", "client")
        clients = list(client_collection.find({}))  # Fetch all client records
        today = datetime.now().date()

        # Define deadlines for payment types
        def calculate_next_deadline(payment_type, current_date):
            if payment_type == "BIR 0619 E":
                return current_date.replace(day=10) + timedelta(days=30 if current_date.day > 10 else 0)
            elif payment_type == "BIR 2550 M":
                return current_date.replace(day=20) + timedelta(days=30 if current_date.day > 20 else 0)
            elif payment_type in ["BIR 1601 EQ", "BIR 2551 Q", "BIR 2550 Q", "BIR 1701 Q", "BIR 1702 Q"]:
                quarters = {"BIR 1601 EQ": 30, "BIR 2551 Q": 25, "BIR 2550 Q": 25, "BIR 1701 Q": 15, "BIR 1702 Q": 15}
                months = {"BIR 1601 EQ": [4, 7, 10], "BIR 2551 Q": [4, 7, 10], "BIR 2550 Q": [4, 7, 10],
                          "BIR 1701 Q": [5, 8, 11], "BIR 1702 Q": [5, 8, 11]}
                for month in months[payment_type]:
                    deadline = datetime(current_date.year, month, quarters[payment_type])
                    if deadline.date() > current_date:
                        return deadline
                return datetime(current_date.year + 1, months[payment_type][0], quarters[payment_type])
            elif payment_type == "BIR 1701 AIT":
                return datetime(current_date.year, 4, 15) if current_date < datetime(current_date.year, 4, 15).date() else datetime(current_date.year + 1, 4, 15)
            elif payment_type == "BIR 0605":
                return datetime(current_date.year, 1, 31) if current_date < datetime(current_date.year, 1, 31).date() else datetime(current_date.year + 1, 1, 31)
            elif payment_type == "BOOKS OF ACCOUNTS":
                return datetime(current_date.year, 12, 31)
            elif payment_type == "DTI":
                return current_date + timedelta(days=5 * 365)  # Extend by 5 years
            else:
                return None

        for client in clients:
            payment_type = client.get("payment_type")
            current_status = client.get("status")
            payment_date_str = client.get("payment_date")

            # Skip if no payment_date exists
            if not payment_date_str:
                continue

            payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d").date()

            # Update statuses based on payment_date
            if current_status in ["PENDING", "TO BE RECEIVED"] and today == payment_date:
                print(f"Updating {client['_id']} ({payment_type}) to DEADLINE TO PAY")
                client_collection.update_one(
                    {"_id": client["_id"]},
                    {"$set": {"status": "DEADLINE TO PAY"}}
                )
            elif current_status in ["PENDING", "TO BE RECEIVED", "DEADLINE TO PAY"] and today > payment_date:
                print(f"Updating {client['_id']} ({payment_type}) to OVERDUE")
                client_collection.update_one(
                    {"_id": client["_id"]},
                    {"$set": {"status": "OVERDUE"}}
                )
            elif current_status == "COMPLETED" and today > payment_date:
                if payment_type == "DTI":
                    new_date = payment_date + timedelta(days=5 * 365)  # Extend by 5 years
                elif payment_type in [
                    "BUSINESS PERMIT", "BUSINESS TAX", "SANITARY PERMIT",
                    "CCENRO/ENVIRONMENTAL", "FIRE CERTIFICATE", "BARANGAY CLEARANCE"
                ]:
                    new_date = payment_date + timedelta(days=365)  # Extend by 1 year
                elif payment_type.startswith("BIR") or payment_type == "BOOKS OF ACCOUNTS":
                    new_date = calculate_next_deadline(payment_type, today)
                else:
                    continue  # For unsupported types

                print(f"Updating {client['_id']} ({payment_type}) to TO BE RECEIVED and setting new payment_date to {new_date}")
                client_collection.update_one(
                    {"_id": client["_id"]},
                    {"$set": {
                        "status": "TO BE RECEIVED",
                        "payment_date": new_date.strftime("%Y-%m-%d")
                    }}
                )

    except Exception as e:
        print(f"Error updating payment statuses: {e}")





def get_quarter_deadline(date, months, day):
    """
    Helper to calculate deadlines for quarterly payment types.
    Returns the deadline date if the current month is in the given months list.
    """
    if date.month in months:
        return datetime(date.year, date.month, day)
    return None


# Data Insertion
def handle_client_insertion(data, selected_dates):
    """
    Inserts client data into the database with associated payment types.
    Each record will have a default 'status' of 'TO BE RECEIVED' and a timestamp 'client_added_at'.
    """
    global bookkeeping_data_cache
    try:
        client_collection = Database.get_collection("myDB", "client")
        client_id = generate_client_id()
        status = ""
        # Define payment deadlines logic
        def calculate_deadline(payment_type, current_date):
            if payment_type == "BIR 0619 E":
                next_month = (current_date.month % 12) + 1
                year_adjustment = current_date.year + (1 if next_month == 1 else 0)
                return datetime(year_adjustment, next_month, 10)
            elif payment_type == "BIR 2550 M":
                next_month = (current_date.month % 12) + 1
                year_adjustment = current_date.year + (1 if next_month == 1 else 0)
                return datetime(year_adjustment, next_month, 20)
            elif payment_type in ["BIR 1601 EQ", "BIR 2551 Q", "BIR 2550 Q", "BIR 1701 Q", "BIR 1702 Q"]:
                quarters = {"BIR 1601 EQ": 30, "BIR 2551 Q": 25, "BIR 2550 Q": 25, "BIR 1701 Q": 15, "BIR 1702 Q": 15}
                months = {"BIR 1601 EQ": [4, 7, 10], "BIR 2551 Q": [4, 7, 10], "BIR 2550 Q": [4, 7, 10],
                          "BIR 1701 Q": [5, 8, 11], "BIR 1702 Q": [5, 8, 11]}
                for month in months[payment_type]:
                    deadline = datetime(current_date.year, month, quarters[payment_type])
                    if deadline > current_date:
                        return deadline
                return datetime(current_date.year + 1, months[payment_type][0], quarters[payment_type])
            elif payment_type == "BIR 1701 AIT":
                return datetime(current_date.year + (1 if current_date >= datetime(current_date.year, 4, 15) else 0), 4,
                                15)
            elif payment_type == "BIR 0605":
                return datetime(current_date.year + (1 if current_date >= datetime(current_date.year, 1, 31) else 0), 1,
                                31)
            elif payment_type == "BOOKS OF ACCOUNTS":
                return datetime(current_date.year, 12, 31)
            else:
                return None

        # Define payment categories
        payment_categories = []
        if data["bir_checked"]:
            payment_categories.extend([
                "BIR 0605", "BIR 0619 E", "BIR 1601 EQ", "BIR 2551 Q", "BIR 2550 M",
                "BIR 2550 Q", "BIR 1701 Q", "BIR 1702 Q", "BIR 1701 AIT", "BOOKS OF ACCOUNTS"
            ])
        if data["bp_checked"]:
            payment_categories.extend([
                "BUSINESS TAX", "BUSINESS PERMIT", "SANITARY PERMIT", "CCENRO/ENVIRONMENTAL",
                "FIRE CERTIFICATE", "BARANGAY CLEARANCE"
            ])
        if data["dti_checked"]:
            payment_categories.append("DTI")

        # Insert data for each payment type
        today = datetime.now()

        # Validate DTI date before inserting
        month_mapping = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }

        for payment_type, date_components in selected_dates.items():
            if payment_type == "DTI" and payment_type in payment_categories:
                month = month_mapping.get(date_components["month"])
                day = int(date_components["day"])
                year = int(date_components["year"])
                payment_date = datetime(year, month, day)

                if payment_date.date() <= today.date():
                    return False, "The selected DTI date is past the current date. Please choose a future date."

            if payment_type in [
                "BUSINESS PERMIT", "BUSINESS TAX", "SANITARY PERMIT", "CCENRO/ENVIRONMENTAL",
                "FIRE CERTIFICATE", "BARANGAY CLEARANCE"
            ] and payment_type in payment_categories:
                month = month_mapping.get(date_components["month"])
                day = int(date_components["day"])
                year = int(date_components["year"])
                payment_date = datetime(year, month, day)

                if payment_date.date() <= today.date():
                    return False, f"The selected date for {payment_type} must be in the future."

        for payment_type in payment_categories:
            client_record = {
                "client_id": client_id,
                "client_name": data["client_name"],
                "business_name": data["business_name"],
                "contact_info": data["contact_info"],
                "tin_num": data["tin_num"],  # Include the tin_num field
                "payment_type": payment_type,
                "status": "TO BE RECEIVED",
                "client_added_at": today.strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Calculate `payment_date` based on payment type
            if payment_type in selected_dates and payment_type in ["DTI", "BUSINESS PERMIT", "BUSINESS TAX",
                                                                   "SANITARY PERMIT", "CCENRO/ENVIRONMENTAL",
                                                                   "FIRE CERTIFICATE", "BARANGAY CLEARANCE"]:
                month = month_mapping[selected_dates[payment_type]["month"]]
                day = int(selected_dates[payment_type]["day"])
                year = int(selected_dates[payment_type]["year"])
                payment_date = datetime(year, month, day)
                client_record["payment_date"] = payment_date.strftime("%Y-%m-%d")
            else:
                deadline = calculate_deadline(payment_type, today)
                if deadline:
                    client_record["payment_date"] = deadline.strftime("%Y-%m-%d")

            # Insert record into MongoDB
            client_collection.insert_one(client_record)

        # Clear cache after insertion
        bookkeeping_data_cache.clear()
        return True, "Client added successfully."

    except Exception as e:
        return False, f"An error occurred: {e}"



def fetch_client_data_for_action(client_id, payment_type):
    """
    Fetches client data for the given client_id and payment_type.
    """
    try:
        collection = Database.get_collection("myDB", "client")
        query = {"client_id": client_id, "payment_type": payment_type}
        projection = {"_id": 0, "payment_type": 1, "status": 1}
        return collection.find_one(query, projection)
    except Exception as e:
        print(f"Error fetching client data for action: {e}")
        return None

def fetch_client_data_for_action_dashboard(client_name, payment_type):
    """
    Fetches client data for the given client_id and payment_type.
    """
    try:
        collection = Database.get_collection("myDB", "client")
        query = {"client_name": client_name, "payment_type": payment_type}
        projection = {"_id": 0, "payment_type": 1, "status": 1}
        return collection.find_one(query, projection)
    except Exception as e:
        print(f"Error fetching client data for action: {e}")
        return None

def update_client_status(client_id, payment_type, new_status):
    """
    Updates the status of a specific payment type for the given client_id and sets client_updated_at.
    """
    try:
        collection = Database.get_collection("myDB", "client")

        # Update the status and set the current date/time for client_updated_at
        result = collection.update_one(
            {"client_id": client_id, "payment_type": payment_type},
            {"$set": {"status": new_status, "client_updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
        )

        # Clear the cache after updating
        bookkeeping_data_cache.clear()

        # Return True if the update modified a document
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating client status: {e}")
        return False

def update_client_status_dashboard(client_name, payment_type, new_status):
    """
    Updates the status of a specific payment type for the given client_id and sets client_updated_at.
    """
    try:
        collection = Database.get_collection("myDB", "client")

        # Update the status and set the current date/time for client_updated_at
        result = collection.update_one(
            {"client_name": client_name, "payment_type": payment_type},
            {"$set": {"status": new_status, "client_updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
        )

        # Clear the cache after updating
        bookkeeping_data_cache.clear()

        # Return True if the update modified a document
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating client status: {e}")
        return False

def fetch_unique_client_names():
    """
    Fetch unique client names from the 'client' collection.
    """
    try:
        client_collection = Database.get_collection("myDB", "client")
        client_names = client_collection.distinct("client_name")  # Fetch unique client names
        return client_names
    except Exception as e:
        print(f"Error fetching unique client names: {e}")
        return []

def delete_client_by_name(client_name):
    """
    Deletes a client record by its name.
    """
    try:
        client_collection = Database.get_collection("myDB", "client")
        result = client_collection.delete_many({"client_name": client_name})  # Delete all matching records
        return result.deleted_count > 0  # Return True if at least one document was deleted
    except Exception as e:
        print(f"Error deleting client: {e}")
        return False


def fetch_status_counts():
    """
    Fetch counts of all statuses from the database.
    Returns a dictionary with counts for all statuses.
    """
    try:
        client_collection = Database.get_collection("myDB", "client")

        # Aggregate the count of each status
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        results = list(client_collection.aggregate(pipeline))

        # Map results to a dictionary
        counts = {res["_id"]: res["count"] for res in results}

        # Ensure all statuses are represented, even if count is zero
        all_statuses = ["TO BE RECEIVED", "PENDING", "DEADLINE TO PAY", "COMPLETED", "OVERDUE"]
        return {status: counts.get(status, 0) for status in all_statuses}

    except Exception as e:
        print(f"Error fetching status counts: {e}")
        return {status: 0 for status in ["TO BE RECEIVED", "PENDING", "DEADLINE TO PAY", "COMPLETED", "OVERDUE"]}

def fetch_client_data(client_name):
    """
    Fetch all data related to a client name.
    """
    try:
        client_collection = Database.get_collection("myDB", "client")
        return list(client_collection.find({"client_name": client_name}))
    except Exception as e:
        print(f"Error fetching client data: {e}")
        return []

def update_client_data(client_name, updates):
    """
    Update client data for a specific client name.
    """
    try:
        client_collection = Database.get_collection("myDB", "client")
        client_collection.update_many({"client_name": client_name}, {"$set": updates})
        return True
    except Exception as e:
        print(f"Error updating client data: {e}")
        return False



def delete_payment_types(client_name, payment_types):
    """
    Delete specific payment types for a client.
    """
    try:
        collection = Database.get_collection("myDB", "client")
        result = collection.delete_many({"client_name": client_name, "payment_type": {"$in": payment_types}})
        return result.deleted_count > 0  # Check if any documents were deleted
    except Exception as e:
        print(f"Error deleting payment types: {e}")
        return False



def update_or_insert_payment_type(client_name, business_name, contact_info, payment_date, payment_type):
    """
    Updates or inserts data for the given client and payment type.
    If the payment_date matches today's date, the payment_type status is set to 'DEADLINE TO PAY'.
    """
    try:
        collection = Database.get_collection("myDB", "client")
        today = datetime.now().date()

        existing_payment_status = collection.find_one({"client_name": client_name, "payment_type": payment_type})
        current_status = ""
        if existing_payment_status:
            # Extract current status and payment_date from the existing record
            current_status = existing_payment_status.get("status")

        # Convert payment_date to a date object
        payment_date_obj = datetime.strptime(payment_date, "%Y-%m-%d").date()

        if payment_date_obj == today and current_status != "COMPLETED":
            status = "DEADLINE TO PAY"
        elif current_status == "COMPLETED":
            status = "COMPLETED"
        elif payment_date_obj > today and current_status == "TO BE RECEIVED":
            status = "TO BE RECEIVED"
        elif payment_date_obj > today and current_status == "PENDING":
            status = "PENDING"
        elif payment_date_obj < today and current_status == "OVERDUE":
            status = "OVERDUE"
        else:
            status = "TO BE RECEIVED"


        # Check if the payment type data already exists
        existing_payment = collection.find_one({"client_name": client_name, "payment_type": payment_type})

        if existing_payment:
            # Update existing data with the new payment_date and status
            result = collection.update_one(
                {"client_name": client_name, "payment_type": payment_type},
                {"$set": {"payment_date": payment_date, "status": status}}
            )
            return result.modified_count > 0
        else:
            # Fetch client_id and tin_num from the existing client
            client_data = collection.find_one({"client_name": client_name}, {"client_id": 1, "tin_num": 1, "_id": 0})
            if client_data is None:
                print(f"Failed to fetch client data for {payment_type} insertion.")
                return False

            # Extract client_id and tin_num
            client_id = client_data["client_id"]
            tin_num = client_data["tin_num"]

            # Insert new data for the payment type
            new_data = {
                "client_id": client_id,
                "client_name": client_name,
                "business_name": business_name,
                "contact_info": contact_info,
                "tin_num": tin_num,
                "payment_type": payment_type,
                "status": status,  # Use the calculated status
                "payment_date": payment_date,
                "client_added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            collection.insert_one(new_data)
            return True

    except Exception as e:
        print(f"Error updating or inserting data for {payment_type}: {e}")
        return False


# Define deadlines for payment types
complete_deadlines = {
    "BIR 0619 E": lambda date: date.replace(day=10),
    "BIR 1601 EQ": lambda date: get_quarter_deadline(date, [4, 7, 10], 30),
    "BIR 2551 Q": lambda date: get_quarter_deadline(date, [4, 7, 10], 25),
    "BIR 2550 M": lambda date: date.replace(day=20),
    "BIR 2550 Q": lambda date: get_quarter_deadline(date, [4, 7, 10], 25),
    "BIR 1701 Q": lambda date: get_quarter_deadline(date, [5, 8, 11], 15),
    "BIR 1702 Q": lambda date: get_quarter_deadline(date, [5, 8, 11], 15),
    "BIR 1701 AIT": lambda date: datetime(date.year, 4, 15),
    "BIR 0605": lambda date: datetime(date.year, 1, 31),
    "BOOKS OF ACCOUNTS": lambda date: datetime(date.year, 12, 31),
    "BUSINESS PERMIT": lambda date: datetime(date.year, 1, 20),
    "BUSINESS TAX": lambda date: datetime(date.year, 1, 25),
    "SANITARY PERMIT": lambda date: datetime(date.year, 1, 20),
    "CCENRO/ENVIRONMENTAL": lambda date: datetime(date.year, 1, 20),
    "FIRE CERTIFICATE": lambda date: datetime(date.year, 1, 20),
    "BARANGAY CLEARANCE": lambda date: datetime(date.year, 1, 20),
    "DTI": lambda date: None,  # Special case handled separately
}

def get_quarter_deadline(date, months, day):
    """
    Helper function to calculate deadlines for quarterly payments.
    Returns the deadline if the current month is in the given months list.
    """
    if date.month in months:
        return datetime(date.year, date.month, day)
    return None

def calculate_deadline(payment_type, today):
    """
    Calculates the deadline for a given payment type based on the current date.
    Ensures all deadlines exceed today's date.
    """
    if payment_type == "BIR 1601 EQ":
        return get_next_quarter_deadline(today, [4, 7, 10], 30)
    elif payment_type == "BIR 2550 Q":
        return get_next_quarter_deadline(today, [4, 7, 10], 25)
    elif payment_type == "BIR 1701 Q":
        return get_next_quarter_deadline(today, [5, 8, 11], 15)
    elif payment_type == "BIR 1702 Q":
        return get_next_quarter_deadline(today, [5, 8, 11], 15)
    elif payment_type == "BIR 0619 E":
        return get_next_month_deadline(today, 10)  # 10th of the next month
    elif payment_type == "BIR 2551 Q":
        return get_next_quarter_deadline(today, [4, 7, 10], 25)  # 25th of the quarter months
    elif payment_type == "BIR 0605":
        deadline = datetime(today.year, 1, 31)
        return deadline if deadline > today else datetime(today.year + 1, 1, 31)
    elif payment_type == "BOOKS OF ACCOUNTS":
        deadline = datetime(today.year, 12, 31)
        return deadline if deadline > today else datetime(today.year + 1, 12, 31)
    elif payment_type == "BIR 1701 AIT":
        deadline = datetime(today.year, 4, 15)
        return deadline if deadline > today else datetime(today.year + 1, 4, 15)
    elif payment_type == "BIR 2550 M":
        deadline = datetime(today.year, today.month, 20)
        return deadline + relativedelta.relativedelta(months=1) if deadline <= today else deadline
    elif payment_type in ["BUSINESS PERMIT", "SANITARY PERMIT", "CCENRO/ENVIRONMENTAL", "FIRE CERTIFICATE", "BARANGAY CLEARANCE"]:
        deadline = datetime(today.year, 1, 20)
        return deadline if deadline > today else datetime(today.year + 1, 1, 20)
    elif payment_type == "BUSINESS TAX":
        deadline = datetime(today.year, 1, 25)
        return deadline if deadline > today else datetime(today.year + 1, 1, 25)
    elif payment_type == "DTI":
        return today + relativedelta.relativedelta(years=5)  # Extend by 5 years
    else:
        return None  # Default case
def get_next_month_deadline(today, day):
    """
    Calculates the next monthly deadline for the given day.
    Ensures the deadline is greater than today's date.
    """
    # Start with the target day of the current month
    try:
        potential_deadline = today.replace(day=day)
    except ValueError:
        # Handle cases where the current month does not have `day` (e.g., February 30)
        potential_deadline = None

    # If today's date exceeds the potential deadline, move to the next month
    if not potential_deadline or today >= potential_deadline:
        next_month = today + relativedelta.relativedelta(months=1)
        potential_deadline = next_month.replace(day=day)

    return potential_deadline

def get_next_quarter_deadline(today, months, day):
    """
    Calculates the next quarterly deadline that is greater than today.
    - months: List of months where the deadline can fall (e.g., [4, 7, 10]).
    - day: The specific day of the month for the deadline (e.g., 30).
    """
    for month in months:
        deadline = datetime(today.year, month, day)
        if deadline > today:
            return deadline
    # If no deadline is found in the current year, use the first quarter of next year
    return datetime(today.year + 1, months[0], day)


def fetch_filtered_data(payment_type="DEFAULT", payment_status="DEFAULT"):
    """
    Fetches filtered bookkeeping data based on payment type and status.
    Excludes records with 'COMPLETED' status.
    Prioritizes status in the order: OVERDUE, DEADLINE TO PAY, TO BE RECEIVED, PENDING.
    Sorts by the nearest payment_date after filtering.
    """
    try:
        collection = Database.get_collection("myDB", "client")

        # Build the base query
        query = {"status": {"$ne": "COMPLETED"}}  # Exclude 'COMPLETED'
        if payment_type != "DEFAULT":
            query["payment_type"] = payment_type
        if payment_status != "DEFAULT":
            query["status"] = payment_status

        # Fetch data with projection
        projection = {
            "_id": 0,
            "client_id": 1,
            "client_name": 1,
            "business_name": 1,
            "contact_info": 1,
            "payment_type": 1,
            "status": 1,
            "payment_date": 1,
        }
        data = list(collection.find(query, projection))

        # Filter data for payment_date conditions
        today = datetime.now().date()
        filtered_data = []
        for record in data:
            if "payment_date" in record and record["payment_date"]:
                payment_date = datetime.strptime(record["payment_date"], "%Y-%m-%d").date()

                # Apply deadline conditions
                if record["payment_type"] == "DTI":
                    if payment_date <= today + timedelta(days=180):  # 6 months
                        filtered_data.append(record)
                else:
                    if payment_date <= today + timedelta(days=30):  # 30 days
                        filtered_data.append(record)

        # Prioritize by status and nearest payment_date
        status_priority = {"OVERDUE": 0, "DEADLINE TO PAY": 1, "TO BE RECEIVED": 2, "PENDING": 3}
        filtered_data.sort(
            key=lambda x: (
                x.get("payment_date") and datetime.strptime(x["payment_date"], "%Y-%m-%d"),
                status_priority.get(x["status"], float("inf")),
            )
        )
        return filtered_data
    except Exception as e:
        print(f"Error fetching filtered data: {e}")
        return []



def fetch_distinct_clients_added_today():
    """
    Fetch distinct clients added today with specific fields, grouped by client_name.
    """
    try:
        # Get today's date as a string prefix
        today_date = datetime.now().strftime("%Y-%m-%d")

        collection = Database.get_collection("myDB", "client")

        # Use aggregation to group by client_name and ensure distinct data
        pipeline = [
            {"$match": {"client_added_at": {"$regex": f"^{today_date}"}}},
            {"$group": {
                "_id": "$client_name",  # Group by client_name to remove duplicates
                "client_name": {"$first": "$client_name"},
                "business_name": {"$first": "$business_name"},
                "contact_info": {"$first": "$contact_info"},
                "client_added_at": {"$first": "$client_added_at"}
            }}
        ]

        return list(collection.aggregate(pipeline))
    except Exception as e:
        print(f"Error fetching distinct clients added today: {e}")
        return []

def ensure_payment_types_with_deadlines(client_name, payment_types, today):
    """
    Ensure payment types exist for the client with calculated payment deadlines.
    """
    try:
        client_collection = Database.get_collection("myDB", "client")

        # Fetch existing client data to retrieve missing fields
        existing_client = client_collection.find_one({"client_name": client_name})
        if not existing_client:
            print(f"No existing client data found for {client_name}.")
            return

        # Extract the full client data
        client_id = existing_client.get("client_id")
        business_name = existing_client.get("business_name", "")
        contact_info = existing_client.get("contact_info", "")
        tin_num = existing_client.get("tin_num", "")
        client_added_at = existing_client.get("client_added_at", today.strftime("%Y-%m-%d %H:%M:%S"))

        # Get existing payment types for the client
        existing_types = client_collection.find({"client_name": client_name}, {"payment_type": 1})
        existing_types = [doc["payment_type"] for doc in existing_types]

        for payment_type in payment_types:
            if payment_type not in existing_types:
                # Calculate the deadline for the payment type
                payment_date = calculate_deadline(payment_type, today)

                # Prepare the new record with all necessary fields
                record = {
                    "client_id": client_id,
                    "client_name": client_name,
                    "business_name": business_name,
                    "contact_info": contact_info,
                    "tin_num": tin_num,  # Include TIN number
                    "payment_type": payment_type,
                    "status": "TO BE RECEIVED",
                    "payment_date": payment_date.strftime("%Y-%m-%d") if payment_date else None,
                    "client_added_at": client_added_at  # Use the same client_added_at date
                }

                # Insert the record
                client_collection.insert_one(record)

    except Exception as e:
        print(f"Error ensuring payment types with deadlines: {e}")
