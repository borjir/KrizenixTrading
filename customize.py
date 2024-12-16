
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QPropertyAnimation, QSize
from PyQt5.QtWidgets import QDialog, QApplication, QGraphicsBlurEffect, QMessageBox, QAction, QHeaderView, QPushButton
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from datetime import datetime
from PyQt5.uic import loadUi
from PyQt5 import QtGui


def date_current(self):
    current_date = datetime.now()

    # Extract the day of the week and format the date
    day_of_week = current_date.strftime("%A")  # e.g., "Wednesday"
    formatted_date = current_date.strftime("%B %d, %Y")  # e.g., "November 27, 2024"
    self.day_label.setText(day_of_week +"   |")
    self.date_label.setText(formatted_date +"   |")

def toggled(self):
    width = self.side_bar_frame.width()
    if width == 100:
        newWidth = 350
    else:
        newWidth = 100

    self.animation = QPropertyAnimation(self.side_bar_frame, b"minimumWidth")
    self.animation.setDuration(250)
    self.animation.setStartValue(width)
    self.animation.setEndValue(newWidth)
    self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
    self.animation.start()

def toggled_admin(self):
    self.dashboard_tab_btn.setVisible(True)
    self.supply_management_tab_btn.setVisible(True)
    self.bookkeeping_tab_btn.setVisible(True)
    self.account_tab_btn.setVisible(True)
def toggled_supply_mgmt(self):
    self.dashboard_tab_btn.setVisible(False)
    self.bookkeeping_tab_btn.setVisible(False)
    self.account_tab_btn.setVisible(False)

def toggled_bookkeeping(self):
    self.dashboard_tab_btn.setVisible(False)
    self.supply_management_tab_btn.setVisible(False)
    self.account_tab_btn.setVisible(False)

def access_history_customize(self):
    self.access_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

def dashboard_popups(self):
    self.hardwares_added_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.items_updated_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.items_updated_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
    self.dashboard_bookkeeping_services_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.dashboard_bookkeeping_services_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
    self.dashboard_bookkeeping_services_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
    self.clients_added_this_day_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.items_added_this_day_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.items_added_this_day_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
    self.item_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.item_history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

def create_list_customize(self):
    self.check_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.check_list_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
    self.average_data_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.average_data_list_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    self.average_data_list_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    self.average_data_list_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
    self.item_data_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.item_data_list_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    self.item_data_list_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    self.item_data_list_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
    self.item_data_list_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
    self.hardware_data_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.hardware_data_list_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    self.hardware_data_list_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    self.hardware_data_list_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)


def main_supply_customize(self):
    self.supply_management_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.supply_management_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    self.supply_management_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
    self.supply_management_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
    self.supply_management_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)

def main_bookkeeping_customize(self):
    self.bookkeeping_services_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.bookkeeping_services_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    self.bookkeeping_services_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    self.bookkeeping_services_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
    self.bookkeeping_services_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
    self.bookkeeping_services_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
    self.bookkeeping_services_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)

def main_account_customize(self):
    self.account_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    self.account_list_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    self.account_list_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)

def hide_bp_part(self):
    self.bp_frame.setVisible(False)
    self.bt_frame.setVisible(False)
    self.sp_frame.setVisible(False)
    self.ccenro_frame.setVisible(False)
    self.fc_frame.setVisible(False)
    self.bc_frame.setVisible(False)
    self.dti_frame.setVisible(True)

def hide_dti_part(self):
    self.bp_frame.setVisible(True)
    self.bt_frame.setVisible(True)
    self.sp_frame.setVisible(True)
    self.ccenro_frame.setVisible(True)
    self.fc_frame.setVisible(True)
    self.bc_frame.setVisible(True)
    self.dti_frame.setVisible(False)

def show_all_payment_frame(self):
    self.bp_frame.setVisible(True)
    self.bt_frame.setVisible(True)
    self.sp_frame.setVisible(True)
    self.ccenro_frame.setVisible(True)
    self.fc_frame.setVisible(True)
    self.bc_frame.setVisible(True)
    self.dti_frame.setVisible(True)

def edit_hide_bp_part(self):
    self.bp_frame_edit.setVisible(False)
    self.bt_frame_edit.setVisible(False)
    self.sp_frame_edit.setVisible(False)
    self.ccenro_frame_edit.setVisible(False)
    self.fc_frame_edit.setVisible(False)
    self.bc_frame_edit.setVisible(False)
    self.dti_frame_edit.setVisible(True)

def edit_hide_dti_part(self):
    self.bp_frame_edit.setVisible(True)
    self.bt_frame_edit.setVisible(True)
    self.sp_frame_edit.setVisible(True)
    self.ccenro_frame_edit.setVisible(True)
    self.fc_frame_edit.setVisible(True)
    self.bc_frame_edit.setVisible(True)
    self.dti_frame_edit.setVisible(False)

def show_all_payment_edit(self):
    self.bp_frame_edit.setVisible(True)
    self.bt_frame_edit.setVisible(True)
    self.sp_frame_edit.setVisible(True)
    self.ccenro_frame_edit.setVisible(True)
    self.fc_frame_edit.setVisible(True)
    self.bc_frame_edit.setVisible(True)
    self.dti_frame_edit.setVisible(True)