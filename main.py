from PyQt5.QtWidgets import QProgressDialog, QFileDialog, QApplication, QWidget, QLabel, QFrame, QHBoxLayout, QPushButton, QHBoxLayout, QComboBox, QDialog, QStackedWidget, QMessageBox, QDesktopWidget, QTableWidgetItem
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QColor
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import QTimer,QTime,Qt,QSize
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import re
import sys
import os
import platform
from connection_checker import is_connected  # Import the connection checker
import customize
import login_function
import supply_management_function
import bookkeeping_function

from login_function import check_account_existence

from supply_management_function import fetch_hardware_names
from supply_management_function import fetch_supply_data

from bookkeeping_function import validate_client_data, handle_client_insertion
from bookkeeping_function import fetch_bookkeeping_data
from bookkeeping_function import update_payment_status
from bookkeeping_function import fetch_status_counts
from global_state import GlobalState



class PopupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("dialog.ui", self)  # Load dialog.ui design

        #customize
        self.setWindowTitle("Krizenix Trading")
        customize.create_list_customize(self)
        customize.dashboard_popups(self)

        if GlobalState.num == 0:
            self.stackedWidget.setCurrentIndex(0)
            self.setFixedSize(600, 550)
        if GlobalState.num == 1:
            self.stackedWidget.setCurrentIndex(1)
            self.populate_hardware_names()
            self.setFixedSize(600, 750)
        if GlobalState.num == 2:
            self.stackedWidget.setCurrentIndex(2)
            self.load_hardware_names()
            self.setFixedSize(550, 400)
        if GlobalState.num == 3:
            self.stackedWidget.setCurrentIndex(3)
            self.setFixedSize(550, 550)
        # if GlobalState.num == 4:
        #     self.stackedWidget.setCurrentIndex(4)
        #     self.setFixedSize(850, 400)
        # if GlobaLState.num == 5:
        #     self.stackedWidget.setCurrentIndex(5)
        if GlobalState.num == 6:
            self.stackedWidget.setCurrentIndex(6)
            self.load_categories()
            GlobalState.temp_list = []
            self.setFixedSize(700,700)
        if GlobalState.num == 9:
            self.stackedWidget.setCurrentIndex(9)
            self.setFixedSize(950,550)
            # Fetch today's hardware data
            hardware_data = supply_management_function.fetch_hardware_added_today()

            # Populate the table
            self.hardwares_added_table.setRowCount(len(hardware_data))
            for row_index, hardware in enumerate(hardware_data):
                self.hardwares_added_table.setItem(row_index, 0, QTableWidgetItem(hardware["hardware_name"]))
                self.hardwares_added_table.setItem(row_index, 1, QTableWidgetItem(hardware["hardware_location"]))
                self.hardwares_added_table.setItem(row_index, 2, QTableWidgetItem(hardware["hardware_contactInfo"]))
                self.hardwares_added_table.setItem(row_index, 3, QTableWidgetItem(hardware["hardware_added_at"].strftime("%Y-%m-%d %H:%M:%S")))

            # Adjust column widths
            self.hardwares_added_table.resizeColumnsToContents()

        if GlobalState.num == 10:
            self.stackedWidget.setCurrentIndex(10)
            self.setFixedSize(950, 550)

            # Fetch today's updated items
            updated_items = supply_management_function.fetch_items_updated_today()

            # Populate the table
            self.items_updated_table.setRowCount(len(updated_items))
            for row_index, item in enumerate(updated_items):
                self.items_updated_table.setItem(row_index, 0, QTableWidgetItem(item["category"]))
                self.items_updated_table.setItem(row_index, 1, QTableWidgetItem(item["item_name"]))
                self.items_updated_table.setItem(row_index, 2, QTableWidgetItem(f"{item['item_price']:.2f}"))
                self.items_updated_table.setItem(row_index, 3, QTableWidgetItem(item["hardware_name"]))
                self.items_updated_table.setItem(row_index, 4, QTableWidgetItem(
                    item["item_updated_at"].strftime("%Y-%m-%d %H:%M:%S")))

        if GlobalState.num == 11:
            self.stackedWidget.setCurrentIndex(11)
            self.setFixedSize(780, 800)
        if GlobalState.num == 13:
            self.load_client_names()
            self.stackedWidget.setCurrentIndex(13)
            self.setFixedSize(550, 400)
        if GlobalState.num == 14:
            self.stackedWidget.setCurrentIndex(14)
            self.setFixedSize(780, 800)
            self.load_edit_client_names()

            if self.choose_edit_clientBox.count() > 0:
                first_client_name = self.choose_edit_clientBox.itemText(0)
                self.populate_edit_fields(first_client_name)  # Load data for the first client
        if GlobalState.num == 16:
            self.stackedWidget.setCurrentIndex(16)
            self.setFixedSize(1100,600)
            self.populate_comboboxes()
            self.load_dashboard_data()
            self.update_dashboard_graph()
            self.setup_dashboard_filters()
        if GlobalState.num == 17:
            self.stackedWidget.setCurrentIndex(17)
            self.setFixedSize(950, 550)
            self.clients_added_this_day_table.setRowCount(0)  # Clear existing rows

            # Fetch distinct clients' data added today
            clients_data = bookkeeping_function.fetch_distinct_clients_added_today()

            # Populate the table
            self.clients_added_this_day_table.setRowCount(len(clients_data))
            for row_index, client in enumerate(clients_data):
                self.clients_added_this_day_table.setItem(row_index, 0, QTableWidgetItem(client["client_name"]))
                self.clients_added_this_day_table.setItem(row_index, 1, QTableWidgetItem(client["business_name"]))
                self.clients_added_this_day_table.setItem(row_index, 2, QTableWidgetItem(client["contact_info"]))
                self.clients_added_this_day_table.setItem(row_index, 3, QTableWidgetItem(client["client_added_at"]))
        if GlobalState.num == 19:
            self.stackedWidget.setCurrentIndex(19)
            self.setFixedSize(950, 550)
            self.items_added_this_day_table.setRowCount(0)  # Clear existing rows

            # Fetch today's added items
            items_added_today = supply_management_function.fetch_items_added_today()

            # Populate the table
            self.items_added_this_day_table.setRowCount(len(items_added_today))
            for row_index, item in enumerate(items_added_today):
                self.items_added_this_day_table.setItem(row_index, 0, QTableWidgetItem(item["category"]))
                self.items_added_this_day_table.setItem(row_index, 1, QTableWidgetItem(item["item_name"]))
                self.items_added_this_day_table.setItem(row_index, 2, QTableWidgetItem(f"{item['item_price']:.2f}"))
                self.items_added_this_day_table.setItem(row_index, 3, QTableWidgetItem(item["hardware_name"]))
                self.items_added_this_day_table.setItem(row_index, 4, QTableWidgetItem(
                    item["item_added_at"].strftime("%Y-%m-%d %H:%M:%S")))
        if GlobalState.num == 21:
            self.stackedWidget.setCurrentIndex(21)
            self.setFixedSize(950, 650)

            # Set default sorting order from combo box
            selected_order = self.item_historyBox.currentText()

            # Fetch sorted data
            sorted_items = supply_management_function.fetch_sorted_item_history(selected_order)

            # Populate the table
            self.item_history_table.setRowCount(len(sorted_items))
            for row_index, item in enumerate(sorted_items):
                self.item_history_table.setItem(row_index, 0, QTableWidgetItem(item["category"]))
                self.item_history_table.setItem(row_index, 1, QTableWidgetItem(item["item_name"]))
                self.item_history_table.setItem(row_index, 2, QTableWidgetItem(f"{item['item_price']:.2f}"))
                self.item_history_table.setItem(row_index, 3, QTableWidgetItem(item["hardware_name"]))
                self.item_history_table.setItem(row_index, 4, QTableWidgetItem(
                    item["item_added_at"].strftime("%Y-%m-%d %H:%M:%S")))

            # Connect the combo box to reload data when selection changes
            self.item_historyBox.currentTextChanged.connect(self.reload_item_history_table)

        #-------------------------------------SUPPLY MANAGEMENT BUTTONS---------------------------------
        # Connect buttons
        #-------------HARDWARE--------------#
        self.hardwares_added_backPage_btn.clicked.connect(self.back_to_dashboard)
        self.add_hardware_confirm_btn.clicked.connect(self.add_hardware_confirm)
        self.add_hardware_cancel_btn.clicked.connect(self.add_hardware_cancel)
        self.delete_hardware_confirm_btn.clicked.connect(self.delete_hardware_confirm)
        self.delete_hardware_cancel_btn.clicked.connect(self.delete_hardware_cancel)
        #-------------ITEM--------------------#
        self.item_history_back_btn.clicked.connect(self.back_to_main_page)
        self.items_updated_backPage_btn.clicked.connect(self.back_to_dashboard)
        self.items_added_backPage_btn.clicked.connect(self.back_to_dashboard)
        self.add_item_confirm_btn.clicked.connect(self.add_item_confirm)
        self.add_item_cancel_btn.clicked.connect(self.add_item_cancel)
        self.add_item_hardware_proceed_btn.clicked.connect(self.add_item_hardware_proceed)
        self.add_item_hardware_confirm_btn.clicked.connect(self.add_item_hardware_confirm)
        self.add_item_hardware_cancel_btn.clicked.connect(self.add_item_hardware_cancel)
        self.add_item_hardware_back_btn.clicked.connect(self.add_item_hardware_back)
        self.view_item_details_confirm_btn.clicked.connect(self.view_item_confirm)
        self.edit_item_confirm_btn.clicked.connect(self.edit_item_confirm)
        self.edit_item_cancel_btn.clicked.connect(self.edit_item_cancel)
        self.delete_item_confirm_btn.clicked.connect(self.delete_item_confirm)
        self.delete_item_cancel_btn.clicked.connect(self.delete_item_cancel)
        #----------------------CREATE LIST------------------#
        self.add_list_categoryBox.currentTextChanged.connect(self.refresh_items)
        self.add_list_btn.clicked.connect(self.add_to_list)
        self.add_list_cancel_btn.clicked.connect(self.cancel_list_creation)
        self.check_list_btn.clicked.connect(self.check_list_confirmation)
        self.back_to_create_list_btn.clicked.connect(self.back_to_create_list)
        self.add_list_confirm_btn.clicked.connect(self.average_list_data)
        self.average_data_list_btn.clicked.connect(self.average_list_data_page)
        self.item_data_list_btn.clicked.connect(self.item_list_data_page)
        self.hardware_data_list_btn.clicked.connect(self.hardware_list_data_page)
        self.back_to_main_page_btn.clicked.connect(self.back_to_main_page)
        self.convert_pdf_btn.clicked.connect(self.convert_to_pdf)
        self.set_directory_btn.clicked.connect(self.set_directory)

#------------------------------BOOKKEEPING BUTTONS-------------------------
        self.add_client_confirm_btn.clicked.connect(self.add_client_confirm)
        self.add_client_cancel_btn.clicked.connect(self.add_client_cancel)
        self.add_client_confirm_verify_btn.clicked.connect(self.add_client_confirm_verify)
        self.go_back_add_client_btn.clicked.connect(self.go_back_add_client)
        self.add_client_cancel_verify_btn.clicked.connect(self.add_client_cancel_verify)
        self.edit_client_confirm_btn.clicked.connect(self.edit_client_confirm)
        self.edit_client_cancel_btn.clicked.connect(self.edit_client_cancel)
        self.edit_client_confirm_verify_btn.clicked.connect(self.edit_client_confirm_verify)
        self.edit_client_cancel_verify_btn.clicked.connect(self.edit_client_cancel_verify)
        self.go_back_edit_client_btn.clicked.connect(self.go_back_edit_client)
        self.delete_client_confirm_btn.clicked.connect(self.delete_client_confirm)
        self.delete_client_cancel_btn.clicked.connect(self.delete_client_cancel)
        self.payment_back_to_dashboard_btn.clicked.connect(self.back_to_dashboard)
        self.clients_back_to_dashboard_btn.clicked.connect(self.back_to_dashboard)

        self.load_directory()  # Load saved directory when the program starts

        # Load hardware names into the combobox\
        self.choose_delete_categoryBox.currentTextChanged.connect(self.load_items_for_category)
        # Load create list categories and names\
        # Populate combo boxes
        self.update_category_box()
        self.update_item_box_based_on_category()
        self.load_hardware_names_for_list()

        self.hardware_insert_categoryBox.currentTextChanged.connect(self.load_items_based_on_category)
        self.hardware_insert_itemBox.currentTextChanged.connect(self.load_hardwares_based_on_item)
        self.choose_delete_categoryBox.currentTextChanged.connect(self.load_items_for_category)
        self.choose_delete_itemBox.currentTextChanged.connect(self.load_hardware_for_deletion)


        # Connect signals
        self.list_data_categoryBox.currentTextChanged.connect(self.update_item_box_based_on_category)
        self.list_data_itemBox.currentTextChanged.connect(self.item_list_data_page)
        self.item_data_hardwareBox.currentTextChanged.connect(self.hardware_list_data_page)

        self.initialize_date_comboboxes("bp_choose_month_comboBox", "bp_choose_day_comboBox", "bp_choose_year_comboBox")
        self.initialize_date_comboboxes("bt_choose_month_comboBox", "bt_choose_day_comboBox", "bt_choose_year_comboBox")
        self.initialize_date_comboboxes("sp_choose_month_comboBox", "sp_choose_day_comboBox", "sp_choose_year_comboBox")
        self.initialize_date_comboboxes("ccenro_choose_month_comboBox", "ccenro_choose_day_comboBox",
                                        "ccenro_choose_year_comboBox")
        self.initialize_date_comboboxes("fc_choose_month_comboBox", "fc_choose_day_comboBox", "fc_choose_year_comboBox")
        self.initialize_date_comboboxes("bc_choose_month_comboBox", "bc_choose_day_comboBox", "bc_choose_year_comboBox")
        self.initialize_date_comboboxes("choose_month_comboBox", "choose_day_comboBox", "choose_year_comboBox")

#---------------------------------DASHBOARD--------------------==============================-------------#
    def back_to_dashboard(self):
        self.close()

    def update_dashboard_graph(self):
        """
        Updates the dashboard graph showing the distribution of statuses
        from dashboard_bookkeeping_services_table, scaled for smaller size.
        """
        # Step 1: Count statuses from the table
        status_counts = {
            "TO BE RECEIVED": 0,
            "PENDING": 0,
            "OVERDUE": 0,
            "DEADLINE TO PAY": 0,
        }

        # Iterate over rows in the table to count statuses
        row_count = self.dashboard_bookkeeping_services_table.rowCount()
        for row in range(row_count):
            widget = self.dashboard_bookkeeping_services_table.cellWidget(row, 3)  # Assuming a widget is used
            if widget:
                status = widget.text()
                if status in status_counts:
                    status_counts[status] += 1  # Increment the count

        # Step 3: Convert all counts in the dictionary to integers
        status_counts = {status: int(count) for status, count in status_counts.items()}

        # Step 4: Prepare data for the graph
        statuses = list(status_counts.keys())
        counts = [status_counts[status] for status in statuses]  # Extract counts

        # Step 3: Create a Matplotlib figure with reduced size
        figure = Figure(figsize=(6, 3), facecolor="white")  # Smaller figure
        canvas = FigureCanvas(figure)

        # Clear existing widgets from the graph layout
        while self.add_dashboard_graph_to_layout.count():
            widget = self.add_dashboard_graph_to_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        # Add the new canvas to the layout
        self.add_dashboard_graph_to_layout.addWidget(canvas)

        # Step 4: Plot the graph with smaller components
        ax = figure.add_subplot(111)
        ax.plot(statuses, counts, label="Status Count", marker="o", color="b", markersize=5)

        # Customize the graph for smaller display
        ax.set_title("Monthly Status Distribution", fontsize=6)  # Smaller font for title
        ax.set_xlabel("", fontsize=5)  # Smaller font for x-axis label
        ax.set_ylabel("", fontsize=5)  # Smaller font for y-axis label
        ax.tick_params(axis="both", which="major", labelsize=6)  # Smaller tick labels
        ax.legend(fontsize=6)  # Smaller legend text
        ax.grid(True, linewidth=0.5)  # Thinner grid lines

    #--------------------------SUPPLY MANAGEMENT--------------------------------------------------------------#
    #--------------------------------HARDWARE-----------------------------------#
    def populate_hardware_names(self):
        hardware_names = supply_management_function.fetch_hardware_names()
        self.insert_item_hardwareBox.clear()
        self.insert_item_hardwareBox.addItems(hardware_names)
    def load_hardware_names(self):
        """Load hardware names into the QComboBox."""
        hardware_names = supply_management_function.fetch_hardware_names()
        self.choose_delete_hardwareBox.clear()
        self.choose_delete_hardwareBox.addItems(hardware_names)
    def add_hardware_confirm(self):
        # Implement your confirm logic
        n = supply_management_function.insert_hardware_data(self)
        if n == 0:
            self.hardware_name_lineEdit.clear()
            self.hardware_location_lineEdit.clear()
            self.hardware_contactInfo_lineEdit.clear()

    def add_hardware_cancel(self):
        # Implement your cancel logic here
        print("Cancelled!")
        self.close()  # Close dialog

    def delete_hardware_confirm(self):
        """Delete hardware by calling the function in supply_management_function.py."""
        n = supply_management_function.delete_hardware_data(self)
        if n == 0:
            self.load_hardware_names()  # Refresh combobox after deleting\

    def delete_hardware_cancel(self):
        self.close()
#-------------------------------------ITEM-------------------------------------#
    def reload_item_history_table(self):
        """
        Reload the item history table based on the selected sorting order.
        """
        selected_order = self.item_historyBox.currentText()
        sorted_items = supply_management_function.fetch_sorted_item_history(selected_order)

        self.item_history_table.setRowCount(len(sorted_items))
        for row_index, item in enumerate(sorted_items):
            self.item_history_table.setItem(row_index, 0, QTableWidgetItem(item["category"]))
            self.item_history_table.setItem(row_index, 1, QTableWidgetItem(item["item_name"]))
            self.item_history_table.setItem(row_index, 2, QTableWidgetItem(f"{item['item_price']:.2f}"))
            self.item_history_table.setItem(row_index, 3, QTableWidgetItem(item["hardware_name"]))
            self.item_history_table.setItem(row_index, 4, QTableWidgetItem(
                item["item_added_at"].strftime("%Y-%m-%d %H:%M:%S")))

    def load_hardwares_based_on_item(self):
        selected_category = self.hardware_insert_categoryBox.currentText()
        selected_item = self.hardware_insert_itemBox.currentText()
        if selected_category and selected_item:
            hardwares = supply_management_function.fetch_unlinked_hardwares(selected_category, selected_item)
            self.hardware_insert_hardwareBox.clear()
            if hardwares:
                self.hardware_insert_hardwareBox.addItems(hardwares)
            else:
                self.hardware_insert_hardwareBox.addItem("No hardware available")

    def load_items_based_on_category(self):
        selected_category = self.hardware_insert_categoryBox.currentText()
        if selected_category:
            items = supply_management_function.fetch_items_for_category(selected_category)
            self.hardware_insert_itemBox.clear()
            if items:
                self.hardware_insert_itemBox.addItems(items)
            else:
                self.hardware_insert_itemBox.addItem("No items available")

    def load_categories_for_hardware_insert(self):
        # Fetch categories from the database
        categories = supply_management_function.fetch_categories()

        # Populate the category combo box
        self.hardware_insert_categoryBox.clear()
        if categories:
            self.hardware_insert_categoryBox.addItems(categories)
        else:
            self.hardware_insert_categoryBox.addItem("No categories available")

    def load_items_for_category(self):
        """Load items into the QComboBox based on the selected category."""
        selected_category = self.choose_delete_categoryBox.currentText()
        items = supply_management_function.fetch_items_for_category(selected_category)
        self.choose_delete_itemBox.clear()
        self.choose_delete_itemBox.addItems(items)

    def load_categories_for_deletion(self):  # Renamed method
        """Load categories into the choose_delete_categoryBox."""
        self.choose_delete_categoryBox.clear()

        # Add the fixed placeholder option
        self.choose_delete_categoryBox.addItem("CHOOSE CATEGORY")
        self.choose_delete_categoryBox.setItemData(0, 0, QtCore.Qt.UserRole - 1)  # Disable this entry

        # Fetch categories from the database
        categories = supply_management_function.fetch_categories()
        self.choose_delete_categoryBox.addItems(categories)

    def load_hardware_for_deletion(self):
        selected_category = self.choose_delete_categoryBox.currentText()
        selected_item = self.choose_delete_itemBox.currentText()

        if selected_category and selected_item:
            hardwares = supply_management_function.fetch_hardware_for_item(selected_category, selected_item)
            self.choose_hardware_delete_hardwareBox.clear()
            if hardwares:
                self.choose_hardware_delete_hardwareBox.addItems(hardwares)
            else:
                self.choose_hardware_delete_hardwareBox.addItem("No hardware available")
    def add_item_hardware_proceed(self):
        self.load_categories_for_hardware_insert()
        self.load_items_based_on_category()
        self.load_hardwares_based_on_item()
        QMessageBox.information(self,"Loading","Loading data.....")
        self.stackedWidget.setCurrentIndex(18)

    def add_item_hardware_confirm(self):
        result = supply_management_function.insert_existing_item_with_hardware(self)
        if result == 0:
            self.load_categories_for_hardware_insert()
            self.load_items_based_on_category()
            self.load_hardwares_based_on_item()
            self.hardware_itemPrice_lineEdit.clear()
    def add_item_hardware_cancel(self):
        self.close()
    def add_item_hardware_back(self):
        self.stackedWidget.setCurrentIndex(1)
    def add_item_confirm(self):
        n = supply_management_function.insert_item_data(self)
        if n == 0:
            self.itemName_lineEdit.clear()
            self.itemPrice_lineEdit.clear()

    def add_item_cancel(self):
        self.close()

    def view_item_confirm(self):
        self.close()

    def edit_item_confirm(self):
        n = supply_management_function.edit_item_data(self)
        if n == 0:
            self.close()

    def edit_item_cancel(self):
        self.close()

    def delete_item_confirm(self):
        result = supply_management_function.delete_item_data(self)
        if result == 0:
            self.load_items_for_category()  # Refresh items for the category
            self.load_hardware_for_deletion()  # Refresh hardware options

    def delete_item_cancel(self):
        self.close()

#-------------------------------CREATE LIST--------------------------------#
    def load_categories(self):
        """
        Load categories into the `add_list_categoryBox` combo box directly from the `item` collection.
        """
        self.add_list_categoryBox.clear()

        # Add a fixed placeholder option
        self.add_list_categoryBox.addItem("CHOOSE CATEGORY")
        self.add_list_categoryBox.setItemData(0, 0, QtCore.Qt.UserRole - 1)  # Disable this entry

        # Fetch categories directly from the `item` collection
        categories = supply_management_function.fetch_categories()
        self.add_list_categoryBox.addItems(categories)

        # Connect the signal to refresh items when a category changes
        self.add_list_categoryBox.currentTextChanged.connect(self.refresh_items)

    def add_to_list(self):
        """
        Add the selected item to the temporary list along with its quantity.
        """
        selected_category = self.add_list_categoryBox.currentText()
        selected_item = self.add_list_itemBox.currentText()
        quantity_text = self.add_quantityBox.text().strip()

        # Check if the category is "CHOOSE CATEGORY"
        if selected_category == "CHOOSE CATEGORY":
            QMessageBox.warning(self, "Error", "Please choose a valid category first.")
            return

        # Check if the selected item is valid
        if not selected_item:
            QMessageBox.warning(self, "Error", "Please select a valid item.")
            return

        # Validate quantity input
        if not quantity_text.isdigit():
            QMessageBox.warning(self, "Error", "Please enter a valid integer quantity.")
            return

        quantity = int(quantity_text)

        # Check if the item is already in the temporary list
        for item in GlobalState.temp_list:
            if item["category"] == selected_category and item["item_name"] == selected_item:
                QMessageBox.warning(self, "Error",
                                    f"The item '{selected_item}' is already in the list under category '{selected_category}'.")
                return

        # Add the selected item with quantity to the temporary list
        GlobalState.temp_list.append({
            "category": selected_category,
            "item_name": selected_item,
            "quantity": quantity
        })

        # Display a success message
        QMessageBox.information(self, "Success",
                                f"The item '{selected_item}' with quantity '{quantity}' has been successfully added to the list.")

        # Clear the quantity field
        self.add_quantityBox.clear()

        # Refresh the items in the combo box
        self.refresh_items()

    def update_category_box(self):
        """
        Populate the list_data_categoryBox with unique categories from GlobalState.temp_list.
        """
        categories = sorted(set(item["category"] for item in GlobalState.temp_list))
        self.list_data_categoryBox.clear()

        if categories:
            self.list_data_categoryBox.addItems(categories)  # Add unique categories
            # Automatically select the first category if available
            self.list_data_categoryBox.setCurrentIndex(0)
            # Update items based on the first category
            self.update_item_box_based_on_category()
        else:
            self.list_data_categoryBox.addItem("NO CATEGORIES AVAILABLE")
            self.list_data_itemBox.clear()
            self.list_data_itemBox.addItem("NO ITEMS AVAILABLE")

    def update_item_box_based_on_category(self):
        """
        Update list_data_itemBox based on the selected category in list_data_categoryBox.
        Ensures items are unique and immediately specific.
        """
        selected_category = self.list_data_categoryBox.currentText()

        # Check if there's a valid selection
        if not selected_category or selected_category == "NO CATEGORIES AVAILABLE":
            self.list_data_itemBox.clear()
            self.list_data_itemBox.addItem("NO ITEMS AVAILABLE")
            return

        # Fetch items corresponding to the selected category
        items = [
            item["item_name"] for item in GlobalState.temp_list
            if item["category"] == selected_category
        ]

        # Use a set to ensure uniqueness
        unique_items = sorted(set(items))

        # Clear and populate the item box
        self.list_data_itemBox.clear()
        if unique_items:
            self.list_data_itemBox.addItems(unique_items)  # Add unique items
            # Automatically select the first item if available
            self.list_data_itemBox.setCurrentIndex(0)
        else:
            self.list_data_itemBox.addItem("NO ITEMS AVAILABLE")

    def load_hardware_names_for_list(self):
        """
        Load hardware names into item_data_hardwareBox sorted by lowest average item price.
        Automatically filter by the first hardware.
        """
        hardware_names = supply_management_function.fetch_hardware_names_with_averages(GlobalState.temp_list)
        print("Sorted hardware names by average price:", hardware_names)  # Debug

        self.item_data_hardwareBox.clear()
        self.item_data_hardwareBox.addItems(hardware_names)  # Add sorted hardware names

        if hardware_names:
            self.item_data_hardwareBox.setCurrentIndex(0)  # Automatically select the first hardware
            self.hardware_list_data_page()  # Trigger filtering for the first hardware

    def refresh_items(self):
        """
        Refresh the items in the combo box (`add_list_itemBox`) based on the selected category.
        """
        selected_category = self.add_list_categoryBox.currentText()

        # Ignore the placeholder
        if selected_category == "CHOOSE CATEGORY":
            self.add_list_itemBox.clear()
            return

        # Fetch items for the selected category from the `item` collection
        items = supply_management_function.fetch_items_for_category(selected_category)
        self.add_list_itemBox.clear()

        if items:
            self.add_list_itemBox.addItems(items)
            self.add_list_itemBox.setCurrentIndex(0)  # Ensure the first item is selected
        else:
            self.add_list_itemBox.addItem("NO ITEMS AVAILABLE")  # Fallback message

    def check_list_confirmation(self):
        """
        Populate the `check_list_table` with items from the temporary list, including their quantities.
        """
        self.check_list_table.setRowCount(len(GlobalState.temp_list))

        for row_index, item_data in enumerate(GlobalState.temp_list):
            category = item_data["category"]
            item_name = item_data["item_name"]
            quantity = str(item_data["quantity"])

            self.check_list_table.setItem(row_index, 0, QTableWidgetItem(category))
            self.check_list_table.setItem(row_index, 1, QTableWidgetItem(item_name))
            self.check_list_table.setItem(row_index, 2, QTableWidgetItem(quantity))

        self.stackedWidget.setCurrentIndex(7)  # Navigate to the appropriate screen

    def back_to_create_list(self):
        self.stackedWidget.setCurrentIndex(6)

    def average_list_data_page(self):
        self.list_stackedWidget.setCurrentIndex(0)

    def average_list_data(self):
        if not GlobalState.temp_list:
            QMessageBox.warning(self, "Error", "The list is empty. Please add items before confirming.")
            return

        GlobalState.num = 1
        self.close()

        # Open a new instance of the dialog
        new_dialog = PopupDialog(self.parent())
        new_dialog.setFixedSize(1000, 600)
        new_dialog.list_stackedWidget.setCurrentIndex(0)
        new_dialog.average_data_list_btn.setChecked(True)
        new_dialog.stackedWidget.setCurrentIndex(8)

        # Fetch full and partial matches
        full_matches, partial_matches = supply_management_function.fetch_average_item_prices_by_hardware(
            GlobalState.temp_list)

        # Sort full matches by total price
        full_matches.sort(key=lambda x: x["total_price"])

        # Sort partial matches by number of matched items (desc), then by total price (asc)
        partial_matches.sort(key=lambda x: (-len(x["matched_items"]), x["total_price"]))

        # Combine results
        hardware_averages = full_matches + partial_matches

        total_sum = 0
        new_dialog.average_data_list_table.setRowCount(len(hardware_averages))

        for row_index, data in enumerate(hardware_averages):
            total_price = data["total_price"]
            average_price = data["average_price"]
            hardware_name = data["hardware_name"]
            hardware_location = data["hardware_location"]
            hardware_contactInfo = data["hardware_contactInfo"]

            # Update the table
            new_dialog.average_data_list_table.setItem(row_index, 0, QTableWidgetItem(str(row_index + 1)))
            new_dialog.average_data_list_table.setItem(row_index, 1, QTableWidgetItem(f"{average_price:.2f}"))
            new_dialog.average_data_list_table.setItem(row_index, 2, QTableWidgetItem(f"{total_price:.2f}"))
            new_dialog.average_data_list_table.setItem(row_index, 3, QTableWidgetItem(hardware_name))
            new_dialog.average_data_list_table.setItem(row_index, 4, QTableWidgetItem(hardware_location))
            new_dialog.average_data_list_table.setItem(row_index, 5, QTableWidgetItem(hardware_contactInfo))

            total_sum += total_price

        new_dialog.exec_()

    def item_list_data_page(self):
        """
        Fetch and display ranked item prices based on the selected category and item name.
        Include quantity from GlobalState.temp_list and calculate total price.
        """
        self.list_stackedWidget.setCurrentIndex(1)
        try:
            # Fetch selected category and item
            selected_category = self.list_data_categoryBox.currentText()
            selected_item = self.list_data_itemBox.currentText()

            # Fetch sorted data
            sorted_items = supply_management_function.fetch_sorted_items(
                GlobalState.temp_list,
                selected_category,
                selected_item
            )

            # Add quantity from GlobalState.temp_list to sorted_items
            for item in sorted_items:
                for temp_item in GlobalState.temp_list:
                    if item["category"] == temp_item["category"] and item["item_name"] == temp_item["item_name"]:
                        item["quantity"] = temp_item["quantity"]

            # Populate the table
            self.item_data_list_table.setRowCount(len(sorted_items))
            for row_index, item in enumerate(sorted_items):
                quantity = item.get("quantity", 0)  # Default to 0 if not found
                total_price = item["item_price"] * quantity  # Calculate total price

                self.item_data_list_table.setItem(row_index, 0, QTableWidgetItem(str(row_index + 1)))  # Row index
                self.item_data_list_table.setItem(row_index, 1, QTableWidgetItem(f"{total_price:.2f}"))  # Total price
                self.item_data_list_table.setItem(row_index, 2, QTableWidgetItem(str(quantity)))  # Quantity
                self.item_data_list_table.setItem(row_index, 3, QTableWidgetItem(item["category"]))  # Category
                self.item_data_list_table.setItem(row_index, 4, QTableWidgetItem(item["item_name"]))  # Item name
                self.item_data_list_table.setItem(row_index, 5, QTableWidgetItem(f"{item['item_price']:.2f}"))  # Price
                self.item_data_list_table.setItem(row_index, 6, QTableWidgetItem(item["hardware_name"]))  # Hardware name


            # Set vertical headers to row numbers
            for row_index in range(self.item_data_list_table.rowCount()):
                self.item_data_list_table.setVerticalHeaderItem(row_index, QTableWidgetItem("  " + str(row_index + 1)))

            print("Table populated successfully.")

        except Exception as e:
            # Catch any unexpected errors
            print(f"Error in item_list_data_page: {e}")
            self.dialog.setText(f"Error occurred: {e}")
            self.dialog.setStandardButtons(QMessageBox.Ok)
            self.dialog.show()

    def hardware_list_data_page(self):
        """
        Fetch and display hardware data filtered by the selected hardware in item_data_hardwareBox.
        Sort by the lowest average price for all items in the hardware, calculate total price based on quantity,
        update the total price label, and display the item count in the by_hardware_count label.
        """
        self.list_stackedWidget.setCurrentIndex(2)  # Assuming index 2 is for hardware data
        try:
            # Get selected hardware from QComboBox
            selected_hardware = self.item_data_hardwareBox.currentText()

            # Fetch hardware data
            hardware_data = supply_management_function.fetch_hardware_data(GlobalState.temp_list, selected_hardware)

            # Add quantity information to hardware data from temp_list
            total_price_sum = 0  # Initialize total price sum
            item_count = 0  # Initialize item count
            for data in hardware_data:
                for temp_item in GlobalState.temp_list:
                    if data["category"] == temp_item["category"] and data["item_name"] == temp_item["item_name"]:
                        data["quantity"] = temp_item["quantity"]
                        break  # Avoid redundant checks after finding the match

                item_count += 1  # Count each item

            # Populate the table
            self.hardware_data_list_table.setRowCount(len(hardware_data))
            for row_index, data in enumerate(hardware_data):
                category = data["category"]
                item_name = data["item_name"]
                hardware_name = data["hardware_name"]
                quantity = data.get("quantity", 0)  # Default to 0 if not found
                item_price = data["item_price"]
                total_price = item_price * quantity  # Calculate total price
                total_price_sum += total_price  # Accumulate total price
                contact_info = data["hardware_contactInfo"]

                self.hardware_data_list_table.setItem(row_index, 0, QTableWidgetItem(f"{total_price:.2f}"))
                self.hardware_data_list_table.setItem(row_index, 1, QTableWidgetItem(str(quantity)))
                self.hardware_data_list_table.setItem(row_index, 2, QTableWidgetItem(category))
                self.hardware_data_list_table.setItem(row_index, 3, QTableWidgetItem(item_name))
                self.hardware_data_list_table.setItem(row_index, 4, QTableWidgetItem(f"{item_price:.2f}"))
                self.hardware_data_list_table.setItem(row_index, 5, QTableWidgetItem(hardware_name))

            # Update the labels
            self.by_hardware_total.setText(f"Overall Price: P{total_price_sum:.2f}")
            self.by_hardware_count.setText(f"Item Count: {item_count}")
            self.chosen_hardware_contactInfo.setText(f"Contact Info: {contact_info}")
            self.chosen_hardware_contactInfo.setVisible(False)

            # Set vertical headers to row numbers
            for row_index in range(self.hardware_data_list_table.rowCount()):
                self.hardware_data_list_table.setVerticalHeaderItem(row_index,
                                                                    QTableWidgetItem("  " + str(row_index + 1)))

            print("Hardware data table, total price, and item count updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def cancel_list_creation(self):
        self.close()

    def back_to_main_page(self):
        self.close()

    def set_directory(self):
        """
        Opens a dialog for the user to select a directory and saves it to a config file specific to the device.
        This config file is only used on this device.
        """
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Save PDFs",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if directory:
            self.pdf_save_directory = directory
            print(f"PDFs will be saved to: {self.pdf_save_directory}")

            # Save the directory to a local config file
            config_path = os.path.join(os.path.expanduser("~"), ".yourapp", "config.txt")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)  # Ensure directory exists

            with open(config_path, "w") as config_file:
                config_file.write(self.pdf_save_directory)

            QMessageBox.information(self, "Directory Set", "Directory successfully set!")
        else:
            print("No directory selected.")
            QMessageBox.warning(self, "No Directory Selected", "Please select a valid directory for saving PDFs.")

    def load_directory(self):
        """
        Loads the saved directory from a local config file specific to this device.
        """
        config_path = os.path.join(os.path.expanduser("~"), ".yourapp", "config.txt")

        if os.path.exists(config_path):
            with open(config_path, "r") as config_file:
                self.pdf_save_directory = config_file.read().strip()
            print(f"Loaded saved directory: {self.pdf_save_directory}")
        else:
            self.pdf_save_directory = None
            print("No saved directory found.")

    def get_config_file_path(self):
        """
        Returns the path to the config file, depending on the operating system.
        """
        if platform.system() == "Windows":
            app_data_dir = os.getenv("APPDATA", os.path.expanduser("~"))
            config_path = os.path.join(app_data_dir, "YourAppName", "config.txt")
        else:
            # For Mac/Linux, use a common location in the home directory
            config_path = os.path.join(os.path.expanduser("~"), ".yourapp", "config.txt")

        return config_path

    def generate_unique_filename(self):
        """
        Generate a unique file name using the current date.
        For example, Report1 (19-12-2024).pdf, Report2 (19-12-2024).pdf.
        """
        current_date = datetime.now().strftime("%d-%m-%Y")
        counter = 1

        while True:
            # Construct the file name with the current counter and date
            file_name = f"Report{counter} ({current_date}).pdf"
            file_path = os.path.join(self.pdf_save_directory, file_name)

            # Check if a file with the same name already exists
            if not os.path.exists(file_path):
                return file_name  # Return the first available unique file name

            counter += 1  # Increment the counter if the file already exists

    def convert_to_pdf(self):
        """
        Generate a receipt-style PDF report with titles for each table, consistent width,
        smaller font sizes, and invisible table cells.
        """
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image, Paragraph
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        # Ask for confirmation
        if not hasattr(self, 'pdf_save_directory') or not self.pdf_save_directory:
            QMessageBox.warning(self, "Error", "Please set a directory using the 'Set Directory' button before saving.")
            return

            # Generate a unique file name (e.g., Report1.pdf, Report2.pdf)
        file_name = self.generate_unique_filename()

        # Ask for confirmation with file name
        reply = QMessageBox.question(
            self,
            "Confirm PDF Conversion",
            f"Are you sure you want to generate the PDF named '{file_name}' in '{self.pdf_save_directory}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return  # Exit if the user does not confirm

        file_path = os.path.join(self.pdf_save_directory, file_name)

        try:
            document = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                topMargin=10,
                bottomMargin=10,
                leftMargin=20,
                rightMargin=10
            )
            elements = []

            # Add logo
            logo_path = "images/KSX_LOGO.png"
            try:
                logo = Image(logo_path, width=100, height=100)
                logo.hAlign = "CENTER"
                elements.append(logo)
            except Exception as e:
                print(f"Error loading logo: {e}")

            # Add title
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "Title", fontName="Courier-Bold", fontSize=17, alignment=1, spaceAfter=20
            )
            title = Paragraph("KRIZENIX TRADING", title_style)
            elements.append(title)
            elements.append(Spacer(1, 20))

            # Define a function to add table with a title
            def add_table_with_title(title_text, table_data, col_widths):
                # Add the title
                table_title = Paragraph(title_text, ParagraphStyle(
                    name='TableTitle', fontSize=12, fontName='Courier-Bold', alignment=1, spaceAfter=10
                ))
                elements.append(table_title)
                elements.append(Spacer(1, 5))  # Adjust this value for more/less space
                # Add the table
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0, colors.white),  # Make grid invisible
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 15))  # Add space after the table

            # Add TOTAL COST table
            total_cost_data = self.get_average_data_list_table()
            total_cost_col_widths = [65, 65, 65, 130, 130, 130]  # Adjust as needed
            add_table_with_title("CHEAPEST TOTAL COST BY AVERAGE", total_cost_data, total_cost_col_widths)

            elements.append(Spacer(1, 15))

            # Add CHEAPEST ITEMS table
            cheapest_items_data = self.get_cheapest_items_data()
            cheapest_items_col_widths = [75, 120, 120, 75, 75, 120]  # Adjust as needed
            add_table_with_title("CHEAPEST ITEMS", cheapest_items_data, cheapest_items_col_widths)

            elements.append(Spacer(1, 15))

            # Add CHEAPEST HARDWARE table
            cheapest_hardware_data = self.get_hardware_data_list_table()
            cheapest_hardware_col_widths = [75, 120, 120, 75, 75, 120]  # Adjust as needed
            add_table_with_title("CHOSEN HARDWARE", cheapest_hardware_data, cheapest_hardware_col_widths)

            # Add QLabel-like content beneath the CHEAPEST HARDWARE table
            by_hardware_total_text = self.by_hardware_total.text()  # Fetch QLabel text
            by_hardware_count_text = self.by_hardware_count.text()  # Fetch QLabel text
            hardware_contactInfo = self.chosen_hardware_contactInfo.text()

            label_style = ParagraphStyle(
                name='LabelStyle', fontSize=9, fontName='Courier-Bold', alignment=0, spaceAfter=10  # Left-aligned
            )

            elements.append(Paragraph(by_hardware_total_text, label_style))
            elements.append(Paragraph(by_hardware_count_text, label_style))
            elements.append(Paragraph(hardware_contactInfo, label_style))

            # Build the PDF
            document.build(elements)
            QMessageBox.information(self, "Success", f"PDF saved successfully as {file_name} in {self.pdf_save_directory}")
        except Exception as e:
            print(f"Error generating PDF: {e}")

    def get_average_data_list_table(self):
        """
        Fetch data from average_data_list_table, adding a 'RANK' column dynamically,
        limited to the top 5 rows.
        """
        total_cost_data = []

        # Add the header row
        total_cost_data.append(["RANK", "AVG PRICE", "OVR PRICE", "HARDWARE NAME", "LOCATION", "CONTACT INFO"])

        # Determine the number of rows to fetch (max 5)
        max_rows = min(self.average_data_list_table.rowCount(), 5)

        # Process each row in the average_data_list_table up to max_rows and add the rank
        for row in range(max_rows):
            rank = row + 1  # Generate rank starting from 1
            avg_price = self.average_data_list_table.item(row, 1).text()
            total_price = self.average_data_list_table.item(row, 2).text()
            hardware_name = self.average_data_list_table.item(row, 3).text()
            location = self.average_data_list_table.item(row, 4).text()
            contact_info = self.average_data_list_table.item(row, 5).text()

            # Append the row data with rank
            total_cost_data.append([rank, avg_price, total_price, hardware_name, location, contact_info])

        return total_cost_data

    def get_cheapest_items_data(self):
        """
        Fetch data for cheapest items, including quantity and total price from GlobalState.temp_list.
        """
        cheapest_items_data = []
        cheapest_items_data.append(
            ["TOTAL PRICE", "CATEGORY", "ITEM NAME", "QTY", "ITEM PRICE", "HARDWARE NAME"])

        for item in GlobalState.temp_list:
            category = item["category"]
            item_name = item["item_name"]
            quantity = item["quantity"]

            # Fetch item details
            item_details = supply_management_function.fetch_cheapest_item(category, item_name)
            if item_details:
                item_price = item_details["item_price"]
                total_price = item_price * quantity

                # Append the data to the table
                cheapest_items_data.append([
                    f"{total_price:.2f}",
                    category,
                    item_name,
                    quantity,
                    f"{item_price:.2f}",
                    item_details["hardware_name"]
                ])

        return cheapest_items_data

    def get_hardware_data_list_table(self):
        """
        Fetch data from hardware_data_list_table.
        """
        hardware_data = []
        hardware_data.append(["TOTAL PRICE", "CATEGORY", "ITEM NAME", "QTY", "ITEM PRICE","HARDWARE NAME"])
        for row in range(self.hardware_data_list_table.rowCount()):
            hardware_name = self.hardware_data_list_table.item(row, 5).text()
            total_price = self.hardware_data_list_table.item(row, 0).text()
            quantity = self.hardware_data_list_table.item(row, 1).text()
            category = self.hardware_data_list_table.item(row, 2).text()
            item_name = self.hardware_data_list_table.item(row, 3).text()
            price = self.hardware_data_list_table.item(row, 4).text()
            hardware_data.append([total_price, category, item_name, quantity, price, hardware_name])
        return hardware_data

    #------------------------------------------------BOOKKEEPING--------------------------------------#
    def initialize_date_comboboxes(self, month_combo_name, day_combo_name, year_combo_name):
        """
        Initialize and populate the month, day, and year combo boxes during client insertion.
        """
        # Get references to the month, day, and year combo boxes
        month_combo = getattr(self, month_combo_name)
        day_combo = getattr(self, day_combo_name)
        year_combo = getattr(self, year_combo_name)

        # Populate month combo box
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        month_combo.clear()
        month_combo.addItems(months)

        # Populate year combo box (e.g., next 50 years from the current year)
        current_year = datetime.now().year
        year_combo.clear()
        year_combo.addItems([str(year) for year in range(current_year, current_year + 51)])

        # Get tomorrow's date
        tomorrow = datetime.now() + relativedelta(years=1)
        selected_month = tomorrow.strftime("%B")
        selected_year = tomorrow.year
        selected_day = tomorrow.day

        # Function to update day combo box based on month and year
        def update_days():
            selected_month = month_combo.currentText()
            selected_year = int(year_combo.currentText())

            # Define the number of days in each month
            days_in_month = {
                "January": 31, "February": 28, "March": 31, "April": 30,
                "May": 31, "June": 30, "July": 31, "August": 31,
                "September": 30, "October": 31, "November": 30, "December": 31
            }

            # Adjust for leap year
            if selected_month == "February" and (
                    (selected_year % 4 == 0 and selected_year % 100 != 0) or (selected_year % 400 == 0)):
                days_in_month["February"] = 29

            # Get the current selected day
            current_day = day_combo.currentText()

            # Populate the day combo box
            day_combo.clear()
            day_combo.addItems([str(day) for day in range(1, days_in_month[selected_month] + 1)])

            # Retain the previously selected day if valid, otherwise set to 1
            if current_day.isdigit() and int(current_day) <= days_in_month[selected_month]:
                day_combo.setCurrentText(current_day)
            else:
                day_combo.setCurrentText(str(min(int(current_day) if current_day.isdigit() else selected_day,
                                                 days_in_month[selected_month])))

        # Call `update_days` to initialize the day combo box for the first time
        update_days()

        # Set initial values for month, day, and year to tomorrow's date
        month_combo.setCurrentText(selected_month)
        year_combo.setCurrentText(str(selected_year))
        day_combo.setCurrentText(str(selected_day))

        # Connect signals for month and year combo boxes to update the days dynamically
        month_combo.currentTextChanged.connect(update_days)
        year_combo.currentTextChanged.connect(update_days)

    def load_client_names(self):
        """
        Load unique client names into the `choose_delete_clientBox`.
        """
        client_names = bookkeeping_function.fetch_unique_client_names()
        self.choose_delete_clientBox.clear()
        if client_names:
            self.choose_delete_clientBox.addItems(client_names)  # Populate QComboBox with client names
        else:
            self.choose_delete_clientBox.addItem("No clients available")

    def load_edit_client_names(self):
        """
        Populate the `choose_edit_clientBox` with unique client names from the database.
        """
        client_names = bookkeeping_function.fetch_unique_client_names()  # Fetch unique names
        self.choose_edit_clientBox.clear()  # Clear the combobox first
        if client_names:
            self.choose_edit_clientBox.addItems(client_names)  # Populate with names
            self.choose_edit_clientBox.currentTextChanged.connect(self.populate_edit_fields)  # Reflect selection
        else:
            self.choose_edit_clientBox.addItem("No clients available")

    def populate_edit_fields(self, client_name):
        """
        Populate all fields (LineEdits, CheckBoxes, ComboBoxes) based on the selected client.
        """
        if not client_name or client_name == "No clients available":
            return

        client_data = bookkeeping_function.fetch_client_data(client_name)
        if not client_data:
            QMessageBox.warning(self, "Error", f"No data found for client: {client_name}")
            return

        # Reflect business_name and contact_info
        self.edit_business_name_lineEdit.setText(client_data[0].get("business_name", ""))
        self.edit_client_contactInfo_lineEdit.setText(client_data[0].get("contact_info", ""))
        self.edit_tin_num_lineEdit.setText(client_data[0].get("tin_num", ""))

        # Check and set BIR checkbox based on payment_type
        payment_types = [data["payment_type"] for data in client_data]
        if any(pt in [
            "BIR 0605", "BIR 0619 E", "BIR 1601 EQ", "BIR 2551 Q", "BIR 2550 M",
            "BIR 2550 Q", "BIR 1701 Q", "BIR 1702 Q", "BIR 1701 AIT", "BOOKS OF ACCOUNTS"
        ] for pt in payment_types):
            self.edit_bir_checkBox.setChecked(True)
        else:
            self.edit_bir_checkBox.setChecked(False)  # Set False only if no matching BIR types

        # Reset other checkboxes
        self.edit_bp_checkBox.setChecked(False)
        self.edit_dti_checkBox.setChecked(False)

        # Get tomorrow's date
        tomorrow = datetime.now() + relativedelta(years=1)

        # Function to calculate the number of days in the selected month and year
        def calculate_days_in_month(month, year):
            if month in {"January", "March", "May", "July", "August", "October", "December"}:
                return 31
            elif month in {"April", "June", "September", "November"}:
                return 30
            elif month == "February":
                # Leap year check
                if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                    return 29
                return 28
            return 30

        # Function to update days dynamically
        def update_days(month_combo, day_combo, year_combo):
            month_box = getattr(self, month_combo)
            day_box = getattr(self, day_combo)
            year_box = getattr(self, year_combo)

            selected_month = month_box.currentText()
            selected_year = int(year_box.currentText()) if year_box.currentText().isdigit() else datetime.now().year

            days_in_month = calculate_days_in_month(selected_month, selected_year)
            current_day = day_box.currentText()

            # Update days in the combo box
            day_box.clear()
            day_box.addItems([str(day) for day in range(1, days_in_month + 1)])

            # Set to the current day if valid, otherwise reset to 1
            if current_day.isdigit() and int(current_day) <= days_in_month:
                day_box.setCurrentText(current_day)
            else:
                day_box.setCurrentText("1")

        # Function to initialize and populate month, day, and year combo boxes
        def populate_date_combo_boxes(month_combo, day_combo, year_combo, date_value):
            """
            Populate the month, day, and year combo boxes and set their initial values.
            """
            months = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]

            month_box = getattr(self, month_combo)
            day_box = getattr(self, day_combo)
            year_box = getattr(self, year_combo)

            # Populate month and year boxes
            month_box.clear()
            month_box.addItems(months)
            year_box.clear()
            year_box.addItems([str(year) for year in range(datetime.now().year, datetime.now().year + 51)])

            # Set initial values
            selected_month = date_value.strftime("%B")
            selected_year = date_value.year
            selected_day = date_value.day

            month_box.setCurrentText(selected_month)
            year_box.setCurrentText(str(selected_year))
            update_days(month_combo, day_combo, year_combo)  # Initialize days
            day_box.setCurrentText(str(selected_day))

            # Connect signals to dynamically update days
            month_box.currentTextChanged.connect(lambda: update_days(month_combo, day_combo, year_combo))
            year_box.currentTextChanged.connect(lambda: update_days(month_combo, day_combo, year_combo))

        # Populate and dynamically manage BUSINESS PERMIT-related fields
        bp_types = {
            "BUSINESS PERMIT": (
            "bp_choose_month_comboBox_edit", "bp_choose_day_comboBox_edit", "bp_choose_year_comboBox_edit"),
            "BUSINESS TAX": (
            "bt_choose_month_comboBox_edit", "bt_choose_day_comboBox_edit", "bt_choose_year_comboBox_edit"),
            "SANITARY PERMIT": (
            "sp_choose_month_comboBox_edit", "sp_choose_day_comboBox_edit", "sp_choose_year_comboBox_edit"),
            "CCENRO/ENVIRONMENTAL": (
            "ccenro_choose_month_comboBox_edit", "ccenro_choose_day_comboBox_edit", "ccenro_choose_year_comboBox_edit"),
            "FIRE CERTIFICATE": (
            "fc_choose_month_comboBox_edit", "fc_choose_day_comboBox_edit", "fc_choose_year_comboBox_edit"),
            "BARANGAY CLEARANCE": (
            "bc_choose_month_comboBox_edit", "bc_choose_day_comboBox_edit", "bc_choose_year_comboBox_edit"),
        }

        for payment_type, (month_combo, day_combo, year_combo) in bp_types.items():
            matching_data = next((data for data in client_data if data["payment_type"] == payment_type), None)
            payment_date = datetime.strptime(matching_data["payment_date"], "%Y-%m-%d") if matching_data else tomorrow
            if matching_data:
                self.edit_bp_checkBox.setChecked(True)
            populate_date_combo_boxes(month_combo, day_combo, year_combo, payment_date)

        # Populate DTI fields
        dti_data = next((data for data in client_data if data["payment_type"] == "DTI"), None)
        payment_date = datetime.strptime(dti_data["payment_date"], "%Y-%m-%d") if dti_data else tomorrow
        if dti_data:
            self.edit_dti_checkBox.setChecked(True)
        populate_date_combo_boxes("edit_choose_month_comboBox", "edit_choose_day_comboBox", "edit_choose_year_comboBox",
                                  payment_date)

    def save_client_changes(self):
        """
        Save updated client details to the database and handle checkbox logic.
        """
        client_name = self.choose_edit_clientBox.currentText()
        business_name = self.edit_business_name_lineEdit.text().strip()
        contact_info = self.edit_client_contactInfo_lineEdit.text().strip()
        tin_num = self.edit_tin_num_lineEdit.text().strip()

        if not (self.edit_bir_checkBox.isChecked() or
                self.edit_bp_checkBox.isChecked() or
                self.edit_dti_checkBox.isChecked()):
            QMessageBox.critical(self, "Error", "Please select at least one checkbox to edit data.")
            return

        if not business_name or not contact_info.isdigit() or len(contact_info) != 11:
            QMessageBox.critical(self, "Error", "Invalid business name or contact info.")
            return

        # Update client details
        updates = {"business_name": business_name, "contact_info": contact_info}
        if not bookkeeping_function.update_client_data(client_name, updates):
            QMessageBox.critical(self, "Error", "Failed to update client data.")
            return

        today = datetime.now()

        # Handle BIR types
        bir_types = [
            "BIR 0605", "BIR 0619 E", "BIR 1601 EQ", "BIR 2551 Q", "BIR 2550 M",
            "BIR 2550 Q", "BIR 1701 Q", "BIR 1702 Q", "BIR 1701 AIT", "BOOKS OF ACCOUNTS"
        ]
        if self.edit_bir_checkBox.isChecked():
            bookkeeping_function.ensure_payment_types_with_deadlines(client_name, bir_types, today)
            print("dasa")
        else:
            bookkeeping_function.delete_payment_types(client_name, bir_types)

        # Handle Business Permit-related types
        bp_types = {
            "BUSINESS PERMIT": (
            "bp_choose_month_comboBox_edit", "bp_choose_day_comboBox_edit", "bp_choose_year_comboBox_edit"),
            "BUSINESS TAX": (
            "bt_choose_month_comboBox_edit", "bt_choose_day_comboBox_edit", "bt_choose_year_comboBox_edit"),
            "SANITARY PERMIT": (
            "sp_choose_month_comboBox_edit", "sp_choose_day_comboBox_edit", "sp_choose_year_comboBox_edit"),
            "CCENRO/ENVIRONMENTAL": (
            "ccenro_choose_month_comboBox_edit", "ccenro_choose_day_comboBox_edit", "ccenro_choose_year_comboBox_edit"),
            "FIRE CERTIFICATE": (
            "fc_choose_month_comboBox_edit", "fc_choose_day_comboBox_edit", "fc_choose_year_comboBox_edit"),
            "BARANGAY CLEARANCE": (
            "bc_choose_month_comboBox_edit", "bc_choose_day_comboBox_edit", "bc_choose_year_comboBox_edit"),
        }
        print("wada")
        if self.edit_bp_checkBox.isChecked():
            for payment_type, (month_box, day_box, year_box) in bp_types.items():
                try:
                    # Debugging: Ensure ComboBoxes are found
                    month_combo = self.findChild(QComboBox, month_box)
                    day_combo = self.findChild(QComboBox, day_box)
                    year_combo = self.findChild(QComboBox, year_box)

                    if not month_combo or not day_combo or not year_combo:
                        raise ValueError(f"ComboBox not found for {payment_type}: "
                                         f"{month_box}, {day_box}, {year_box}")

                    # Access values
                    month = month_combo.currentText()
                    print(f"Month for {payment_type}: {month}")  # Debug
                    day = int(day_combo.currentText())
                    print(f"Day for {payment_type}: {day}")  # Debug
                    year = int(year_combo.currentText())
                    print(f"Year for {payment_type}: {year}")  # Debug

                    # Map month name to index
                    month_index = {month_name: index for index, month_name in enumerate(calendar.month_name) if
                                   month_name}.get(month)

                    if not month_index:
                        QMessageBox.critical(self, "Error", f"Invalid month selection for {payment_type}.")
                        return

                    # Construct payment_date
                    payment_date = datetime(year, month_index, day)

                    # Ensure date is in the future
                    if payment_date.date() < today.date():
                        QMessageBox.critical(self, "Error",
                                             f"The selected date for {payment_type} must be in the future.")
                        return

                    # Update or insert payment type
                    bookkeeping_function.update_or_insert_payment_type(
                        client_name,
                        business_name.upper(),
                        contact_info,
                        payment_date.strftime("%Y-%m-%d"),
                        payment_type
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"An error occurred while processing {payment_type}: {e}")
        else:
            bookkeeping_function.delete_payment_types(client_name, list(bp_types.keys()))

        # Handle DTI type
        if self.edit_dti_checkBox.isChecked():
            month = self.edit_choose_month_comboBox.currentText()
            day = int(self.edit_choose_day_comboBox.currentText())
            year = int(self.edit_choose_year_comboBox.currentText())

            month_mapping = {
                "January": 1, "February": 2, "March": 3, "April": 4,
                "May": 5, "June": 6, "July": 7, "August": 8,
                "September": 9, "October": 10, "November": 11, "December": 12
            }
            month_int = month_mapping.get(month)

            payment_date = datetime(year, month_int, day)
            if payment_date.date() < today.date():
                QMessageBox.critical(self, "Error", "The selected DTI payment date must be in the future.")
                return

            if not bookkeeping_function.update_or_insert_payment_type(
                    client_name,
                    business_name.upper(),
                    contact_info,
                    payment_date.strftime("%Y-%m-%d"),
                    "DTI"
            ):
                self.close()
        else:
            bookkeeping_function.delete_payment_types(client_name, ["DTI"])

        QMessageBox.information(self, "Success", "Client data updated successfully.")
        self.close()

    def process_client_data(self):
        """
        Collects input data, validates it, and passes it for database insertion.
        """
        # Collect form data
        client_data = {
            "client_name": self.client_name_lineEdit.text().strip().upper(),
            "business_name": self.business_name_lineEdit.text().strip().upper(),
            "contact_info": self.client_contactInfo_lineEdit.text().strip(),
            "tin_num": self.tin_num_lineEdit.text().strip(),  # Collect the TIN number
            "bir_checked": self.insert_bir_checkBox.isChecked(),
            "bp_checked": self.insert_bp_checkBox.isChecked(),
            "dti_checked": self.insert_dti_checkBox.isChecked(),
        }

        # Validate the data
        is_valid, validation_message = validate_client_data(client_data)

        if not is_valid:
            QMessageBox.warning(self, "Validation Error", validation_message)
            return

        # Handle the selected dates for payment types
        selected_dates = {
            "DTI": {
                "month": self.choose_month_comboBox.currentText(),
                "day": self.choose_day_comboBox.currentText(),
                "year": self.choose_year_comboBox.currentText()
            },
            "BUSINESS PERMIT": {
                "month": self.bp_choose_month_comboBox.currentText(),
                "day": self.bp_choose_day_comboBox.currentText(),
                "year": self.bp_choose_year_comboBox.currentText()
            },
            "BUSINESS TAX": {
                "month": self.bt_choose_month_comboBox.currentText(),
                "day": self.bt_choose_day_comboBox.currentText(),
                "year": self.bt_choose_year_comboBox.currentText()
            },
            "SANITARY PERMIT": {
                "month": self.sp_choose_month_comboBox.currentText(),
                "day": self.sp_choose_day_comboBox.currentText(),
                "year": self.sp_choose_year_comboBox.currentText()
            },
            "CCENRO/ENVIRONMENTAL": {
                "month": self.ccenro_choose_month_comboBox.currentText(),
                "day": self.ccenro_choose_day_comboBox.currentText(),
                "year": self.ccenro_choose_year_comboBox.currentText()
            },
            "FIRE CERTIFICATE": {
                "month": self.fc_choose_month_comboBox.currentText(),
                "day": self.fc_choose_day_comboBox.currentText(),
                "year": self.fc_choose_year_comboBox.currentText()
            },
            "BARANGAY CLEARANCE": {
                "month": self.bc_choose_month_comboBox.currentText(),
                "day": self.bc_choose_day_comboBox.currentText(),
                "year": self.bc_choose_year_comboBox.currentText()
            }
        }

        # Insert the data
        success, insert_message = handle_client_insertion(client_data, selected_dates)

        if success:
            # Clear form inputs
            self.client_name_lineEdit.clear()
            self.business_name_lineEdit.clear()
            self.client_contactInfo_lineEdit.clear()
            self.tin_num_lineEdit.clear()  # Clear the TIN number field
            self.insert_bir_checkBox.setChecked(False)
            self.insert_bp_checkBox.setChecked(False)
            self.insert_dti_checkBox.setChecked(False)

            # Show success message
            QMessageBox.information(self, "Success", insert_message)
            self.close()
        else:
            QMessageBox.critical(self, "Error", insert_message)

    def add_client_confirm(self):
        # Get input values
        client_name = self.client_name_lineEdit.text().strip()
        business_name = self.business_name_lineEdit.text().strip()
        contact_info = self.client_contactInfo_lineEdit.text().strip()
        tin_num = self.tin_num_lineEdit.text().strip()

        # Add more fields as necessary

        # Check if any field is empty
        if not client_name or not business_name or not contact_info or not tin_num:
            QMessageBox.warning(self, "Incomplete Data", "Please fill in all required fields before proceeding.")
            return
        if self.insert_dti_checkBox.isChecked() and self.insert_bp_checkBox.isChecked():
            self.stackedWidget.setCurrentIndex(12)
            customize.show_all_payment_frame(self)
        elif self.insert_dti_checkBox.isChecked():
            self.stackedWidget.setCurrentIndex(12)
            customize.hide_bp_part(self)
            # Populate year combo box when DTI is checked
            self.setFixedSize(780,450)
        elif self.insert_bp_checkBox.isChecked():
            self.stackedWidget.setCurrentIndex(12)
            customize.hide_dti_part(self)
        else:
            self.process_client_data()


    def add_client_cancel(self):
        self.close()

    def add_client_confirm_verify(self):
        self.process_client_data()

    def go_back_add_client(self):
        self.stackedWidget.setCurrentIndex(11)
        self.setFixedSize(780, 800)

    def add_client_cancel_verify(self):
        self.close()

    def delete_client_confirm(self):
        """
        Perform deletion of the selected client from the database.
        """
        selected_client = self.choose_delete_clientBox.currentText()
        if selected_client == "No clients available" or not selected_client.strip():
            QMessageBox.warning(self, "Error", "Please select a valid client.")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete client '{selected_client}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = bookkeeping_function.delete_client_by_name(selected_client)
            if success:
                QMessageBox.information(self, "Success", f"Client '{selected_client}' has been deleted.")
                self.load_client_names()  # Refresh the client list

    def delete_client_cancel(self):
        self.close()

    def edit_client_confirm(self):
        if self.edit_dti_checkBox.isChecked() and self.edit_bp_checkBox.isChecked():
            self.stackedWidget.setCurrentIndex(15)
            customize.show_all_payment_edit(self)
        elif self.edit_dti_checkBox.isChecked():
            self.stackedWidget.setCurrentIndex(15)
            self.setFixedSize(780, 450)
            customize.edit_hide_bp_part(self)
        elif self.edit_bp_checkBox.isChecked():
            self.stackedWidget.setCurrentIndex(15)
            customize.edit_hide_dti_part(self)
        else:
            # Validate that a client is selected
            client_name = self.choose_edit_clientBox.currentText()
            if not client_name or client_name == "No clients available":
                QMessageBox.critical(self, "Error", "Please select a valid client.")
                return

            # Call the save function to process changes
            self.save_client_changes()
    def edit_client_cancel(self):
        self.close()

    def edit_client_confirm_verify(self):
        # Validate that a client is selected
        client_name = self.choose_edit_clientBox.currentText()
        if not client_name or client_name == "No clients available":
            QMessageBox.critical(self, "Error", "Please select a valid client.")
            return

        # Call the save function to process changes
        self.save_client_changes()

    def edit_client_cancel_verify(self):
        self.close()

    def go_back_edit_client(self):
        self.stackedWidget.setCurrentIndex(14)
        self.setFixedSize(780, 800)

    def load_dashboard_data(self):
        """
        Loads data into the dashboard_bookkeeping_services_table with prioritization and sorting.
        """
        data = bookkeeping_function.fetch_filtered_data(
            payment_type=self.dashboard_paymentTypeBox.currentText(),
            payment_status=self.dashboard_paymentStatusBox.currentText()
        )

        # Clear the table before populating
        self.dashboard_bookkeeping_services_table.setRowCount(0)
        # Populate the table
        for row_index, record in enumerate(data):
            self.dashboard_bookkeeping_services_table.insertRow(row_index)

            # Set client name
            self.dashboard_bookkeeping_services_table.setItem(
                row_index, 0, QTableWidgetItem(record["client_name"])
            )

            # Set payment type
            self.dashboard_bookkeeping_services_table.setItem(
                row_index, 1, QTableWidgetItem(record["payment_type"])
            )
            # Set payment date
            payment_date = record.get("payment_date")
            self.dashboard_bookkeeping_services_table.setItem(
                row_index, 2, QTableWidgetItem(payment_date if payment_date else "N/A")
            )

            # Create and apply the status widget for the third column
            status_widget = self.create_status_widget(record["status"])
            self.dashboard_bookkeeping_services_table.setCellWidget(row_index, 3, status_widget)


    def get_status_color(self, status):
        """
        Maps a status to a corresponding color.
        """
        color_mapping = {
            "TO BE RECEIVED": QColor("#FFC107"),   # Yellow
            "PENDING": QColor("#0288D1"),         # Light Blue
            "DEADLINE TO PAY": QColor("#FF5722"), # Red
            "COMPLETED": QColor("#04AA6D"),       # Green
            "OVERDUE": QColor("#f44336"),         # Gray\"TO BE RECEIVED": "#FFC107",

        }
        return color_mapping.get(status, QColor("#ffffff"))  # Default to white

    def create_status_widget(self, status):
        """
        Creates a QLabel widget with a background color based on the status.
        """
        label = QLabel(status)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"background-color: {self.get_status_color(status).name()};font: bold 12px 'Segoe UI'; color: black;")
        return label
    def populate_comboboxes(self):
        """
        Populate the dashboard_paymentTypeBox and dashboard_paymentStatusBox with dynamic values.
        Only statuses and payment types with applicable records are included.
        """
        # Populate payment types dynamically
        self.dashboard_paymentTypeBox.clear()
        self.dashboard_paymentTypeBox.addItem("DEFAULT")  # Add default option

        # Fetch distinct payment types based on filtered data
        filtered_data = bookkeeping_function.fetch_filtered_data()
        unique_payment_types = {record["payment_type"] for record in filtered_data}  # Extract unique payment types
        self.dashboard_paymentTypeBox.addItems(sorted(unique_payment_types))  # Add payment types to the combo box

        # Populate payment statuses dynamically
        self.dashboard_paymentStatusBox.clear()
        self.dashboard_paymentStatusBox.addItem("DEFAULT")  # Add default option

        unique_statuses = {record["status"] for record in filtered_data}  # Extract unique statuses
        ordered_statuses = ["OVERDUE", "DEADLINE TO PAY", "TO BE RECEIVED", "PENDING"]  # Display order
        for status in ordered_statuses:
            if status in unique_statuses:
                self.dashboard_paymentStatusBox.addItem(status)

    def setup_dashboard_filters(self):
        """
        Connect combo boxes to load data based on their selections.
        """
        self.dashboard_paymentTypeBox.currentTextChanged.connect(self.load_dashboard_data)
        self.dashboard_paymentStatusBox.currentTextChanged.connect(self.load_dashboard_data)

#-----------------------------------------------------------------CLASS MAINWINDOW--------------------------------------------------------------------------------#

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("main_window.ui", self)

        self.setMinimumSize(1020,440)

        # Add the line graph to dashboard_graph_layout
        self.add_line_graph_to_grid_layout()

        # # Customize
        customize.access_history_customize(self)
        customize.main_supply_customize(self)
        customize.main_bookkeeping_customize(self)
        customize.main_account_customize(self)
        self.welcome_username_label.setText(f"Welcome, {GlobalState.user}!")

        # role
        if GlobalState.role_num == 0:
            self.main_stackedWidget.setCurrentIndex(0)
            customize.toggled_admin(self)
        if GlobalState.role_num == 1:
            self.main_stackedWidget.setCurrentIndex(1)
            customize.toggled_supply_mgmt(self)
        if GlobalState.role_num == 2:
            self.main_stackedWidget.setCurrentIndex(2)
            customize.toggled_bookkeeping(self)
        #toggled
        self.toggle_btn.clicked.connect(self.toggled)
        #---dashboard----#
        self.dashboard_tab_btn.setChecked(True)
        self.dashboard_tab_btn.clicked.connect(self.dashboard_page)
        self.new_hardware_added_btn.clicked.connect(self.hardwares_added_popup)
        self.prices_updated_btn.clicked.connect(self.items_updated_popup)
        self.payment_receivable_month_btn.clicked.connect(self.open_notif_dialog)
        self.new_client_added_btn.clicked.connect(self.open_client_added_dialog)
        self.new_item_added_btn.clicked.connect(self.open_item_added_dialog)
        #-----supply management-----#
        self.supply_management_tab_btn.clicked.connect(self.supply_management_page)
        self.add_hardware_btn.clicked.connect(self.open_insert_hardware_dialog)
        self.delete_hardware_btn.clicked.connect(self.open_delete_hardware_dialog)
        self.add_item_btn.clicked.connect(self.open_insert_item_dialog)
        self.delete_item_btn.clicked.connect(self.open_delete_item_dialog)
        self.createList_btn.clicked.connect(self.open_create_list_dialog)
        self.item_history_btn.clicked.connect(self.open_item_history_dialog)
        #-----bookkeeping-----#
        self.bookkeeping_tab_btn.clicked.connect(self.bookkeeping_page)
        self.add_client_btn.clicked.connect(self.open_insert_client_dialog)
        self.edit_client_btn.clicked.connect(self.open_edit_client_dialog)
        self.delete_client_btn.clicked.connect(self.open_delete_client_dialog)
        self.main_notif_btn.clicked.connect(self.open_notif_dialog)
        #---------accounts---------------------
        self.account_tab_btn.clicked.connect(self.account_page)
        #-----logout---------#
        self.logout_tab_btn.clicked.connect(self.logout)

        # # Start monitoring the internet connection
        self.internet_check_timer = QtCore.QTimer()
        self.internet_check_timer.timeout.connect(self.check_internet_connection)
        self.internet_check_timer.start(5000)  # Check every 5 seconds

        # Setup a timer to update statuses periodically
        self.status_update_timer = QTimer(self)
        self.status_update_timer.timeout.connect(update_payment_status)
        self.status_update_timer.start(86400000)  # Run once every 24 hours (86400000 ms)

        # Set up a timer to check the role every 5 seconds
        self.role_check_timer = QTimer(self)
        self.role_check_timer.timeout.connect(self.check_role_change)
        self.role_check_timer.start(5000)  # 5000 ms = 5 seconds

        # Flag to prevent multiple notifications
        self.notified_role_change = False

        # Call the function once during startup
        update_payment_status()

#------------------------------LOAD DATA-----------------------------------#
        self.load_access_history()
        self.load_hardware_count()
        self.loadHardwareNames()
        self.loadSupplyManagementData()
        self.setupItemFilters()
        distinct_client_count = bookkeeping_function.get_distinct_client_count()
        self.count_clients_listed.setText(str(distinct_client_count))  # Assuming you have a label named count_hardwares_listed
        self.setupBookkeepingFilters()
        self.setup_filters()  # Initialize the filters
        self.populate_account_list_table()  # Populate the table initiall


        # Monitor current time
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1)
        customize.date_current(self)
#---------------------------SHOW REAL-TIME TIMER------------------------------------#

    def showTime(self):
        currentTime = QTime.currentTime()
        display_Txt = currentTime.toString("hh:mm:ss")
        self.time_label.setText(display_Txt)
#----------------------------CHECK ROLE-----------------------------------------------#
    def check_role_change(self):
        """
        Checks if the user's role has changed in the database.
        If it has, redirects the user to the login page.
        """
        if self.notified_role_change:
            return  # Skip if already notified

        try:
            current_role = login_function.get_current_user_role(GlobalState.user)
            if current_role != GlobalState.role:
                self.notified_role_change = True  # Set flag to prevent further notifications
                QMessageBox.warning(
                    self,
                    "Session Alert",
                    "Your role has changed. You need to log in again."
                )
                self.redirect_to_login()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def redirect_to_login(self):
        """
        Redirects the user to the login page.
        """
        self.close()  # Close the MainWindow
        login_window = Login()  # Replace with your actual login window instance
        widget.addWidget(login_window)
        widget.setCurrentWidget(login_window)

#-----------------------------------TOGGLED--------------------------------------------#
    def toggled(self):
        customize.toggled(self)


#---------------------------------INTERNET CHECKER-------------------------------------#
    def check_internet_connection(self):
        if not is_connected():
            QMessageBox.critical(
                self,
                "No Internet Connection",
                "The internet connection has been lost. The application will now close.",
            )
            sys.exit(1)  # Exit the program if connection is lost

#---------------------------DASHBOARD-------------------------------#
    def hardwares_added_popup(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 9

        # Show dialog
        dialog = PopupDialog(self)
        dialog.exec_()  # Modal dialog; pauses main window until closed

        self.setEnabled(True)

    def items_updated_popup(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 10

        # Show dialog
        dialog = PopupDialog(self)
        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

    def add_line_graph_to_grid_layout(self):
        """
        Adds a line graph to the dashboard showing the distribution of statuses with smaller text sizes.
        """
        # Fetch data for the graph
        status_counts = fetch_status_counts()

        # Updated statuses and their sequence
        statuses = ["TO BE RECEIVED", "PENDING", "DEADLINE TO PAY", "COMPLETED", "OVERDUE"]
        counts = [status_counts.get(status, 0) for status in statuses]

        # Create a Matplotlib figure and canvas
        figure = Figure(facecolor="white")
        canvas = FigureCanvas(figure)

        # Add the canvas to gridLayout_7
        self.dashboard_graph_layout.addWidget(canvas)

        # Plot the line graph
        ax = figure.add_subplot(111)
        ax.plot(statuses, counts, label="Status Count", marker='o', color='b')

        # Customizing the graph
        ax.set_title("Yearly Status Distribution", fontsize=7)  # Smaller font for the title
        ax.set_xlabel("Status", fontsize=7)  # Smaller font for x-axis label
        ax.set_ylabel("Count", fontsize=7)  # Smaller font for y-axis label
        ax.tick_params(axis='both', which='major', labelsize=7)  # Smaller tick labels
        ax.legend(fontsize=7)  # Smaller legend text
        ax.grid(True)

    def dashboard_page(self):
        # Clear the existing layout to remove the old graph
        while self.dashboard_graph_layout.count():
            item = self.dashboard_graph_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


        # Refresh other dashboard elements
        self.main_stackedWidget.setCurrentIndex(0)
        supply_management_function.supply_data_cache.clear()
        bookkeeping_function.bookkeeping_data_cache.clear()
        self.load_access_history()
        self.add_line_graph_to_grid_layout()
        self.load_hardware_count()
        supply_management_function.supply_data_cache.clear()
        bookkeeping_function.bookkeeping_data_cache.clear()
        distinct_client_count = bookkeeping_function.get_distinct_client_count()
        self.count_clients_listed.setText(str(distinct_client_count))


    def load_access_history(self):
        access_history = login_function.fetch_access_history()

        access_history.sort(key=lambda x: x["last_access"], reverse=True)

        self.access_history_table.setRowCount(len(access_history))

        for row_index, data in enumerate(access_history):
            username = data["username"]
            last_access = data["last_access"]

            # Use the format_time_difference from login_function
            time_diff = login_function.format_time_difference(last_access)

            self.access_history_table.setItem(row_index, 0, QTableWidgetItem(username))
            self.access_history_table.setItem(row_index, 1, QTableWidgetItem(time_diff))

    def load_hardware_count(self):
        count = supply_management_function.fetch_hardware_count()
        self.count_hardwares_listed.setText(str(count))

#-----------------------------SUPPLY MANAGEMENT PAGE---------------------------------#

    def loadSupplyManagementData(self, selected_category="DEFAULT", selected_hardware="DEFAULT", search_term=""):
        """Load supply management data into the supply_management_table with optional filters."""
        self.supply_management_table.setRowCount(0)  # Clear the table before loading new data
        supply_data = fetch_supply_data()

        print("hm")

        # Filter data based on selected category and hardware
        if selected_category != "DEFAULT":
            supply_data = [item for item in supply_data if item["category"] == selected_category]
        print("gege")

        if selected_hardware != "DEFAULT":
            supply_data = [item for item in supply_data if item["hardware_name"] == selected_hardware]

        # Filter by search term if provided
        if search_term:
            supply_data = [
                item for item in supply_data
                if search_term.lower() in item["item_name"].lower()
            ]

        supply_data = sorted(supply_data, key=lambda x: x["item_id"], reverse=True)

        if not supply_data:
            return  # No data to display

        print('tf')

        # Populate the table
        self.supply_management_table.setRowCount(len(supply_data))  # Set the number of rows
        for row_index, data in enumerate(supply_data):
            self.supply_management_table.setItem(row_index, 0, QTableWidgetItem(str(data["item_id"])))
            self.supply_management_table.setItem(row_index, 1, QTableWidgetItem(data["category"]))
            self.supply_management_table.setItem(row_index, 2, QTableWidgetItem(data["item_name"]))
            self.supply_management_table.setItem(row_index, 3, QTableWidgetItem(str(data["item_price"])))
            self.supply_management_table.setItem(row_index, 4, QTableWidgetItem(data["hardware_name"]))
            self.supply_management_table.setItem(row_index, 5, QTableWidgetItem(data["hardware_contactInfo"]))
            print('aha')

            button_style = """
                QPushButton {{
                    background-color: {bg_color};
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    cursor: pointer;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """

            # Create a container widget for the buttons
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(3, 3, 3, 3)
            button_layout.setSpacing(8)

            info_button = QPushButton()
            info_button.setIcon(QIcon("images/ICON_VIEW.png"))
            info_button.setIconSize(QSize(19, 19))
            info_button.setStyleSheet(button_style.format(
                bg_color="#28a745", hover_color="#218838", pressed_color="#1e7e34"))
            info_button.setFixedSize(33,23)
            info_button.setCursor(Qt.PointingHandCursor)  # Explicitly set cursor
            info_button.clicked.connect(lambda _, id=data["item_id"]: self.handle_button_click(id, "info"))
            button_layout.addWidget(info_button)

            # Edit Button
            edit_button = QPushButton()
            edit_button.setIcon(QIcon("images/ICON_EDIT.png"))
            edit_button.setIconSize(QSize(19, 19))
            edit_button.setStyleSheet(button_style.format(
                bg_color="#007bff", hover_color="#0056b3", pressed_color="#004085"))
            edit_button.setFixedSize(33, 23)
            edit_button.setCursor(Qt.PointingHandCursor)  # Explicitly set cursor
            edit_button.clicked.connect(lambda _, id=data["item_id"]: self.handle_button_click(id, "edit"))
            button_layout.addWidget(edit_button)

            print("uy")

            # Set the widget with buttons in the last column (index 5)
            self.supply_management_table.setCellWidget(row_index, 6, button_widget)
            supply_management_function.supply_data_cache.clear()
            print("nya")
        print('ahhaahah')

    def handle_button_click(self, item_id, action_type):
        """
        Handle button clicks for Info/Edit actions and update GlobalState.
        :param item_id: ID of the item clicked.
        :param action_type: Type of action ('info' or 'edit').
        """
        if action_type == "info":
            # Retrieve item details from the database
            item_details = supply_management_function.fetch_item_details_by_id(item_id)

            if item_details:
                # Open the dialog and populate its labels
                dialog = PopupDialog(self)

                # Set the labels in the dialog with the retrieved data
                dialog.details_item_category.setText(item_details.get("category", "N/A"))
                dialog.details_item_name.setText(item_details.get("item_name", "N/A"))
                dialog.details_item_price.setText(str(item_details.get("item_price", "N/A")))
                dialog.details_hardware_name.setText(item_details.get("hardware_name", "N/A"))
                dialog.details_hardware_location.setText(item_details.get("hardware_location", "N/A"))
                dialog.details_hardware_contact.setText(item_details.get("hardware_contactInfo", "N/A"))
                added_at = item_details.get("item_added_at")
                if added_at:
                    added_at_str = added_at.strftime("%Y-%m-%d %H:%M:%S")
                    dialog.details_item_added_at.setText(added_at_str)
                else:
                    dialog.details_item_added_at.setText("N/A")
                updated_at = item_details.get("item_updated_at")
                if updated_at:
                    updated_at_str = updated_at.strftime("%Y-%m-%d %H:%M:%S")
                    dialog.details_item_updated_at.setText(updated_at_str)
                else:
                    dialog.details_item_updated_at.setText("N/A")

                # Set the appropriate dialog view
                dialog.stackedWidget.setCurrentIndex(4)  # Assuming index 4 is the details view
                dialog.setFixedSize(900, 600)

                # Display the dialog
                dialog.exec_()
            else:
                QMessageBox.warning(self, "Error", "Unable to fetch item details. Please try again.")
        elif action_type == "edit":
            print('Initiating edit process...')
            # New logic for editing item details
            item_details = supply_management_function.fetch_item_details_for_edit(item_id)
            GlobalState.id = item_id

            if item_details:
                dialog = PopupDialog(self)
                print("Populating edit dialog fields...")
                dialog.details_item_category_edit.setText(item_details.get("category", "N/A"))
                dialog.details_item_name_edit.setText(item_details.get("item_name", "N/A"))
                dialog.edit_item_price_lineEdit.setText(str(item_details.get("item_price", "N/A")))
                print("Setting dialog to edit view.")
                dialog.stackedWidget.setCurrentIndex(5)  # Edit view
                dialog.setFixedSize(600, 500)
                dialog.exec_()

                self.loadHardwareNames()  # Refresh hardware names if needed
                supply_management_function.supply_data_cache.clear()  # Clear the cache
                self.loadSupplyManagementData()

            else:
                QMessageBox.warning(self, "Error", "Unable to fetch item details for editing. Please try again.")


    def setupItemFilters(self):
        """Connect item filters to their corresponding signals."""
        self.categoryBox.currentTextChanged.connect(self.applyItemFilters)
        self.hardwareBox.currentTextChanged.connect(self.applyItemFilters)
        self.search_item_lineEdit.textChanged.connect(self.applyItemFilters)

    def applyItemFilters(self):
        """Apply item filters based on category, hardware, and search term."""
        selected_category = self.categoryBox.currentText()
        selected_hardware = self.hardwareBox.currentText()
        search_term = self.search_item_lineEdit.text()

        # Reload the table with the applied filters
        self.loadSupplyManagementData(selected_category, selected_hardware, search_term)

    def loadHardwareNames(self):
        self.hardwareBox.clear()
        hardware_names = fetch_hardware_names()
        if hardware_names:
            hardware_names.sort()  # Sort the list alphabetically
            self.hardwareBox.addItem("DEFAULT")
            self.hardwareBox.addItems(hardware_names)
    def supply_management_page(self):
        self.main_stackedWidget.setCurrentIndex(1)

    def open_insert_hardware_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 0

        # Show dialog
        dialog = PopupDialog(self)

        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

        self.loadHardwareNames()  # Refresh hardware names if needed
        supply_management_function.supply_data_cache.clear()  # Clear the cache
        self.loadSupplyManagementData()
        self.applyItemFilters()


    def open_delete_hardware_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 2

        # Show dialog
        dialog = PopupDialog(self)

        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

        self.loadHardwareNames()  # Refresh hardware names if needed
        supply_management_function.supply_data_cache.clear()  # Clear the cache
        self.loadSupplyManagementData()
        self.applyItemFilters()


    def open_insert_item_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 1

        # Show dialog
        dialog = PopupDialog(self)
        dialog.load_categories_for_hardware_insert()
        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

        self.loadHardwareNames()  # Refresh hardware names if needed
        supply_management_function.supply_data_cache.clear()  # Clear the cache
        self.loadSupplyManagementData()
        self.applyItemFilters()

    def open_delete_item_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 3

        # Show dialog
        dialog = PopupDialog(self)

        dialog.load_categories_for_deletion()

        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

        self.loadHardwareNames()  # Refresh hardware names if needed
        supply_management_function.supply_data_cache.clear()  # Clear the cache
        self.loadSupplyManagementData()
        self.applyItemFilters()

    def open_create_list_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 6

        # Show dialog
        dialog = PopupDialog(self)

        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

        self.loadHardwareNames()  # Refresh hardware names if needed
        supply_management_function.supply_data_cache.clear()  # Clear the cache
        self.loadSupplyManagementData()
        self.applyItemFilters()

    def open_item_added_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 19

        # Show dialog
        dialog = PopupDialog(self)

        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

    def open_item_history_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 21

        # Show dialog
        dialog = PopupDialog(self)

        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)


#-------------------------------BOOKKEEPING PAGE------------------------------------#
    def bookkeeping_page(self):
        if GlobalState.dash_num == 0:
            self.main_stackedWidget.setCurrentIndex(2)
            # Disable main window
            self.setEnabled(False)
            GlobalState.num = 16

            # Show dialog
            dialog = PopupDialog(self)

            dialog.exec_()  # Modal dialog; pauses main window until closed

            # Re-enable main window
            self.setEnabled(True)

            bookkeeping_function.bookkeeping_data_cache.clear()  # Clear the cache
            self.loadBookkeepingData()
            self.applyBookkeepingFilters()
            GlobalState.dash_num = 1
        else:
            self.main_stackedWidget.setCurrentIndex(2)

    def setupBookkeepingFilters(self):
        """
        Connect bookkeeping filters to their respective signals
        and trigger default data loading.
        """
        # Connect filters to their handlers
        self.search_client_lineEdit.textChanged.connect(self.applyBookkeepingFilters)
        self.paymentTypeBox.currentTextChanged.connect(self.applyBookkeepingFilters)
        self.paymentStatusBox.currentTextChanged.connect(self.applyBookkeepingFilters)

        # Trigger default loading (all data)
        self.applyBookkeepingFilters()

    def applyBookkeepingFilters(self):
        """
        Apply filters to refresh the bookkeeping table dynamically.
        Load all data by default if 'DEFAULT' is selected in combo boxes.
        """
        client_name = self.search_client_lineEdit.text().strip()  # Get search input
        payment_type = self.paymentTypeBox.currentText()  # Get payment type
        payment_status = self.paymentStatusBox.currentText()  # Get status

        # Load the table with applied filters
        self.loadBookkeepingData(client_name, payment_type, payment_status)

    def create_status_widget(self, status):
        """
        Creates a custom-styled widget for payment status.
        """
        # Create a frame to hold the status
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {self.get_status_color(status)};")

        # Create a label for the status text
        label = QLabel(status)
        label.setStyleSheet("font: bold 12px 'Segoe UI'; color: black;")
        label.setAlignment(Qt.AlignCenter)

        # Layout to center the label in the frame
        layout = QHBoxLayout(frame)
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for clean alignment

        return frame

    def get_status_color(self, status):
        """
        Returns the color corresponding to the status.
        """
        status_colors = {
            "TO BE RECEIVED": "#FFC107",
            "COMPLETED": "#04AA6D",
            "PENDING": "#0288D1",
            "DEADLINE TO PAY": "#FF5722",
            "OVERDUE": "#f44336"
        }
        return status_colors.get(status, "gray")  # Default to gray if status is unknown

    def create_action_button(self, client_id, payment_type):
        """
        Creates a styled action button for bookkeeping_services_table, passing both client_id and payment_type.
        """
        button = QPushButton("")
        button.setIcon(QIcon("images/ICON_CHANGE.png"))
        button.setIconSize(QSize(19, 19))
        button.setFixedSize(33, 23)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)

        # Pass both client_id and payment_type to the handler
        button.clicked.connect(lambda: self.handleBookkeepingAction(client_id, payment_type))

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(button)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setAlignment(Qt.AlignCenter)
        return container

    def loadBookkeepingData(self, client_name="", payment_type="DEFAULT", payment_status="DEFAULT"):
        """
        Load bookkeeping data into the table using filters.
        """
        self.bookkeeping_services_table.setRowCount(0)  # Clear the table

        # Fetch data with filters
        bookkeeping_data = fetch_bookkeeping_data(client_name, payment_type=payment_type, payment_status=payment_status)

        if not bookkeeping_data:
            return  # No data to display
        status_priority = {
            'OVERDUE': 1,
            'DEADLINE TO PAY': 2,
            'TO BE RECEIVED': 3,
            'PENDING': 4,
            'COMPLETED': 5
        }

        # Sort data by payment_date and status priority
        sorted_data = sorted(bookkeeping_data, key=lambda x: (x["payment_date"], status_priority.get(x["status"], 6)))

        self.bookkeeping_services_table.setRowCount(len(sorted_data))

        for row_index, data in enumerate(sorted_data):
            self.bookkeeping_services_table.setItem(row_index, 0, QTableWidgetItem(str(data["client_id"])))
            self.bookkeeping_services_table.setItem(row_index, 1, QTableWidgetItem(str(data["tin_num"])))
            self.bookkeeping_services_table.setItem(row_index, 2, QTableWidgetItem(data["client_name"]))
            self.bookkeeping_services_table.setItem(row_index, 3, QTableWidgetItem(data["business_name"]))
            self.bookkeeping_services_table.setItem(row_index, 4, QTableWidgetItem(data["contact_info"]))
            self.bookkeeping_services_table.setItem(row_index, 5, QTableWidgetItem(data["payment_type"]))
            self.bookkeeping_services_table.setItem(row_index, 6, QTableWidgetItem(data["payment_date"]))
            self.bookkeeping_services_table.setItem(row_index, 7, QTableWidgetItem(data["status"]))

            # Create status widget for the 'status' column
            status_widget = self.create_status_widget(data["status"])
            self.bookkeeping_services_table.setCellWidget(row_index, 7, status_widget)

            # Add action button for each row in the 'action' column
            button_widget = self.create_action_button(data["client_id"], data["payment_type"])
            self.bookkeeping_services_table.setCellWidget(row_index, 8, button_widget)

    def handleBookkeepingAction(self, client_id, payment_type):
        """
        Handle actions for changing the status of bookkeeping entries based on client_id and payment_type.
        Provides user choices for 'TO BE RECEIVED' and confirmation for other statuses.
        """
        client_data = bookkeeping_function.fetch_client_data_for_action(client_id, payment_type)

        if not client_data:
            QMessageBox.warning(self, "Error", "Failed to fetch client data.")
            return

        current_status = client_data.get("status")

        # Define possible transitions
        transitions = {
            "TO BE RECEIVED": ["PENDING", "COMPLETED"],
            "PENDING": ["COMPLETED"],
            "DEADLINE TO PAY": ["COMPLETED"],
            "OVERDUE": ["COMPLETED"]
        }

        # Check if transitions exist for the current status
        if current_status not in transitions:
            QMessageBox.information(self, "Information", f"Status is already being set to 'COMPLETED'.")
            return

        # Handle statuses that require immediate confirmation
        if current_status in ["PENDING", "DEADLINE TO PAY", "OVERDUE"]:
            reply = QMessageBox.question(
                self,
                "Confirm Status Change",
                f"Are you sure you want to change the status of {payment_type} from '{current_status}' to 'COMPLETED'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # Update the status
                if bookkeeping_function.update_client_status(client_id, payment_type, "COMPLETED"):
                    QMessageBox.information(self, "Success", f"Status of {payment_type} updated to 'COMPLETED'.")
                    self.applyBookkeepingFilters()  # Refresh the table
                else:
                    QMessageBox.warning(self, "Error", "Failed to update status.")
            return

        # Prompt user to select a new status for 'TO BE RECEIVED'
        new_status, confirmed = self.askStatusChange(current_status, transitions[current_status])
        if not confirmed:
            return

        # Confirm the change
        reply = QMessageBox.question(
            self,
            "Confirm Status Change",
            f"Are you sure you want to change the status of {payment_type} to '{new_status}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Update the status
            if bookkeeping_function.update_client_status(client_id, payment_type, new_status):
                QMessageBox.information(self, "Success", f"Status of {payment_type} updated to '{new_status}'.")
                self.applyBookkeepingFilters()  # Refresh the table
            else:
                QMessageBox.warning(self, "Error", "Failed to update status.")

    def askStatusChange(self, current_status, options):
        """
        Displays a dialog for selecting a new status.
        :param current_status: The current status of the item.
        :param options: List of possible new statuses.
        :return: Tuple (selected_status, confirmed).
        """
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Choose Status")
        dialog.setText(f"The current status is '{current_status}'. Choose the new status:")
        dialog.setIcon(QMessageBox.Question)

        # Add buttons for each option
        buttons = {}
        for option in options:
            buttons[option] = dialog.addButton(option, QMessageBox.AcceptRole)

        # Add a CANCEL button (this will be the rightmost button)
        cancel_button = dialog.addButton(QMessageBox.Cancel)

        # Customize button styles
        if 'PENDING' in buttons:
            # Set the leftmost button (PENDING) color to #0288D1 (blue)
            buttons['PENDING'].setStyleSheet("""
                QPushButton {
                    background-color: #0288D1;
                    padding: 5px;
                    padding-right: 15px;
                    padding-left: 15px;
                    font-weight: bold;
                    color: black;
                }
                QPushButton:hover {
                    background-color: #0277BD;
                }
                QPushButton:pressed {
                    background-color: #01579B;
                }
            """)

        if 'COMPLETED' in buttons:
            # Set the center button (COMPLETED) color to #04AA6D (green)
            buttons['COMPLETED'].setStyleSheet("""
                QPushButton {
                    background-color: #04AA6D;
                    padding: 5px;
                    padding-right: 15px;
                    padding-left: 15px;
                    font-weight: bold;
                    color: black;
                }
                QPushButton:hover {
                    background-color: #038a56;
                }
                QPushButton:pressed {
                    background-color: #026f48;
                }
            """)

        # Set the CANCEL button to a default color (optional)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #d3d3d3;
                padding: 5px;
                color: black;
            }
            QPushButton:hover {
                background-color: #c0c0c0;
            }
            QPushButton:pressed {
                background-color: #a9a9a9;
            }
        """)

        # Display dialog and wait for user choice
        dialog.exec_()

        # Return the selected option and confirmation
        for option, button in buttons.items():
            if dialog.clickedButton() == button:
                return option, True

        return None, False

    def open_insert_client_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 11

        # Show dialog
        dialog = PopupDialog(self)

        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

        bookkeeping_function.bookkeeping_data_cache.clear()  # Clear the cache
        self.loadBookkeepingData()
        self.applyBookkeepingFilters()

    def open_edit_client_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 14

        # Show dialog
        dialog = PopupDialog(self)

        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

        bookkeeping_function.bookkeeping_data_cache.clear()  # Clear the cache
        self.loadBookkeepingData()
        self.applyBookkeepingFilters()
    def open_delete_client_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 13

        # Show dialog
        dialog = PopupDialog(self)

        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

        bookkeeping_function.bookkeeping_data_cache.clear()  # Clear the cache
        self.loadBookkeepingData()
        self.applyBookkeepingFilters()

    def open_notif_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 16

        # Show dialog
        dialog = PopupDialog(self)

        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

        bookkeeping_function.bookkeeping_data_cache.clear()  # Clear the cache
        self.loadBookkeepingData()
        self.applyBookkeepingFilters()
    def open_client_added_dialog(self):
        # Disable main window
        self.setEnabled(False)
        GlobalState.num = 17

        # Show dialog
        dialog = PopupDialog(self)

        dialog.exec_()  # Modal dialog; pauses main window until closed

        # Re-enable main window
        self.setEnabled(True)

        bookkeeping_function.bookkeeping_data_cache.clear()  # Clear the cache

#---------------------------------ACCOUNTS---------------------------------------------
    def account_page(self):
        self.main_stackedWidget.setCurrentIndex(3)
        self.populate_account_list_table()  # Populate the table

    def setup_filters(self):
        """
        Initialize and connect filters (role_comboBox and search_account_lineEdit).
        """
        from login_function import get_user_role, get_available_roles

        # Get the user's role
        user_role = get_user_role(GlobalState.user)
        if not user_role:
            QMessageBox.warning(self, "Error", "Invalid user role.")
            return

        # Populate the role combo box
        self.role_comboBox.clear()
        available_roles = get_available_roles(user_role)
        self.role_comboBox.addItems(available_roles)
        self.role_comboBox.setCurrentText("DEFAULT")

        # Connect signals
        self.search_account_lineEdit.textChanged.connect(self.populate_account_list_table)
        self.role_comboBox.currentTextChanged.connect(self.populate_account_list_table)

    def populate_account_list_table(self):
        """
        Populates the account_list_table with user data based on filters and role of GlobalState.user.
        - If 'HEAD ADMIN', exclude 'HEAD ADMIN' users from the table.
        - If 'ADMIN', exclude both 'HEAD ADMIN' and 'ADMIN' users from the table.
        - Includes filtering via search_account_lineEdit and role_comboBox.
        """
        try:
            from login_function import fetch_filtered_accounts

            # Get filters
            search_term = self.search_account_lineEdit.text().strip()
            role_filter = self.role_comboBox.currentText()

            # Fetch filtered accounts
            accounts = fetch_filtered_accounts(search_term, role_filter, GlobalState.role)

            # Clear the existing rows in the table
            self.account_list_table.setRowCount(0)

            # Define the button styling
            button_style = """
                QPushButton {{
                    background-color: {bg_color};
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    cursor: pointer;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """

            # Populate the table
            for row_index, account in enumerate(accounts):
                # Insert row into the table
                self.account_list_table.insertRow(row_index)

                # Populate columns
                self.account_list_table.setItem(row_index, 0, QTableWidgetItem(str(account["user_id"])))
                self.account_list_table.setItem(row_index, 1, QTableWidgetItem(account["username"]))
                self.account_list_table.setItem(row_index, 2, QTableWidgetItem(account["email"]))
                self.account_list_table.setItem(row_index, 3, QTableWidgetItem(account["role"]))
                # Format and add the date_registered field
                date_registered = account.get("date_registered")
                formatted_date = date_registered.strftime("%Y-%m-%d %H:%M:%S") if date_registered else "N/A"
                self.account_list_table.setItem(row_index, 4, QTableWidgetItem(formatted_date))

                # Create a container widget for the buttons
                button_widget = QWidget()
                button_layout = QHBoxLayout(button_widget)
                button_layout.setContentsMargins(3, 3, 3, 3)
                button_layout.setSpacing(8)

                # Edit Button
                edit_button = QPushButton()
                edit_button.setIcon(QIcon("images/ICON_EDIT.png"))
                edit_button.setIconSize(QSize(19, 19))
                edit_button.setStyleSheet(button_style.format(
                    bg_color="#007bff", hover_color="#0056b3", pressed_color="#004085"))
                edit_button.setFixedSize(33, 23)
                edit_button.setCursor(Qt.PointingHandCursor)
                edit_button.clicked.connect(lambda _, uid=account["user_id"]: self.handle_edit_button(uid))
                button_layout.addWidget(edit_button)

                # Delete Button
                delete_button = QPushButton()
                delete_button.setIcon(QIcon("images/ICON_DELETE.png"))
                delete_button.setIconSize(QSize(19, 19))
                delete_button.setStyleSheet(button_style.format(
                    bg_color="#f44336", hover_color="#aa2e25", pressed_color="#661b16"))
                delete_button.setFixedSize(33, 23)
                delete_button.setCursor(Qt.PointingHandCursor)
                delete_button.clicked.connect(lambda _, uid=account["user_id"]: self.handle_delete_button(uid, row_index))
                button_layout.addWidget(delete_button)

                # Add the button widget to the table
                self.account_list_table.setCellWidget(row_index, 5, button_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while populating the table: {e}")

    def handle_edit_button(self, user_id):
        """
        Handles the edit button click for editing user details.
        """
        from login_function import fetch_accounts_for_user, get_available_roles, update_account_role, \
            get_current_user_role

        # Verify current user's role
        current_user_role = get_current_user_role(GlobalState.user)
        if current_user_role not in ["HEAD ADMIN", "ADMIN"]:
            QMessageBox.critical(self, "Access Denied", "You do not have permission to edit accounts.")
            return

        # Fetch account data for the selected user
        try:
            account_data = next(acc for acc in fetch_accounts_for_user(GlobalState.role) if acc["user_id"] == user_id)
        except StopIteration:
            QMessageBox.warning(self, "Error", "Account not found or not accessible.")
            return

        # Open PopupDialog and set stackedWidget to 20
        dialog = PopupDialog(self)
        dialog.stackedWidget.setCurrentIndex(20)
        dialog.setFixedSize(700, 600)

        # Populate fields in the dialog
        dialog.edit_details_username.setText(account_data["username"])
        dialog.edit_details_email.setText(account_data["email"])

        # Determine available roles, excluding 'DEFAULT'
        available_roles = get_available_roles(GlobalState.role)
        if "DEFAULT" in available_roles:
            available_roles.remove("DEFAULT")

        # Ensure 'WAITING FOR APPROVAL' is the last item
        available_roles = sorted(available_roles, key=lambda x: (x == "WAITING FOR APPROVAL", x))

        # Populate roles in combo box
        dialog.edit_role.clear()
        dialog.edit_role.addItems(available_roles)

        # Preselect the current role
        dialog.edit_role.setCurrentText(account_data["role"])

        def confirm_edit():
            new_role = dialog.edit_role.currentText()

            # Skip if role is unchanged
            if new_role == account_data["role"]:
                QMessageBox.information(self, "No Changes", "The role remains unchanged.")
                return

            # Confirm role change
            confirmation = QMessageBox.question(
                self,
                "Confirm Role Change",
                f"Are you sure you want to change the role to '{new_role}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirmation == QMessageBox.Yes:
                if update_account_role(user_id, new_role):
                    QMessageBox.information(self, "Success", f"Role updated to '{new_role}' successfully.")
                    dialog.close()
                    self.populate_account_list_table()  # Refresh account list
                else:
                    QMessageBox.critical(self, "Error", "Failed to update the account role.")

        def cancel_edit():
            dialog.close()

        dialog.edit_account_confirm_btn.clicked.connect(confirm_edit)
        dialog.edit_account_cancel_btn.clicked.connect(cancel_edit)
        dialog.exec_()

    def handle_delete_button(self, user_id, row_index):
        """
        Handles the delete button click.
        """
        from login_function import delete_account, get_current_user_role

        # Verify current user's role
        current_user_role = get_current_user_role(GlobalState.user)
        if current_user_role not in ["HEAD ADMIN", "ADMIN"]:
            QMessageBox.critical(self, "Access Denied", "You do not have permission to delete accounts.")
            return

        # Confirm delete action
        confirmation = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this account?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            if delete_account(user_id):
                QMessageBox.information(self, "Success", "Account deleted successfully.")
                self.account_list_table.removeRow(row_index)  # Remove row from table
            else:
                QMessageBox.critical(self, "Error", "Failed to delete account.")

    #------------------------------------LOGOUT-----------------------------------------#

    def logout(self):
        # n = login_function.logout_user_data(self)
        # if n == 0:
        login = Login()
        widget.addWidget(login)
        widget.showMaximized()
        widget.setCurrentIndex(widget.currentIndex() + 1)

#-------------------------------------------------LOGIN PAGE---------------------------------
class Login(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("login.ui", self)

        # Check account existence on startup
        if check_account_existence():
            self.stackedWidget.setCurrentIndex(0)  # Main page
        else:
            self.stackedWidget.setCurrentIndex(1)  # Registration page
            QMessageBox.warning(self, "No Account", "Create an account first.", )

        #buttons
        self.login_btn.clicked.connect(self.mainWindow_page)
        self.register_btn.clicked.connect(self.register_page)
        self.register_confirm_btn.clicked.connect(self.register_confirmed)
        self.register_cancel_btn.clicked.connect(self.register_cancelled)
        self.forgot_password_btn.clicked.connect(self.forgotPass_page)
        self.changePass_confirm_btn.clicked.connect(self.changePass_confirmed)
        self.changePass_cancel_btn.clicked.connect(self.changePass_cancelled)
        self.changePass_email_confirm_btn.clicked.connect(self.changePass_email_confirmed)
        self.changePass_email_cancel_btn.clicked.connect(self.changePass_email_cancelled)
        self.changePass_code_confirm_btn.clicked.connect(self.changePass_code_confirmed)
        self.changePass_code_cancel_btn.clicked.connect(self.changePass_code_cancelled)
        self.code_changePass_back_btn.clicked.connect(self.changePass_code_back)

        # # Start monitoring the internet connection
        self.internet_check_timer = QtCore.QTimer()
        self.internet_check_timer.timeout.connect(self.check_internet_connection)
        self.internet_check_timer.start(5000)  # Check every 5 seconds

        # Check if accounts exist in the database
        if not login_function.check_account_existence():
            # First user registration logic
            self.register_username_lineEdit.setText("admin")
            self.register_username_lineEdit.setDisabled(True)  # Temporarily disable this field
        else:
            pass
# ---------------------------------INTERNET CHECKER-------------------------------------#
    def check_internet_connection(self):
        if not is_connected():
            QMessageBox.critical(
                self,
                "No Internet Connection",
                "The internet connection has been lost. The application will now close.",
            )
            sys.exit(1)  # Exit the program if connection is lost

#--------------------TO MAIN WINDOW PAGE-------------------------#
    def mainWindow_page(self):
        print('test')
        n = login_function.verify_user_data(self)
        print("hi")
        GlobalState.dash_num == 0
        if n == 0 or n == 1:  # HEAD ADMIN
            GlobalState.role_num = 0
            main = MainWindow()
            widget.addWidget(main)
            widget.showMaximized()
            widget.setCurrentIndex(widget.currentIndex() + 1)

        elif n == 2:  # SUPPLY MGMT
            print("Logged in as SUPPLY MANAGEMENT.")
            GlobalState.role_num = 1
            main = MainWindow()
            widget.addWidget(main)
            widget.showMaximized()
            widget.setCurrentIndex(widget.currentIndex() + 1)

        elif n == 3:  # BOOKKEEPING
            print("Logged in as BOOKKEEPING.")
            GlobalState.role_num = 2
            main = MainWindow()
            widget.addWidget(main)
            widget.showMaximized()
            widget.setCurrentIndex(widget.currentIndex() + 1)

        elif n == 4:  # WAITING FOR APPROVAL
            QMessageBox.warning(self, "Approval Pending", "Your account is awaiting approval.")
            # Optionally close or redirect to another page

        else:  # Invalid credentials or unrecognized role
            print("Login failed or unrecognized role.")

    #-------------------------TO REGISTER PAGE-------------------------#
    def register_page(self):
        self.stackedWidget.setCurrentIndex(1)

    def register_confirmed(self):
        print('gg')

        # Validate email format
        email = self.register_email_lineEdit.text().strip()
        if not email or not self.is_valid_email(email):
            QMessageBox.warning(self, "Error", "Please enter a valid email address.")
            return

        # Check if email is unique
        if not login_function.is_email_unique(email):
            QMessageBox.warning(self, "Error", "Email already exists.")
            return

        if not login_function.check_account_existence():
            role = "HEAD ADMIN"
        else:
            role = "WAITING FOR APPROVAL"
        # Proceed with registration
        username = self.register_username_lineEdit.text().strip()
        password = self.register_password_lineEdit.text().strip()
        confirm_password = self.register_confirm_password_lineEdit.text().strip()

        n = login_function.register_user(username, password, confirm_password, email, role)

        print("hoy")
        if n == 0:
            self.register_username_lineEdit.setEnabled(True)
            self.register_username_lineEdit.setText("")
            self.register_email_lineEdit.setText("")
            self.register_password_lineEdit.setText("")
            self.register_confirm_password_lineEdit.setText("")
            self.stackedWidget.setCurrentIndex(0)

    def register_cancelled(self):
        if check_account_existence():
            self.stackedWidget.setCurrentIndex(0)  # Main page
        else:
            self.stackedWidget.setCurrentIndex(1)  # Registration page
            QMessageBox.warning(self, "No Account", "Create an account first.", )

    def is_valid_email(self, email):
        """
        Validates email format.
        Returns True if valid, otherwise False.
        """
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

#-----------------------------TO FORGOT PASSWORD PAGE-------------------------------#
    def forgotPass_page(self):
        self.stackedWidget.setCurrentIndex(4)

    def changePass_email_confirmed(self):
        """
        Verifies if the email exists in the database, sends a verification code,
        and redirects to the next step if successful.
        """
        verification_code = login_function.send_change_password_code(self)  # Call the function to send the code

        if verification_code is not None:
            self.generated_code = verification_code
            self.email_used_for_code = self.email_changePass_lineEdit.text().strip()
            self.stackedWidget.setCurrentIndex(3)  # Redirect to the next step
        else:
            QMessageBox.warning(self, "Error", "Failed to verify email or send the verification code.")

    def changePass_email_cancelled(self):
        self.stackedWidget.setCurrentIndex(0)

    def changePass_code_confirmed(self):
        """
        Verifies the input code and redirects to the next step if valid.
        """
        email = self.email_changePass_lineEdit.text().strip()  # Email from the form
        input_code = self.code_changePass_lineEdit.text().strip()  # Code entered by the user

        # Ensure the stored code and email exist
        stored_code = getattr(self, "generated_code", None)
        stored_email = getattr(self, "email_used_for_code", None)

        if stored_code is None or stored_email is None:
            QMessageBox.warning(self, "Error", "No verification code found. Please restart the process.")
            return

        # Check if the entered email matches the stored email
        if stored_email != email:
            QMessageBox.warning(self, "Error", "Email does not match the one used for verification.")
            return

        # Check if the entered code matches the stored code
        if input_code == str(stored_code):
            QMessageBox.information(self, "Success", "Code verified! Redirecting...")
            self.stackedWidget.setCurrentIndex(2)  # Redirect to the password reset page
        else:
            QMessageBox.warning(self, "Error", "Incorrect verification code. Please try again.")

    def changePass_code_cancelled(self):
        self.email_changePass_lineEdit.clear()
        self.code_changePass_lineEdit.clear()
        self.change_username_lineEdit.clear()
        self.change_password_lineEdit.clear()
        self.change_confirm_password_lineEdit.clear()
        self.stackedWidget.setCurrentIndex(0)

    def changePass_code_back(self):
        self.stackedWidget.setCurrentIndex(4)
    def changePass_confirmed(self):
        n = login_function.verify_changePass_data(self)
        if n == 0:
            self.email_changePass_lineEdit.clear()
            self.code_changePass_lineEdit.clear()
            self.change_username_lineEdit.clear()
            self.change_password_lineEdit.clear()
            self.change_confirm_password_lineEdit.clear()
            self.stackedWidget.setCurrentIndex(0)

    def changePass_cancelled(self):
        self.email_changePass_lineEdit.clear()
        self.code_changePass_lineEdit.clear()
        self.change_username_lineEdit.clear()
        self.change_password_lineEdit.clear()
        self.change_confirm_password_lineEdit.clear()
        self.stackedWidget.setCurrentIndex(0)






if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Login()
    widget = QStackedWidget()
    widget.addWidget(login)
    widget.setMinimumSize(800, 600)
    widget.setWindowTitle("Krizenix Trading")
    widget.setWindowIcon(QIcon('images/KSX_LOGO.png'))

    # Show maximized on start
    def show_maximized():
        widget.showMaximized()

    QtCore.QTimer.singleShot(0, show_maximized)

    widget.show()
    sys.exit(app.exec_())