import sys
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from global_state import GlobalState

# Cache for supply data
supply_data_cache = {}

# Database connection (singleton pattern)
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

# Dialog helper
def show_dialog(parent, title, message, icon=QMessageBox.Information):
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(f"\n{message}")
    dialog.setIcon(icon)
    dialog.setStyleSheet("""
        QMessageBox{background-color: white;}
        QLabel{font: bold 20px Segoe UI; color: #1FB89B;}
        QPushButton{padding: 5px 40px; border-color: #1FB89B; background-color: #1FB89B; color: white; font: bold 20px Segoe UI;}
        QPushButton:hover{border-color: #62CDB9; background-color: #62CDB9;}
    """)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()


def fetch_hardware_added_today():
    """
    Fetch hardware entries added today from the `hardware` collection.
    """
    try:
        collection = Database.get_collection("myDB", "hardware")
        start_of_day = datetime.combine(datetime.today(), datetime.min.time())
        end_of_day = datetime.combine(datetime.today(), datetime.max.time())

        query = {
            "hardware_added_at": {
                "$gte": start_of_day,
                "$lte": end_of_day
            }
        }

        hardware_entries = list(collection.find(query, {
            "_id": 0,
            "hardware_name": 1,
            "hardware_location": 1,
            "hardware_contactInfo": 1,
            "hardware_added_at": 1
        }))

        return hardware_entries
    except Exception as e:
        print(f"Error fetching hardware added today: {e}")
        return []


def fetch_items_updated_today():
    """
    Fetch items updated today from the `item` collection.
    """
    try:
        collection = Database.get_collection("myDB", "item")
        start_of_day = datetime.combine(datetime.today(), datetime.min.time())
        end_of_day = datetime.combine(datetime.today(), datetime.max.time())

        query = {
            "item_updated_at": {
                "$gte": start_of_day,
                "$lte": end_of_day
            }
        }

        updated_items = list(collection.find(query, {
            "_id": 0,
            "category": 1,
            "item_name": 1,
            "item_price": 1,
            "hardware_name": 1,
            "item_updated_at": 1
        }))
        return updated_items
    except Exception as e:
        print(f"Error fetching items updated today: {e}")
        return []


def fetch_item_details_for_edit(item_id):
    """
    Fetches the editable details of an item (category, name, price) by its ID.
    :param item_id: The ID of the item to fetch.
    :return: A dictionary containing the item details or None if not found.
    """
    try:
        collection = Database.get_collection("myDB", "item")
        item_details = collection.find_one({"item_id": int(item_id)}, {
            "_id": 0,  # Exclude MongoDB internal ID
            "category": 1,
            "item_name": 1,
            "item_price": 1
        })
        return item_details
    except Exception as e:
        print(f"Error fetching item details for edit: {e}")
        return None

def fetch_items_details_by_ids(item_ids):
    """
    Fetch details for multiple items by their IDs.
    """
    try:
        collection = Database.get_collection("myDB", "item")
        item_details = collection.find(
            {"item_id": {"$in": item_ids}},
            {"_id": 0, "item_price": 1, "hardware_name": 1, "hardware_location": 1, "hardware_contactInfo": 1}
        )
        return list(item_details)
    except Exception as e:
        print(f"Error fetching item details: {e}")
        return []
def fetch_item_details_by_id(item_id):
    """
    Fetches the details of an item from the database by its ID.
    :param item_id: The ID of the item to fetch.
    :return: A dictionary containing the item details or None if not found.
    """
    try:
        collection = Database.get_collection("myDB", "item")
        # Query the database for the item by its ID, including the item_updated_at field
        item_details = collection.find_one({"item_id": int(item_id)}, {
            "_id": 0,  # Exclude the MongoDB internal ID
            "category": 1,
            "item_name": 1,
            "item_price": 1,
            "hardware_name": 1,
            "hardware_location": 1,
            "hardware_contactInfo": 1,
            "item_added_at": 1,
            "item_updated_at": 1  # Include the item_updated_at field
        })
        return item_details
    except Exception as e:
        print(f"Error fetching item details by ID: {e}")
        return None

# Fetch supply data with caching
def fetch_supply_data(search_term="", selected_category="DEFAULT", selected_hardware="DEFAULT", limit=50, skip=0):
    """
    Fetch supply data with filters, pagination, and search capabilities.
    """
    try:
        collection = Database.get_collection("myDB", "item")

        # Build the query
        query = {}
        if search_term.strip():
            query["item_name"] = {"$regex": search_term.strip(), "$options": "i"}  # Case-insensitive match
        if selected_category != "DEFAULT":
            query["category"] = selected_category
        if selected_hardware != "DEFAULT":
            query["hardware_name"] = selected_hardware

        # Use projection to fetch only necessary fields
        projection = {
            "_id": 0,
            "item_id": 1,
            "category": 1,
            "item_name": 1,
            "item_price": 1,
            "hardware_name": 1,
            "hardware_contactInfo": 1
        }

        # Fetch data with limit and skip
        supply_data = list(collection.find(query, projection).skip(skip).limit(limit))
        return supply_data
    except Exception as e:
        print(f"Error fetching supply data: {e}")
        return []

# Fetch distinct hardware names
def fetch_hardware_names():
    try:
        collection = Database.get_collection("myDB", "hardware")
        hardware_names = collection.distinct("hardware_name")
        return sorted(hardware_names)
    except Exception as e:
        print(f"Error fetching hardware names: {e}")
        return []

# Fetch unique items for a specific category
def fetch_items_for_category(category):
    """
    Fetches unique item names for a given category.
    """
    try:
        collection = Database.get_collection("myDB", "item")
        # Use aggregation to fetch distinct item names for the category
        items = collection.distinct("item_name", {"category": category})
        return sorted(items)  # Sort alphabetically for better UX
    except Exception as e:
        print(f"Error fetching items for category '{category}': {e}")
        return []
def fetch_hardware_count():
    try:
        collection = Database.get_collection("myDB", "hardware")
        count = collection.count_documents({})  # Count all documents in the collection
        return count
    except Exception as e:
        print(f"Error fetching hardware count: {e}")
        return 0  # Return 0 in case of an error

def fetch_categories():
    try:
        collection = Database.get_collection("myDB", "item")
        return sorted(collection.distinct("category"))
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

def fetch_items_for_category(category):
    try:
        collection = Database.get_collection("myDB", "item")
        return sorted(collection.distinct("item_name", {"category": category}))
    except Exception as e:
        print(f"Error fetching items for category '{category}': {e}")
        return []

def fetch_average_item_prices_by_hardware(temp_list):
    try:
        collection = Database.get_collection("myDB", "item")

        # Map quantities from temp_list
        qty_map = {item["item_name"]: item["quantity"] for item in temp_list}

        # Fetch items matching temp_list categories and names
        items = list(collection.find({
            "category": {"$in": [item["category"] for item in temp_list]},
            "item_name": {"$in": [item["item_name"] for item in temp_list]}
        }, {
            "_id": 0,
            "item_price": 1,
            "item_name": 1,
            "hardware_name": 1,
            "hardware_location": 1,
            "hardware_contactInfo": 1
        }))

        # Group items by hardware and calculate averages and counts
        hardware_data = {}
        for item in items:
            hardware_name = item["hardware_name"]
            quantity = qty_map.get(item["item_name"], 0)
            total_price = item["item_price"] * quantity

            if hardware_name not in hardware_data:
                hardware_data[hardware_name] = {
                    "total_price": 0,
                    "unique_items": set(),
                    "hardware_location": item["hardware_location"],
                    "hardware_contactInfo": item["hardware_contactInfo"]
                }

            hardware_data[hardware_name]["total_price"] += total_price
            hardware_data[hardware_name]["unique_items"].add(item["item_name"])

        # Compute averages for each hardware
        result = []
        for hardware_name, data in hardware_data.items():
            average_price = (data["total_price"] / len(data["unique_items"])) if data["unique_items"] else 0
            result.append({
                "hardware_name": hardware_name,
                "total_price": data["total_price"],
                "average_price": average_price,
                "unique_item_count": len(data["unique_items"]),
                "hardware_location": data["hardware_location"],
                "hardware_contactInfo": data["hardware_contactInfo"]
            })

        return result

    except Exception as e:
        print(f"Error fetching average item prices by hardware: {e}")
        return []






def fetch_sorted_items(temp_list, selected_category=None, selected_item=None):
    try:
        collection = Database.get_collection("myDB", "item")

        # Base query: Only items in temp_list
        query = {
            "category": {"$in": [item["category"] for item in temp_list]},
            "item_name": {"$in": [item["item_name"] for item in temp_list]},
        }

        # Add filters for category and item name
        if selected_category and selected_category != "ALL":
            query["category"] = selected_category
        if selected_item and selected_item != "ALL":
            query["item_name"] = selected_item

        # Fetch and sort items by price
        items = list(collection.find(query, {
            "_id": 0,
            "item_price": 1,
            "category": 1,
            "item_name": 1,
            "hardware_name": 1,
        }).sort("item_price", 1))

        return items
    except Exception as e:
        print(f"Error fetching sorted items: {e}")
        return []

def fetch_hardware_data(temp_list, selected_hardware):
    """
    Fetch hardware-specific data filtered by temp_list and selected_hardware.
    :param temp_list: Reference list containing categories and item names.
    :param selected_hardware: Filter for hardware name.
    :return: Filtered list of hardware data.
    """
    try:
        collection = Database.get_collection("myDB", "item")

        # Base query: Match category and item_name in temp_list
        query = {
            "category": {"$in": [item["category"] for item in temp_list]},
            "item_name": {"$in": [item["item_name"] for item in temp_list]},
            "hardware_name": selected_hardware,  # Only include items for the selected hardware
        }

        print("Executing query:", query)  # Debug query

        # Fetch data
        hardware_data = list(collection.find(query, {
            "_id": 0,
            "item_price": 1,
            "category": 1,
            "item_name": 1,
            "hardware_name": 1,
            "hardware_contactInfo": 1
        }))

        print("Fetched hardware data:", hardware_data)  # Debug fetched data

        return hardware_data
    except Exception as e:
        print(f"Error fetching hardware data: {e}")
        return []

def fetch_hardware_names_with_averages(temp_list):
    """
    Fetch hardware names along with their average item prices from temp_list.
    Sort the hardware names by the lowest average price.
    """
    try:
        collection = Database.get_collection("myDB", "item")

        # Aggregate query to calculate the average price for each hardware
        pipeline = [
            {
                "$match": {
                    "category": {"$in": [item["category"] for item in temp_list]},
                    "item_name": {"$in": [item["item_name"] for item in temp_list]}
                }
            },
            {
                "$group": {
                    "_id": "$hardware_name",
                    "average_price": {"$avg": "$item_price"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "hardware_name": "$_id",
                    "average_price": 1
                }
            },
            {
                "$sort": {"average_price": 1}  # Sort by average price (ascending)
            }
        ]

        # Execute aggregation pipeline
        hardware_averages = list(collection.aggregate(pipeline))
        print("Hardware averages fetched:", hardware_averages)  # Debug fetched data

        # Return sorted hardware names
        return [data["hardware_name"] for data in hardware_averages]
    except Exception as e:
        print(f"Error fetching hardware names with averages: {e}")
        return []




# Insert new hardware
def insert_hardware_data(parent):
    """
    Inserts new hardware data and associates existing items with the new hardware,
    ensuring no duplicate items are created.
    """
    hardware_name = parent.hardware_name_lineEdit.text().strip().upper()
    hardware_location = parent.hardware_location_lineEdit.text().strip().upper()
    hardware_contact = parent.hardware_contactInfo_lineEdit.text().strip()

    # Input validation
    if not hardware_name:
        QMessageBox.warning(parent, "Error", "Hardware name must not be empty.")
        return 1
    if not hardware_location:
        QMessageBox.warning(parent, "Error", "Hardware location must not be empty.")
        return 1
    if not (hardware_contact.isdigit() and len(hardware_contact) == 11):
        QMessageBox.warning(parent, "Error", "Hardware contact must be an 11-digit number.")
        return 1

    try:
        hardware_col = Database.get_collection("myDB", "hardware")
        item_col = Database.get_collection("myDB", "item")

        # Check for duplicate hardware
        if hardware_col.find_one({"hardware_name": hardware_name}):
            QMessageBox.warning(parent, "Error", f"Hardware '{hardware_name}' already exists.")
            return 1

        # Check for duplicate hardware contact info
        if hardware_col.find_one({"hardware_contactInfo": hardware_contact}):
            QMessageBox.warning(parent, "Error", f"Hardware with contact info '{hardware_contact}' already exists.")
            return 1

        # Insert the new hardware
        hardware_data = {
            "hardware_name": hardware_name,
            "hardware_location": hardware_location,
            "hardware_contactInfo": hardware_contact,
            "hardware_added_at": datetime.now()
        }
        hardware_col.insert_one(hardware_data)

        QMessageBox.information(parent, "Success", f"Hardware '{hardware_name}' added successfully.")
        return 0

    except Exception as e:
        QMessageBox.critical(parent, "Error", f"An error occurred: {e}")
        return 1


def insert_item_data(parent):
    selected_category = parent.choose_insert_categoryBox.currentText().strip().upper()
    item_name = parent.itemName_lineEdit.text().strip().upper()
    item_price = parent.itemPrice_lineEdit.text().strip()
    hardware_name = parent.insert_item_hardwareBox.currentText().strip().upper()

    # Input validation
    if not item_name:
        QMessageBox.warning(parent, "Error", "Item name must not be empty.")
        return 1
    if not hardware_name:
        QMessageBox.warning(parent, "Error", "Please select a hardware.")
        return 1

    try:
        item_price = float(item_price)  # Convert to float to validate
        if item_price <= 0:
            QMessageBox.warning(parent, "Error", "Item price must be greater than 0.")
            return 1
    except ValueError:
        QMessageBox.warning(parent, "Error", "Item price must be numeric.")
        return 1

    try:
        hardware_col = Database.get_collection("myDB", "hardware")
        item_col = Database.get_collection("myDB", "item")

        # Ensure the selected hardware exists
        selected_hardware = hardware_col.find_one({"hardware_name": hardware_name})
        if not selected_hardware:
            QMessageBox.warning(parent, "Error", f"Hardware '{hardware_name}' does not exist in the database.")
            return 1

        # Check for duplicate item name in the selected category and hardware
        existing_item = item_col.find_one({
            "category": selected_category,
            "item_name": item_name
        })
        if existing_item:
            QMessageBox.warning(parent, "Error", f"An item with the name '{item_name}' already exists in category '{selected_category}'.")
            return 1

        # Get the current max item_id
        last_item = item_col.find_one(sort=[("item_id", -1)])
        new_item_id = last_item["item_id"] + 1 if last_item else 1

        # Insert the item with the hardware details and the new quantity field
        item_col.insert_one({
            "item_id": new_item_id,
            "hardware_name": selected_hardware["hardware_name"],
            "hardware_location": selected_hardware["hardware_location"],
            "hardware_contactInfo": selected_hardware["hardware_contactInfo"],
            "category": selected_category,
            "item_name": item_name,
            "item_price": float(item_price),
            "item_added_at": datetime.now()
        })

        QMessageBox.information(parent, "Success", f"Item '{item_name}' added successfully for hardware '{hardware_name}'.")
        return 0

    except Exception as e:
        QMessageBox.critical(parent, "Error", f"An error occurred: {e}")
        return 1



def edit_item_data(parent):
    """
    Edits the price of an item in the database.
    :param parent: The PopupDialog instance.
    :return: 0 on success, 1 on failure.
    """
    print("hm?")
    item_id = GlobalState.id  # Retrieve the item ID from the global state
    print(f"Editing item with ID: {item_id}")  # Should no longer be None
    new_price = parent.edit_item_price_lineEdit.text().strip()
    print('Received new price input.')

    # Validate input: check if it's a valid float
    try:
        new_price = float(new_price)
        if new_price < 0:
            raise ValueError("Price cannot be negative.")
    except ValueError:
        QMessageBox.warning(parent, "Error", "Item price must be a valid positive number.")
        return 1

    try:
        collection = Database.get_collection("myDB", "item")

        # Update the item pricewar
        result = collection.update_one(
            {"item_id": int(item_id)},
            {"$set": {"item_price": new_price, "item_updated_at": datetime.now()}}
        )

        if result.modified_count == 0:
            QMessageBox.warning(parent, "Error", "No changes made. Please check the item and try again.")
            return 1


        QMessageBox.information(parent, "Success", f"Item price successfully updated to {new_price:.2f}.")
        return 0

    except Exception as e:
        QMessageBox.critical(parent, "Error", f"An error occurred while updating the item price: {e}")
        return 1

# Delete hardware and its associated items
def delete_hardware_data(parent):
    selected_hardware = parent.choose_delete_hardwareBox.currentText()

    if not selected_hardware:
        QMessageBox.warning(parent, "Error", "No hardware selected to delete.")
        return 1

    try:
        hardware_col = Database.get_collection("myDB", "hardware")
        item_col = Database.get_collection("myDB", "item")

        # Confirm deletion
        confirm_dialog = QMessageBox(parent)
        confirm_dialog.setWindowTitle("Confirm Deletion")
        confirm_dialog.setText(
            f"Are you sure you want to delete '{selected_hardware}'?")
        confirm_dialog.setIcon(QMessageBox.Warning)
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_dialog.setDefaultButton(QMessageBox.No)
        response = confirm_dialog.exec_()

        if response != QMessageBox.Yes:
            return 1

        # Delete hardware
        if hardware_col.delete_one({"hardware_name": selected_hardware}).deleted_count == 0:
            QMessageBox.warning(parent, "Error", f"Failed to delete hardware '{selected_hardware}'.")
            return 1

        # Delete associated items
        item_col.delete_many({"hardware_name": selected_hardware})
        QMessageBox.information(parent, "Success", f"Hardware '{selected_hardware}' deleted successfully.")
        return 0

    except Exception as e:
        QMessageBox.critical(parent, "Error", f"An error occurred: {e}")
        return 1


# Delete all items matching the selected name
def delete_item_data(parent):
    """
    Deletes all items with the selected name under the chosen category from the database.
    """
    selected_category = parent.choose_delete_categoryBox.currentText().strip()
    selected_item = parent.choose_delete_itemBox.currentText().strip()
    selected_hardware = parent.choose_hardware_delete_hardwareBox.currentText().strip()

    if not selected_category or not selected_item or not selected_hardware:
        QMessageBox.warning(parent, "Error", "Please select a valid category, item, and hardware.")
        return 1

    try:
        collection = Database.get_collection("myDB", "item")

        # Confirm deletion
        confirm_dialog = QMessageBox(parent)
        confirm_dialog.setWindowTitle("Confirm Deletion")
        confirm_dialog.setText(f"Are you sure you want to delete all instances of '{selected_item}' in category '{selected_category}'?")
        confirm_dialog.setIcon(QMessageBox.Warning)
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_dialog.setDefaultButton(QMessageBox.No)
        response = confirm_dialog.exec_()


        if response != QMessageBox.Yes:
            return 1

        # Delete all items matching the selected category and item name
        result = collection.delete_many({
            "category": selected_category,
            "item_name": selected_item,
            "hardware_name": selected_hardware
        })
        if result.deleted_count == 0:
            QMessageBox.warning(parent, "Error", f"No items found to delete for '{selected_item}' in category '{selected_category}'.")
            return 1

        # Clear the cache and refresh the item list in the UI
        supply_data_cache.clear()
        QMessageBox.information(parent, "Success", f"Deleted {result.deleted_count} item(s) for category '{selected_category}', item '{selected_item}', and hardware '{selected_hardware}'.")
        return 0

    except Exception as e:
        QMessageBox.critical(parent, "Error", f"An error occurred: {e}")
        return 1

def insert_existing_item_with_hardware(parent):
    category = parent.hardware_insert_categoryBox.currentText().strip()
    item_name = parent.hardware_insert_itemBox.currentText().strip()
    hardware_name = parent.hardware_insert_hardwareBox.currentText().strip()
    item_price_text = parent.hardware_itemPrice_lineEdit.text().strip()

    # Validate inputs
    if not category or not item_name or not hardware_name:
        QMessageBox.warning(parent, "Error", f"All fields must be filled.")
        return 1

    try:
        item_price = float(item_price_text)
        if item_price <= 0:
            raise ValueError("Price must be greater than zero.")
    except ValueError:
        QMessageBox.warning(parent, "Error", f"Invalid price. Must be a positive number.")
        return 1
    try:
        item_collection = Database.get_collection("myDB", "item")
        hardware_collection = Database.get_collection("myDB", "hardware")

        # Fetch hardware details
        hardware_details = hardware_collection.find_one({"hardware_name": hardware_name}, {"_id": 0})
        if not hardware_details:
            QMessageBox.warning(parent, "Error", f"Hardware '{hardware_name}' not found.")
            return 1

        # Check if the item already exists for this hardware
        existing_entry = item_collection.find_one({
            "category": category,
            "item_name": item_name,
            "hardware_name": hardware_name
        })
        if existing_entry:
            return 1

        # Generate a new item_id
        last_item = item_collection.find_one(sort=[("item_id", -1)])
        new_item_id = last_item["item_id"] + 1 if last_item else 1

        # Insert data
        item_data = {
            "item_id": new_item_id,
            "category": category,
            "item_name": item_name,
            "item_price": item_price,
            "hardware_name": hardware_details["hardware_name"],
            "hardware_location": hardware_details["hardware_location"],
            "hardware_contactInfo": hardware_details["hardware_contactInfo"],
            "item_added_at": datetime.now()
        }
        item_collection.insert_one(item_data)

        QMessageBox.information(parent, "Success", f"Hardware '{hardware_name}' successfully added for item '{item_name}'.")
        return 0
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"An error occurred: {e}")
        return 1

def fetch_unlinked_hardwares(category, item_name):
    try:
        item_collection = Database.get_collection("myDB", "item")
        hardware_collection = Database.get_collection("myDB", "hardware")

        # Find hardware already linked with the selected item
        linked_hardwares = item_collection.distinct("hardware_name", {
            "category": category,
            "item_name": item_name
        })

        # Find all hardware except the linked ones
        unlinked_hardwares = hardware_collection.distinct("hardware_name", {
            "hardware_name": {"$nin": linked_hardwares}
        })

        return sorted(unlinked_hardwares)
    except Exception as e:
        print(f"Error fetching unlinked hardware: {e}")
        return []

def fetch_hardware_for_item(category, item_name):
    try:
        collection = Database.get_collection("myDB", "item")
        hardware_names = collection.distinct("hardware_name", {
            "category": category,
            "item_name": item_name
        })
        return sorted(hardware_names)
    except Exception as e:
        print(f"Error fetching hardware names for item '{item_name}' in category '{category}': {e}")
        return []

def fetch_items_added_today():
    """
    Fetch items added today from the `item` collection.
    """
    try:
        collection = Database.get_collection("myDB", "item")
        start_of_day = datetime.combine(datetime.today(), datetime.min.time())
        end_of_day = datetime.combine(datetime.today(), datetime.max.time())

        query = {
            "item_added_at": {
                "$gte": start_of_day,
                "$lte": end_of_day
            }
        }

        items_added = list(collection.find(query, {
            "_id": 0,
            "category": 1,
            "item_name": 1,
            "item_price": 1,
            "hardware_name": 1,
            "item_added_at": 1
        }))
        return items_added
    except Exception as e:
        print(f"Error fetching items added today: {e}")
        return []

def fetch_cheapest_item(category, item_name):
    """
    Fetch the cheapest item for the given category and item_name.
    """
    try:
        collection = Database.get_collection("myDB", "item")
        query = {
            "category": category,
            "item_name": item_name
        }

        # Sort items by price (ascending) and fetch the cheapest
        cheapest_item = collection.find_one(query, sort=[("item_price", 1)],
                                             projection={
                                                 "_id": 0,
                                                 "category": 1,
                                                 "item_name": 1,
                                                 "item_price":1,
                                                 "hardware_name": 1
                                             })
        return cheapest_item
    except Exception as e:
        print(f"Error fetching cheapest item for {item_name} in {category}: {e}")
        return None

def fetch_sorted_item_history(order="NEWEST"):
    """
    Fetch item history from the `item` collection sorted by `item_added_at`.
    :param order: "NEWEST" for descending, "OLDEST" for ascending.
    :return: List of sorted items.
    """
    try:
        collection = Database.get_collection("myDB", "item")
        sort_order = -1 if order == "NEWEST" else 1
        items = list(collection.find({}, {
            "_id": 0,
            "category": 1,
            "item_name": 1,
            "item_price": 1,
            "hardware_name": 1,
            "item_added_at": 1
        }).sort("item_added_at", sort_order))
        return items
    except Exception as e:
        print(f"Error fetching sorted item history: {e}")
        return []
