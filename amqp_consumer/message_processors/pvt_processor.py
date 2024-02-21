from typing import Dict, Optional
from message_processors.base_processor import BaseProcessor
from db.db_manager import DBManager
from logger import setup_logger

logger = setup_logger("nav_pvt_processor", level="DEBUG")


class NavPVTProcessor(BaseProcessor):
    def process(self):
        self.data = self.validate(self.data)
        logger.debug("Validated data: %s", self.data)
        if self.data:
            table_name = "nav_pvt"
            DBManager.insert_into_db(table_name=table_name, data=self.data)

    def validate(self, data: Dict) -> Optional[Dict]:
        """
        Validate NAV-PVT message data against SQL table schema.

        Parameters:
        - data: Dict representing the NAV-PVT message.

        Returns:
        - Dict with validated and possibly corrected data suitable for SQL insertion, or None if data is invalid.
        """
        # Default values for fields that can be empty or need conversion
        defaults = {
            "lat": None,
            "lon": None,
            "height": 0.0,
            "hMSL": 0.0,
            "hAcc": 0.0,
            "vAcc": 0.0,
            "velN": 0.0,
            "velE": 0.0,
            "velD": 0.0,
            "gSpeed": 0.0,
            "headMot": 0.0,
            "sAcc": 0.0,
            "headAcc": 0.0,
            "pDOP": 0.0,
            "numSV": 0,
            "tAcc": 0,
            "validDate": 0,  # Boolean, will be cast to int
            "validTime": 0,  # Boolean, will be cast to int
            "gnssFixOk": 0,  # Boolean, will be cast to int
            "fixType": "",
            "year": 2024,
            "month": 1,
            "day": 1,
            "hour": 0,
            "min": 0,
            "second": 0,
        }

        # Remove message_type as it's not part of the table schema
        data.pop("message_type", None)

        # Validate and correct data
        for key, default in defaults.items():
            if not data.get(key) or data[key] == "":
                data[key] = default
            elif key in ["lat", "lon", "height", "hMSL", "hAcc", "vAcc", "velN", "velE", "velD", "gSpeed", "headMot", "sAcc", "headAcc", "pDOP"]:
                try:
                    data[key] = float(data[key])
                except ValueError:
                    logger.error("Invalid value for %s, setting to default %s.", key, default)
                    data[key] = default
            elif key in ["validDate", "validTime", "gnssFixOk"]:
                # Cast boolean values to integer (True to 1, False to 0)
                data[key] = int(bool(data[key]))

        # Ensure mandatory fields like 'full_time', 'device_id', and 'experiment_id' are valid
        if not data.get("full_time") or not data.get("device_id") or not data.get("experiment_id"):
            logger.error("Missing mandatory field 'full_time', 'device_id', or 'experiment_id'.")
            return None

        # Optionally, convert 'full_time' to a timestamp format if it's not already
        # This step depends on how 'full_time' is represented in your incoming data
        # and how you want it formatted in your database.
        # Example conversion could be added here if necessary.

        return data