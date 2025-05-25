# trimvision/ui/main_window.py

from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel,
                             QPushButton, QComboBox, QProgressBar, QTextEdit,
                             QMessageBox, QHBoxLayout, QFrame)
from PyQt6.QtCore import Qt, QTimer
from trimvision import config
from trimvision.core.logger import logger
from trimvision.core.drive_manager import get_detailed_drive_info, DriveInfo
from trimvision.core.trim_worker import TrimWorker
from trimvision.ui.lba_grid_widget import LbaGridWidget # <<< IMPORT NEW WIDGET

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... (window setup as before) ...
        self.setWindowTitle(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.setGeometry(100, 100, 1000, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- Top Section (Drive Select & Info) ---
        self.top_section_layout = QHBoxLayout()
        self.drive_selection_group = QWidget()
        self.drive_selection_v_layout = QVBoxLayout(self.drive_selection_group)
        self.info_panel_group = QWidget()
        self.info_panel_v_layout = QVBoxLayout(self.info_panel_group)
        self.top_section_layout.addWidget(self.drive_selection_group, 1)
        self.top_section_layout.addWidget(self.info_panel_group, 2)
        self.main_layout.addLayout(self.top_section_layout)

        # --- Separator ---
        line_separator = QFrame()
        line_separator.setFrameShape(QFrame.Shape.HLine)
        line_separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(line_separator) # Moved to be after top_section_layout

        # --- Middle section: LBA Grid ---
        self.lba_grid_widget = LbaGridWidget() # <<< REPLACE PLACEHOLDER
        self.lba_grid_widget.setMinimumHeight(300) # Ensure it takes up space
        self.main_layout.addWidget(self.lba_grid_widget)
        
        # --- Bottom section: Progress and Controls ---
        self.bottom_section_layout = QVBoxLayout()
        # ... (progress_bar, eta_label, controls_layout, status_label as before) ...
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Idle")
        self.bottom_section_layout.addWidget(self.progress_bar)

        self.eta_label = QLabel("ETA: N/A | Speed: N/A")
        self.eta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bottom_section_layout.addWidget(self.eta_label)

        self.controls_layout = QHBoxLayout()
        self.start_trim_button = QPushButton("Start TRIM")
        self.start_trim_button.clicked.connect(self.on_start_trim_clicked)
        self.start_trim_button.setEnabled(False)
        
        self.cancel_trim_button = QPushButton("Cancel TRIM")
        self.cancel_trim_button.clicked.connect(self.on_cancel_trim_clicked)
        self.cancel_trim_button.setEnabled(False)

        self.controls_layout.addWidget(self.start_trim_button)
        self.controls_layout.addWidget(self.cancel_trim_button)
        self.bottom_section_layout.addLayout(self.controls_layout)
        
        self.status_label = QLabel("Status: Idle")
        self.bottom_section_layout.addWidget(self.status_label)
        self.main_layout.addLayout(self.bottom_section_layout)


        self.drives_list = []
        self.current_selected_drive: DriveInfo = None
        self.trim_worker: TrimWorker = None

        self._init_ui_elements_content()
        self._load_drives()

        logger.info("Main window UI initialized.")

    # ... (_init_ui_elements_content, _load_drives methods as before) ...
    def _init_ui_elements_content(self):
        self.drive_select_label = QLabel("Select Drive:")
        self.drive_selection_v_layout.addWidget(self.drive_select_label)
        self.drive_combo = QComboBox()
        self.drive_combo.currentIndexChanged.connect(self.on_drive_selected)
        self.drive_selection_v_layout.addWidget(self.drive_combo)
        self.drive_selection_v_layout.addStretch(1)

        self.info_panel_label = QLabel("Drive Information:")
        self.info_panel_v_layout.addWidget(self.info_panel_label)
        self.info_panel_text = QTextEdit()
        self.info_panel_text.setReadOnly(True)
        self.info_panel_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.info_panel_v_layout.addWidget(self.info_panel_text)
        
    def _load_drives(self):
        logger.info("Loading available drives...")
        self.lba_grid_widget.reset_grid() # Reset grid when loading drives
        self.drives_list = get_detailed_drive_info()
        self.drive_combo.clear()
        if self.drives_list:
            for i, drive in enumerate(self.drives_list):
                self.drive_combo.addItem(drive.get_display_name(), userData=i)
            self.drive_combo.setCurrentIndex(-1) 
            self.on_drive_selected(self.drive_combo.currentIndex()) 
            logger.info(f"Found {len(self.drives_list)} SSD drives.")
        else:
            self.drive_combo.addItem("No compatible SSDs found.")
            self.drive_combo.setEnabled(False)
            self.start_trim_button.setEnabled(False)
            self.info_panel_text.setText("No SSD/NVMe drives detected or an error occurred.")
            logger.warning("No drives loaded into UI.")


    def on_drive_selected(self, index):
        if self.is_trim_running():
            # ... (logic to prevent changing drive during trim as before)
            if self.current_selected_drive:
                for i in range(self.drive_combo.count()):
                    drive_idx_in_list = self.drive_combo.itemData(i)
                    if drive_idx_in_list is not None and self.drives_list[drive_idx_in_list] == self.current_selected_drive:
                        self.drive_combo.setCurrentIndex(i)
                        break
            return

        self.lba_grid_widget.reset_grid() # Reset grid when a new drive is selected

        if index < 0 or not self.drives_list :
            self.info_panel_text.setText("Select a drive to see details.")
            self.start_trim_button.setEnabled(False)
            self.current_selected_drive = None
            return
        # ... (rest of on_drive_selected as before, ensuring selected_drive.device_id_wmi is used) ...
        drive_idx_in_list = self.drive_combo.itemData(index)
        if drive_idx_in_list is None or drive_idx_in_list >= len(self.drives_list):
            logger.error(f"Invalid drive index selected: {index}, userData: {drive_idx_in_list}")
            self.info_panel_text.setText("Error selecting drive.")
            self.start_trim_button.setEnabled(False)
            self.current_selected_drive = None
            return

        selected_drive: DriveInfo = self.drives_list[drive_idx_in_list]
        self.current_selected_drive = selected_drive

        info_str = (
            f"Model: {selected_drive.model}\n"
            f"Serial: {selected_drive.serial_number}\n"
            f"Firmware: {selected_drive.firmware_version}\n"
            f"Capacity: {selected_drive.capacity_gb:.2f} GB\n"
            f"WMI DevID: {selected_drive.device_id_wmi}\n"
            f"Phys. Index: {selected_drive.physical_disk_index}\n"
            f"WMI I/F: {selected_drive.interface_type_wmi}\n"
            f"PS MediaType: {selected_drive.ps_media_type}\n"
            f"PS BusType: {selected_drive.ps_bus_type}\n"
            f"Type: {selected_drive.get_display_name().split('(')[1].split(',')[0].strip()}\n"
            f"Letter(s): {selected_drive.drive_letter or 'N/A'}\n"
        )
        self.info_panel_text.setText(info_str)
        self.start_trim_button.setEnabled(True)
        logger.info(f"Drive selected: {selected_drive.model}")


    def on_start_trim_clicked(self):
        # ... (confirmation dialog as before) ...
        if not self.current_selected_drive:
            QMessageBox.warning(self, "No Drive Selected", "Please select a drive to TRIM.")
            return

        if self.is_trim_running():
            QMessageBox.information(self, "TRIM In Progress", "A TRIM operation is already running.")
            return

        drive_name = self.current_selected_drive.get_display_name()
        drive_path = self.current_selected_drive.device_id_wmi

        reply = QMessageBox.question(self, "Confirm TRIM Operation",
                                     f"Are you sure you want to perform a TRIM operation on:\n\n"
                                     f"{drive_name}\n({drive_path})\n\n"
                                     f"This will optimize the selected SSD. Ensure no critical operations are running on this drive.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            logger.info(f"User confirmed TRIM for: {drive_name}")
            self.status_label.setText(f"Starting TRIM on {drive_name}...")
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Starting...")
            self.eta_label.setText("ETA: Calculating... | Speed: N/A")

            # Initialize LBA Grid for the current operation
            # The TrimWorker default total_chunks is 100, pass this to grid for mapping
            self.trim_worker = TrimWorker(self.current_selected_drive) # Creates worker with its default 100 chunks
            self.lba_grid_widget.initialize_grid(
                self.current_selected_drive.capacity_gb,
                self.trim_worker.total_chunks # Pass worker's chunk count
            )

            self.trim_worker.progress_updated.connect(self.update_progress)
            self.trim_worker.chunk_state_changed.connect(self.lba_grid_widget.update_worker_chunk_state) # <<< CONNECT TO GRID
            self.trim_worker.trim_finished.connect(self.handle_trim_finished)
            self.trim_worker.error_occurred.connect(self.handle_trim_error)
            
            self.trim_worker.start()
            self.set_ui_for_trim_running(True)
        else:
            logger.info(f"User cancelled TRIM for: {drive_name}")
            self.status_label.setText("TRIM operation cancelled by user.")

    # ... (on_cancel_trim_clicked, update_progress methods as before) ...
    def on_cancel_trim_clicked(self):
        if self.is_trim_running():
            logger.info("Cancel TRIM button clicked.")
            reply = QMessageBox.question(self, "Cancel TRIM",
                                         "Are you sure you want to cancel the current TRIM operation?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.trim_worker.cancel_operation()
                self.status_label.setText("Cancelling TRIM operation...")
                self.cancel_trim_button.setEnabled(False) 
        else:
            logger.debug("Cancel TRIM clicked but no operation running.")

    def update_progress(self, processed_chunks, total_chunks, speed_mbps, eta_seconds):
        if total_chunks > 0:
            progress_percent = int((processed_chunks / total_chunks) * 100)
            self.progress_bar.setValue(progress_percent)
            self.progress_bar.setFormat(f"{progress_percent}% ({processed_chunks}/{total_chunks} Chunks)")

            eta_str = "Calculating..."
            if eta_seconds != float('inf') and eta_seconds >= 0:
                if eta_seconds < 60: eta_str = f"{eta_seconds:.0f}s"
                elif eta_seconds < 3600: eta_str = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
                else: eta_str = f"{int(eta_seconds // 3600)}h {int((eta_seconds % 3600) // 60)}m"
            
            speed_str = f"{speed_mbps:.2f} MB/s" if speed_mbps > 0 else "N/A"
            self.eta_label.setText(f"ETA: {eta_str} | Speed: {speed_str}")
        else:
            self.progress_bar.setFormat("Processing...")
            
    # REMOVE/REPLACE update_lba_grid_cell from MainWindow as it's now handled by LbaGridWidget directly
    # def update_lba_grid_cell(self, chunk_index, state):
    #     logger.debug(f"LBA Grid: Chunk {chunk_index} state changed to {state}")
    #     self.lba_grid_widget.setText(f"LBA Grid: Chunk {chunk_index + 1} is now {state}") # Old placeholder
    #     if state == "Processing":
    #         self.status_label.setText(f"Processing chunk {chunk_index + 1}/{self.trim_worker.total_chunks if self.trim_worker else 'N/A'}...")


    def handle_trim_finished(self, success, message):
        # ... (as before, but ensure LBA grid animation stops if any) ...
        logger.info(f"TRIM finished. Success: {success}, Message: {message}")
        self.status_label.setText(f"Status: {message}")
        self.progress_bar.setFormat(message)
        if self.lba_grid_widget: # Ensure grid exists
            self.lba_grid_widget._stop_processing_animation() # Stop any pulsing

        if success:
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "TRIM Complete", message)
        else:
            if "cancel" not in message.lower():
                 QMessageBox.warning(self, "TRIM Operation Ended", message)

        self.set_ui_for_trim_running(False)
        if self.trim_worker:
            self.trim_worker.deleteLater()
            self.trim_worker = None
        # Optionally, call self.lba_grid_widget.reset_grid() here or wait for new drive selection


    # ... (handle_trim_error, set_ui_for_trim_running, is_trim_running, closeEvent methods as before) ...
    def handle_trim_error(self, error_message):
        logger.error(f"TRIM worker explicitly emitted error: {error_message}")

    def set_ui_for_trim_running(self, is_running):
        self.start_trim_button.setEnabled(not is_running)
        self.cancel_trim_button.setEnabled(is_running)
        self.drive_combo.setEnabled(not is_running)

    def is_trim_running(self):
        return self.trim_worker is not None and self.trim_worker.isRunning()

    def closeEvent(self, event):
        if self.is_trim_running():
            reply = QMessageBox.question(self, "TRIM in Progress",
                                         "A TRIM operation is currently running. Are you sure you want to quit?\n"
                                         "This will attempt to cancel the operation.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                logger.info("Application closing with TRIM active. Cancelling worker.")
                self.trim_worker.cancel_operation()
                # A better way to handle this is to wait for the worker's 'finished' signal
                # For now, let's accept the close, the worker should stop soon.
                event.accept() 
                # QTimer.singleShot(500, self.close) # This can lead to recursive close calls
                # event.ignore() # Don't ignore if we're accepting
                return
            else:
                event.ignore()
                return
        
        logger.info("Application closing.")
        event.accept()