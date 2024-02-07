from typing import Dict, Optional
from message_processors.base_processor import BaseProcessor
from db.db_manager import DBManager

from logger import setup_logger

logger = setup_logger("gngga_processor")


class GNGGAProcessor(BaseProcessor):
    def process(self):
        self.data = self.validate(self.data)
        logger.debug(f"Validated data: {self.data}")
        if self.data:
            table_name = "gngga"
            DBManager.insert_into_db(table_name=table_name,data=self.data)

    def validate(self, data: Dict) -> Optional[Dict]:
        """
        Validate GNGGA message data against SQL table schema.

        Parameters:
        - data: Dict representing the GNGGA message.

        Returns:
        - Dict with validated and possibly corrected data suitable for SQL insertion, or None if data is invalid.
        """
        # Default values for fields that can be empty or need conversion
        defaults = {
            "lat": None,  # Use NULL for database if not applicable
            "lon": None,
            "alt": 0.0,
            "sep": 0.0,
            "ns": "",
            "ew": "",
            "alt_unit": "",
            "sep_unit": "",
            "diff_age": -1,
            "diff_station": "",
        }

        # if message_type in data remove it
        if "message_type" in data:
            data.pop("message_type")
        # Validate and correct data
        for key, default in defaults.items():
            if not data.get(key) or data[key] == "":
                data[key] = default
            elif key in ["lat", "lon", "hdop", "alt", "sep"]:
                try:
                    data[key] = float(data[key])
                except ValueError:
                    logger.error(f"Invalid value for {key}, setting to default {default}.")
                    data[key] = default

        # Additional validations can be implemented as needed, e.g., checking if lat and lon are within valid ranges

        # Ensure mandatory fields like 'full_time' and 'device_id' are valid
        if not data.get("full_time") or not data.get("device_id"):
            logger.error("Missing mandatory field 'full_time' or 'device_id'.")
            return None  # Or handle as per requirements
        
        # Ensure 'quality' and 'num_sv' are non-negative
        if data["quality"] < 0 or data["num_sv"] < 0:
            logger.error("Invalid 'quality' or 'num_sv', setting to default 0.")
            data["quality"], data["num_sv"] = 0, 0

        return data
