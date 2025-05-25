# TrimVision (MENTOS): SSD/NVMe TRIM Process Visualizer for Windows

TrimVision is a modern, visually-stunning Python GUI application designed to visualize and manage the TRIM process for SSD/NVMe drives on Windows 10/11. It aims to provide both technical users and enthusiasts with an intuitive interface to understand and execute TRIM operations.

## ✨ Features

*   **Drive Detection & Information:**
    *   Automatically scans for and lists connected SSD and NVMe drives.
    *   Displays detailed drive specifications:
        *   Model, Serial Number, Firmware Version
        *   Total Capacity
        *   WMI Device ID & Physical Disk Index
        *   Interface Type (from WMI & PowerShell)
        *   PowerShell-derived MediaType (SSD/HDD) and BusType (SATA/NVMe/RAID)
        *   Assigned Drive Letter(s)
    *   *(Planned: SMART health status and warnings)*
*   **Real-Time TRIM Process Visualization (In Progress):**
    *   A dynamic grid representing Logical Block Addresses (LBAs).
    *   Color-coded blocks to show states: Non-Proceeded, Processing, Processed, Blocked.
    *   Progress bar, estimated time remaining (ETA), and current processing speed.
*   **TRIM Operation Management:**
    *   User confirmation before initiating TRIM.
    *   Background threading for TRIM operations to prevent UI freezing.
    *   Cancel TRIM operation mid-process.
*   **User Interface:**
    *   Clean, modern aesthetic.
    *   Responsive layout.
    *   *(Planned: Dark/Light mode toggle, advanced styling effects)*
*   **Logging & Safety:**
    *   Operations and errors are logged to `trim_operations.log`.
    *   Requires Administrator privileges for TRIM commands.
    *   Validates drives to attempt TRIM only on suitable SSDs.

## ⚠️ Important Safety Notes & Disclaimers

*   **ADMINISTRATOR PRIVILEGES REQUIRED:** TrimVision *must* be run as an administrator to perform TRIM operations and access necessary drive information. It will attempt to UAC-elevate itself if not run as admin.
*   **USE WITH CAUTION:** TRIM operations modify the state of your SSD. While standard TRIM is a safe and beneficial operation for SSD health and performance, always ensure you have selected the correct drive.
*   **BACKUP IMPORTANT DATA:** Although TRIM is a standard maintenance task, it's always a good practice to back up critical data before running any disk utility. The developers of TrimVision are not responsible for any data loss.
*   **EXPERIMENTAL SOFTWARE:** This application is currently under development. Use it at your own risk.
*   **SSD/NVME ONLY:** This tool is designed for Solid State Drives (SSDs) and NVMe drives. Do NOT attempt to use it on Hard Disk Drives (HDDs). The application attempts to filter for SSDs, but user discretion is advised.
*   **WINDOWS 10/11 ONLY:** TrimVision is specifically designed for and tested on Windows 10 and Windows 11.

## 🛠️ Installation

### Prerequisites

*   Windows 10 or Windows 11.
*   Python 3.9+ (Python 3.10 or 3.11 recommended). You can download Python from [python.org](https://www.python.org/downloads/windows/).
    *   Ensure "Add Python to PATH" is checked during installation.
*   Git (for cloning the repository).

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/TrimVision.git
    cd TrimVision
    ```
    *(Replace `your-username/TrimVision.git` with your actual repository URL)*

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    The `requirements.txt` file includes:
    *   `PyQt6`
    *   `psutil`
    *   `pySMART` (for future health status features)
    *   `WMI`

## 🚀 Usage

1.  **Ensure you have Administrator privileges.**
2.  Navigate to the project directory in your terminal (e.g., `cd TrimVision`).
3.  If you created a virtual environment, activate it: `venv\Scripts\activate`.
4.  Run the application:
    ```bash
    python -m trimvision
    ```
    Or:
    ```bash
    python trimvision/__main__.py
    ```

5.  The application will scan for drives. Select an SSD/NVMe drive from the "Select Drive" dropdown.
6.  Review the "Drive Information" panel.
7.  Click the "Start TRIM" button. A confirmation dialog will appear.
8.  Confirm to begin the TRIM process. You can monitor the progress via the LBA grid and progress bar.
9.  The "Cancel TRIM" button can be used to stop an ongoing operation.

## 📝 Logging

TrimVision logs its operations and any errors to a file named `trim_operations.log` located in the application's root directory (or the directory where the executable is run from).

## 🔧 Technical Implementation Details

*   **GUI Framework:** PyQt6
*   **Drive Communication:**
    *   WMI (Windows Management Instrumentation) for drive enumeration and basic info.
    *   PowerShell (`Get-PhysicalDisk`) for more accurate SSD/NVMe media and bus type detection.
    *   *(Planned: `ctypes` for direct `DeviceIoControl` TRIM commands for granular LBA control).*
    *   *(Planned: `pySMART` for S.M.A.R.T. health data).*
*   **Multithreading:** `QThread` is used to offload TRIM operations, keeping the UI responsive.

## 🗺️ Future Enhancements (Roadmap)

*   [ ] **Actual Low-Level TRIM:** Implement TRIM via `DeviceIoControl` for precise LBA range management.
*   [ ] **SMART Health Integration:** Display detailed S.M.A.R.T. attributes and overall health status.
*   [ ] **Advanced UI Styling:**
    *   Dark/Light mode toggle with smooth transitions.
    *   Glassmorphism or Neumorphism effects.
    *   Tooltips, hover animations, and micro-interactions.
*   [ ] **Pause/Resume TRIM:** Allow pausing and resuming the TRIM operation.
*   [ ] **Export Results:** Option to export TRIM results (drive health, operation duration, LBAs processed) to CSV/PDF.
*   [ ] **System Tray Minimization:** Allow minimizing to the system tray for long-running tasks.
*   [ ] **Keyboard Shortcuts.**
*   [ ] **Single Executable Packaging:** Provide a `.exe` using PyInstaller.

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name` or `git checkout -b fix/your-bug-fix`).
3.  Make your changes and commit them with clear, descriptive messages.
4.  Push your changes to your forked repository.
5.  Open a Pull Request to the `main` branch of this repository.

Please ensure your code adheres to general Python best practices and includes comments where necessary.

## 📜 License

This project is licensed under the [MIT License](LICENSE). *(You'll need to create a `LICENSE` file with the MIT License text if you choose this license).*
BY : RIFAT

---

*Disclaimer: This tool interfaces with system-level storage operations. The developers provide it as-is, without any warranty. Always use such tools responsibly and understand the potential risks.*
