# trimvision/core/drive_manager.py

import wmi
import psutil
import subprocess # For PowerShell
import json       # For PowerShell output
from trimvision.core.logger import logger # Assuming logger is in trimvision.core

class DriveInfo:
    def __init__(self, model, serial_number, firmware_version, capacity_gb,
                 device_id_wmi, physical_disk_index, interface_type_wmi, drive_letter, is_ssd, is_nvme,
                 ps_media_type="N/A", ps_bus_type="N/A", health_status="N/A",
                 controller="N/A", pcie_version="N/A"):
        self.model = model
        self.serial_number = serial_number
        self.firmware_version = firmware_version
        self.capacity_gb = capacity_gb
        self.device_id_wmi = device_id_wmi # e.g., \\.\PHYSICALDRIVE0
        self.physical_disk_index = physical_disk_index # e.g., 0, 1, ...
        self.interface_type_wmi = interface_type_wmi # From WMI, can be less accurate
        self.drive_letter = drive_letter
        self.is_ssd = is_ssd
        self.is_nvme = is_nvme
        self.health_status = health_status
        self.controller = controller
        self.pcie_version = pcie_version
        self.ps_media_type = ps_media_type
        self.ps_bus_type = ps_bus_type


    def __str__(self):
        type_str = "Unknown Drive"
        if self.is_nvme:
            type_str = "NVMe SSD"
        elif self.is_ssd: # If not NVMe but is SSD, assume SATA or other SSD type
            type_str = "SSD" # Could be "SATA SSD" if ps_bus_type is SATA
            if self.ps_bus_type and "SATA" in self.ps_bus_type.upper():
                type_str = "SATA SSD"

        elif self.ps_media_type and "HDD" in self.ps_media_type.upper():
            type_str = "HDD"

        return (f"{self.model} ({self.capacity_gb:.2f} GB) - {self.device_id_wmi} "
                f"[{type_str}] PS Bus: {self.ps_bus_type or 'N/A'} "
                f"Letter: {self.drive_letter or 'N/A'}")

    def get_display_name(self):
        type_str = "Drive"
        if self.is_nvme:
            type_str = "NVMe SSD"
        elif self.is_ssd:
            type_str = "SSD"
            if self.ps_bus_type and "SATA" in self.ps_bus_type.upper():
                type_str = "SATA SSD"

        return f"{self.model} ({type_str}, {self.capacity_gb:.2f} GB) - {self.drive_letter or self.device_id_wmi}"

def get_powershell_disk_info(physical_disk_index):
    try:
        command = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
            f"Get-PhysicalDisk -DeviceNumber {physical_disk_index} | Select-Object MediaType, BusType | ConvertTo-Json -Compress"
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False, creationflags=subprocess.CREATE_NO_WINDOW)

        if result.returncode == 0 and result.stdout:
            try:
                disk_data = json.loads(result.stdout)
                if isinstance(disk_data, list) and len(disk_data) > 0: disk_data = disk_data[0]
                elif not isinstance(disk_data, dict): return None, None
                
                ps_media_type = disk_data.get("MediaType")
                ps_bus_type = disk_data.get("BusType")
                logger.debug(f"PS info for disk idx {physical_disk_index}: MediaType={ps_media_type}, BusType={ps_bus_type}")
                return ps_media_type, ps_bus_type
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for PS output (disk {physical_disk_index}): {e}\nOutput: {result.stdout}")
                return None, None
        else:
            logger.warning(f"PS command failed for disk {physical_disk_index}. RC: {result.returncode}. Stderr: {result.stderr}")
            return None, None
    except FileNotFoundError:
        logger.error("PowerShell not found.")
        return None, None
    except Exception as e:
        logger.error(f"Error running PS Get-PhysicalDisk for idx {physical_disk_index}: {e}")
        return None, None

def get_physical_drive_letters(device_id_wmi_param):
    c = wmi.WMI()
    drive_letters = []
    try:
        query = f"ASSOCIATORS OF {{Win32_DiskDrive.DeviceID='{device_id_wmi_param.replace('\\', '\\\\')}'}} WHERE AssocClass = Win32_DiskDriveToDiskPartition"
        for partition in c.query(query):
            query2 = f"ASSOCIATORS OF {{Win32_DiskPartition.DeviceID='{partition.DeviceID}'}} WHERE AssocClass = Win32_LogicalDiskToPartition"
            for logical_disk in c.query(query2):
                drive_letters.append(logical_disk.DeviceID)
    except Exception as e: # Catching WMI specific errors might be better if known
        logger.error(f"Error getting drive letters for {device_id_wmi_param}: {e} (Code: {getattr(e, 'hresult', 'N/A')})")
    return sorted(list(set(drive_letters)))


def get_detailed_drive_info():
    logger.info("Scanning for drives using WMI and PowerShell...")
    drives_list = []
    try:
        wmi_instance = wmi.WMI()
        for disk_wmi in wmi_instance.Win32_DiskDrive():
            model = getattr(disk_wmi, 'Model', 'N/A')
            serial_number = getattr(disk_wmi, 'SerialNumber', 'N/A').strip() if getattr(disk_wmi, 'SerialNumber', None) else 'N/A'
            firmware_version = getattr(disk_wmi, 'FirmwareRevision', 'N/A').strip()
            capacity_bytes = int(getattr(disk_wmi, 'Size', 0))
            capacity_gb = capacity_bytes / (1024**3) if capacity_bytes else 0
            
            # This is the WMI path like \\.\PHYSICALDRIVE0
            current_device_id_wmi = getattr(disk_wmi, 'DeviceID', 'N/A')
            # This is the index like 0, 1, ...
            physical_disk_index = getattr(disk_wmi, 'Index', None)
            
            interface_type_wmi_val = getattr(disk_wmi, 'InterfaceType', 'N/A')
            media_type_wmi_raw = getattr(disk_wmi, 'MediaType', None)

            is_ssd_final = False
            is_nvme_final = False
            ps_media_type_res = "N/A"
            ps_bus_type_res = "N/A"

            if physical_disk_index is not None:
                ps_media_type_res, ps_bus_type_res = get_powershell_disk_info(physical_disk_index)
            else:
                logger.warning(f"Could not get WMI disk Index for {model} ({current_device_id_wmi}). Skipping PowerShell check.")

            if ps_media_type_res and ps_media_type_res != "N/A":
                if ps_media_type_res.upper() in ["SSD", "SCM"]: is_ssd_final = True
                if ps_bus_type_res and ps_bus_type_res.upper() == "NVME":
                    is_nvme_final = True
                    is_ssd_final = True # NVMe is always SSD
                logger.debug(f"Drive {model}: PS_MediaType='{ps_media_type_res}', PS_BusType='{ps_bus_type_res}'. Deduced: is_ssd={is_ssd_final}, is_nvme={is_nvme_final}")
            else: # Fallback if PowerShell fails
                logger.debug(f"Drive {model}: PowerShell check failed/NA. Falling back to WMI/model.")
                if "nvme" in model.lower() or interface_type_wmi_val.upper() == "NVME":
                    is_nvme_final = True
                    is_ssd_final = True
                if not is_ssd_final and media_type_wmi_raw in [4, 5]: is_ssd_final = True # WMI MediaType 4:SSD, 5:SCM
                if not is_ssd_final and "ssd" in model.lower(): is_ssd_final = True
            
            if not is_ssd_final:
                logger.info(f"Skipping non-SSD drive: {model} (DevID: {current_device_id_wmi}, PS_MediaType: {ps_media_type_res or 'N/A'})")
                continue

            drive_letters_str = ", ".join(get_physical_drive_letters(current_device_id_wmi))

            drive_obj = DriveInfo(
                model=model, serial_number=serial_number, firmware_version=firmware_version,
                capacity_gb=capacity_gb, device_id_wmi=current_device_id_wmi,
                physical_disk_index=physical_disk_index, interface_type_wmi=interface_type_wmi_val,
                drive_letter=drive_letters_str, is_ssd=is_ssd_final, is_nvme=is_nvme_final,
                ps_media_type=ps_media_type_res, ps_bus_type=ps_bus_type_res
            )
            drives_list.append(drive_obj)
            logger.info(f"Kept SSD Drive: {drive_obj}")

    except Exception as e:
        logger.error(f"General error enumerating drives: {e}", exc_info=True)

    if not drives_list:
        logger.warning("No SSD/NVMe drives suitable for TRIM were detected.")
    return drives_list


if __name__ == '__main__':
    # Ensure logger is configured if running this file directly for testing
    # from trimvision.utils.admin_checker import is_admin # Assuming this exists and works
    # if not is_admin(): print("Run as admin for WMI/PS access.")
    # else:
    # For direct testing, a simple logger setup:
    import logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger(__name__) # Use local logger for test

    drives = get_detailed_drive_info()
    if drives:
        print(f"\nFound {len(drives)} SSD/NVMe drives suitable for TRIM:")
        for i, drive_info in enumerate(drives):
            print(f"  {i+1}. Model: {drive_info.model}")
            print(f"     WMI Device ID: {drive_info.device_id_wmi}") # Check this name
            print(f"     PS MediaType: {drive_info.ps_media_type}")
            print(f"     Is SSD: {drive_info.is_ssd}, Is NVMe: {drive_info.is_nvme}")
            print(f"     Display Name: {drive_info.get_display_name()}")
            print("-" * 20)
    else:
        print("No SSD/NVMe drives found or an error occurred.")