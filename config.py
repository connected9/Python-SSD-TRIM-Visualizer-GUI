# trimvision/config.py

APP_NAME = "TrimVision"
APP_VERSION = "0.1.0"
APP_AUTHOR = "AI Generated (Enhanced by User)"
LOG_FILE = "trim_operations.log"

# LBA Grid Colors (can be refined later or moved to QSS)
COLOR_LBA_PROCESSED = (0, 180, 0)      # Green
COLOR_LBA_BLOCKED = (220, 0, 0)        # Red
COLOR_LBA_NON_PROCEEDED = (128, 128, 128) # Gray
COLOR_LBA_PROCESSING = (50, 150, 255) # Blue (for active cell)

# Default chunk size for LBA visualization (e.g., 1GB)
# This will be refined, drive size dependent.
DEFAULT_LBA_CHUNK_SIZE_MB = 1024 # 1 GB

# Max ranges for a single DeviceIoControl TRIM call (Windows limit is often 256, be conservative)
MAX_DSM_RANGES_PER_CALL = 64