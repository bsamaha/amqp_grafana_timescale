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
            # Assuming None for fields that are allowed to be NULL in the database
            "lat": None,  # Latitude can be NULL if not available
            "lon": None,  # Longitude can be NULL if not available
            "height": 0.0,  # Default height if not provided
            "hMSL": 0.0,  # Height above mean sea level
            "hAcc": 0.0,  # Horizontal accuracy
            "vAcc": 0.0,  # Vertical accuracy
            "velN": 0.0,  # Velocity North
            "velE": 0.0,  # Velocity East
            "velD": 0.0,  # Velocity Down
            "gSpeed": 0.0,  # Ground Speed
            "headMot": 0.0,  # Heading of motion
            "sAcc": 0.0,  # Speed accuracy
            "headAcc": 0.0,  # Heading accuracy
            "pDOP": 0.0,  # Positional Dilution of Precision
            "numSV": 0,  # Number of satellites
            "tAcc": 0,  # Time accuracy
            # For boolean fields, assuming False as default. Adjust based on your data handling needs.
            "validDate": 1,
            "validTime": 1,
            "gnssFixOk": False,
            # For textual data, assuming empty string if not applicable. Adjust as necessary.
            "fixType": "",
            # Assuming current year, month, day, hour, min, and second if not provided
            # These should ideally be populated with actual data to avoid defaults if possible
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
            elif key in ["lat", "lon", "height", "height_msl", "horizontal_acc", "vertical_acc", "velocity_north", "velocity_east", "velocity_down", "velocity", "heading_acc", "speed_over_ground", "heading_of_motion", "heading_of_vehicle", "magnetic_declination", "declination_acc", "pdop"]:
                try:
                    data[key] = float(data[key])
                except ValueError:
                    logger.error("Invalid value for %s, setting to default %s.", key, default)
                    data[key] = default

        # Ensure mandatory fields like 'full_time', 'device_id', and 'experiment_id' are valid
        if not data.get("full_time") or not data.get("device_id") or not data.get("experiment_id"):
            logger.error("Missing mandatory field 'full_time', 'device_id', or 'experiment_id'.")
            return None


        return data