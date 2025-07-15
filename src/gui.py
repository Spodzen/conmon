# src/gui.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QWidget, QHeaderView, QSplitter, QPushButton, QHBoxLayout, QLabel
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
import os

# (Stylesheet remains the same)
DARK_STYLESHEET = """...""" # Collapsed for brevity

class MainWindow(QMainWindow):
    location_selected = pyqtSignal(float, float)
    firewall_toggle_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conmon - Network Traffic Monitor")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(DARK_STYLESHEET)

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
        layout.addLayout(control_bar)
        
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background-color: #555555; }")

        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath('map.html')))
        splitter.addWidget(self.web_view)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels([
            "Destination IP", "Port", "Process Name", "Data Volume (Bytes)", "Location", "Network Provider",
        ])
        font = QFont('Segoe UI', 10)
        self.table_widget.setFont(font)
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
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
            self.table_widget.setItem(row, 3, volume_item)
            if data.get("process_name") and self.table_widget.item(row, 2).text() == "Unknown":
                 self.table_widget.setItem(row, 2, QTableWidgetItem(data["process_name"]))
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
            self.table_widget.setItem(row_position, 3, volume_item)
            
            location_item = QTableWidgetItem("Resolving...")
            location_item.setData(Qt.UserRole, None) # Initialize lat/lon data
            self.table_widget.setItem(row_position, 4, location_item)
            
            self.table_widget.setItem(row_position, 5, QTableWidgetItem("Resolving..."))
            self.table_widget.setSortingEnabled(True)

    def update_resolved_info(self, ip, location, network, lat, lon):
        """Updates location and network for all rows with the matching IP."""
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0)
            if item and item.text() == ip:
                location_item = QTableWidgetItem(location)
                location_item.setData(Qt.UserRole, (lat, lon))
                self.table_widget.setItem(row, 4, location_item)
                self.table_widget.setItem(row, 5, QTableWidgetItem(network))

    def on_cell_clicked(self, row, column):
        """Handle clicks on the table to pan the map."""
        location_item = self.table_widget.item(row, 4)
        if location_item:
            lat_lon = location_item.data(Qt.UserRole)
            if lat_lon:
                self.location_selected.emit(lat_lon[0], lat_lon[1])

    def refresh_map(self):
        self.web_view.reload()

    def pan_map_to(self, lat, lon):
        """Executes JavaScript to pan the map view."""
        if lat is not None and lon is not None:
            self.web_view.page().runJavaScript(f"map.setView([{lat}, {lon}], 10);")
