# src/gui.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QWidget, QHeaderView, QSplitter, QPushButton, QHBoxLayout, QLabel, QLineEdit, QMenuBar, QAction, QMessageBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
import os

# (Stylesheet remains the same)
DARK_STYLESHEET = """
QWidget {
    background-color: #1e1e1e;
    color: #4dff4d;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}
QHeaderView::section {
    background-color: #333333;
    color: #4dff4d;
    padding: 4px;
    border: 1px solid #555555;
}
QTableWidget {
    gridline-color: #555555;
    border: 1px solid #555555;
}
QTableWidget::item {
    border-bottom: 1px solid #555555;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: #333333;
    border: 1px solid #555555;
    width: 15px;
    height: 15px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #555555;
    min-height: 20px;
    min-width: 20px;
}
QSplitter::handle {
    background-color: #555555;
}

QPushButton {
    color: white;
}

QLineEdit {
    color: white;
}
""" # Collapsed for brevity

class MainWindow(QMainWindow):
    location_selected = pyqtSignal(float, float)
    firewall_toggle_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.map_name = "map" # Default map name
        self._current_filter = None # Stores the active filter
        self.setWindowTitle("Conmon - Network Traffic Monitor")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(DARK_STYLESHEET)

        # Menu Bar
        menubar = self.menuBar()
        help_menu = menubar.addMenu("&Help")

        filter_help_action = QAction("&Filter Help", self)
        filter_help_action.triggered.connect(self.show_filter_help)
        help_menu.addAction(filter_help_action)

        main_widget = QWidget()
        main_widget.setStyleSheet(DARK_STYLESHEET)
        layout = QVBoxLayout(main_widget)

        # --- Control Bar ---
        control_bar = QHBoxLayout()
        self.firewall_toggle = QPushButton("Block Internet")
        self.firewall_toggle.setCheckable(True)
        self.firewall_toggle.toggled.connect(self.on_firewall_toggled)
        control_bar.addWidget(self.firewall_toggle)
        control_bar.addStretch(1)

        # Filter input and buttons
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter (e.g., process=chrome.exe, ip=1.2.3.4)")
        self.filter_input.setFixedWidth(300)
        control_bar.addWidget(self.filter_input)

        self.apply_filter_button = QPushButton("Apply Filter")
        self.apply_filter_button.clicked.connect(self.apply_filter)
        control_bar.addWidget(self.apply_filter_button)

        self.reset_filter_button = QPushButton("Reset Filters")
        self.reset_filter_button.clicked.connect(self.reset_filters)
        control_bar.addWidget(self.reset_filter_button)

        layout.addLayout(control_bar)
        
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background-color: #555555; }")

        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath('map.html')))
        splitter.addWidget(self.web_view)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels([
            "Destination IP", "Port", "Process Name", "Interface", "Data Volume (Bytes)", "Location", "Network Provider",
        ])
        font = QFont('Segoe UI', 10)
        self.table_widget.setFont(font)
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch) # Adjusted for new column
        self.table_widget.setSortingEnabled(True)
        self.table_widget.sortByColumn(3, Qt.DescendingOrder)
        self.table_widget.cellClicked.connect(self.on_cell_clicked)
        splitter.addWidget(self.table_widget)

        splitter.setSizes([400, 400])
        layout.addWidget(splitter)

        self.setCentralWidget(main_widget)

    def on_firewall_toggled(self, checked):
        self.firewall_toggle_changed.emit(checked)
        self.firewall_toggle.setText("Unblock Internet" if checked else "Block Internet")

    def find_row_by_key(self, key):
        """Helper function to find a row by its unique key stored in UserRole."""
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0) # Key is stored in the first column
            if item and item.data(Qt.UserRole) == key:
                return row
        return -1

    def add_or_update_connection(self, key, data):
        """Adds a new row or updates an existing one using a robust key search."""
        volume_item = QTableWidgetItem()
        volume_item.setData(Qt.DisplayRole, int(data['volume']))

        row = self.find_row_by_key(key)

        if row != -1:
            # --- Update Existing Row ---
            self.table_widget.setItem(row, 3, QTableWidgetItem(data.get("interface", "Unknown"))) # Update Interface column
            self.table_widget.setItem(row, 4, volume_item) # Adjusted for new column
            if data.get("process_name") and self.table_widget.item(row, 2).text() == "Unknown":
                 self.table_widget.setItem(row, 2, QTableWidgetItem(data["process_name"]))

            # Update text color for non-VPN traffic
            if data.get("interface") != 'NordLynx':
                yellow_color = QColor(255, 255, 0) # RGB for yellow
                for col in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, col)
                    if item:
                        item.setForeground(yellow_color)
            else:
                # Reset color to default if it was previously yellow and now is VPN
                default_color = QColor(77, 255, 77) # From DARK_STYLESHEET
                for col in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, col)
                    if item:
                        item.setForeground(default_color)
        else:
            # --- Add New Row ---
            self.table_widget.setSortingEnabled(False)
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)

            ip_item = QTableWidgetItem(data["dst_ip"])
            ip_item.setData(Qt.UserRole, key) # Store the unique key in the item

            self.table_widget.setItem(row_position, 0, ip_item)
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(str(data["dst_port"])))
            self.table_widget.setItem(row_position, 2, QTableWidgetItem(data.get("process_name", "Unknown")))
            self.table_widget.setItem(row_position, 3, QTableWidgetItem(data.get("interface", "Unknown"))) # New Interface column
            self.table_widget.setItem(row_position, 4, volume_item) # Adjusted for new column
            
            location_item = QTableWidgetItem("Resolving...")
            location_item.setData(Qt.UserRole, None) # Initialize lat/lon data
            self.table_widget.setItem(row_position, 5, location_item) # Adjusted for new column
            
            self.table_widget.setItem(row_position, 6, QTableWidgetItem("Resolving...")) # Adjusted for new column
            self.table_widget.setSortingEnabled(True)

        # Apply filter if active
        if self._current_filter:
            self._apply_filter_to_row(row if row != -1 else row_position, data)

    def update_resolved_info(self, ip, location, network, lat, lon):
        """Updates location and network for all rows with the matching IP."""
        # This function now needs to iterate through all rows to find matching IPs
        # as the key is no longer just IP.
        for row in range(self.table_widget.rowCount()):
            # Get the IP from the first column
            ip_item = self.table_widget.item(row, 0)
            if ip_item and ip_item.text() == ip:
                location_item = QTableWidgetItem(location)
                location_item.setData(Qt.UserRole, (lat, lon))
                self.table_widget.setItem(row, 5, location_item) # Adjusted for new column
                self.table_widget.setItem(row, 6, QTableWidgetItem(network)) # Adjusted for new column

    def on_cell_clicked(self, row, column):
        """Handle clicks on the table to pan the map."""
        location_item = self.table_widget.item(row, 5) # Adjusted for new column
        if location_item:
            lat_lon = location_item.data(Qt.UserRole)
            if lat_lon:
                self.location_selected.emit(lat_lon[0], lat_lon[1])

    def refresh_map(self):
        self.web_view.reload()

    def pan_map_to(self, lat, lon):
        """Executes JavaScript to pan the map view."""
        if lat is not None and lon is not None:
            self.web_view.page().runJavaScript(f"{self.map_name}.setView([{lat}, {lon}], 10);")

    def set_map_name(self, name):
        self.map_name = name

    def apply_filter(self):
        filter_text = self.filter_input.text().strip()
        if not filter_text:
            self.reset_filters()
            return

        filter_parts = filter_text.split('=', 1)
        if len(filter_parts) != 2:
            self.reset_filters()
            return

        self._current_filter = {
            "key": filter_parts[0].strip().lower(),
            "value": filter_parts[1].strip().lower()
        }

        for row in range(self.table_widget.rowCount()):
            # Retrieve the original data for the row to apply the filter
            # This assumes you have a way to get the full row data, e.g., from a model
            # For now, we'll re-evaluate based on visible items
            self._apply_filter_to_row(row, None) # Pass None for data, as we'll read from table

    def _apply_filter_to_row(self, row, data=None):
        """Applies the current filter to a specific row."""
        if not self._current_filter:
            self.table_widget.setRowHidden(row, False)
            return

        filter_key = self._current_filter["key"]
        filter_value = self._current_filter["value"]

        column_map = {
            "ip": 0,
            "port": 1,
            "process": 2,
            "interface": 3,
            "location": 5,
            "network": 6,
        }

        col_index = column_map.get(filter_key)
        if col_index is None:
            self.table_widget.setRowHidden(row, False)
            return

        item = self.table_widget.item(row, col_index)
        if item and filter_value in item.text().lower():
            self.table_widget.setRowHidden(row, False)
        else:
            self.table_widget.setRowHidden(row, True)

    def reset_filters(self):
        self.filter_input.clear()
        self._current_filter = None
        for row in range(self.table_widget.rowCount()):
            self.table_widget.setRowHidden(row, False)

    def show_filter_help(self):
        help_message = """
        Enter filters in the format: `field=value`

        Available fields:
        - `ip`: Destination IP address
        - `port`: Destination Port
        - `process`: Process Name
        - `interface`: Network Interface (e.g., NordLynx, Ethernet)
        - `location`: Geographical Location (City, Country)
        - `network`: Network Provider (ASN Organization)

        Example: `process=chrome.exe` or `interface=NordLynx`
        """
        QMessageBox.information(self, "Filter Help", help_message)
