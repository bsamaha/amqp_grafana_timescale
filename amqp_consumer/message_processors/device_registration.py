"""
This module contains the DeviceRegistrationProcessor class, which processes device registration messages.
If the device is not registered, it will be added to the database. If the device is already registered, the id of the device will be returned from the hardware table.
"""

from logger import setup_logger
from db.db_manager import DBManager 
from message_processors.base_processor import BaseProcessor
from psycopg2 import DatabaseError
import json

logger = setup_logger(__name__, level="INFO")

class Hardware:
    def __init__(self) -> None:
        self.alias = None
        self.region = None
        self.location_desc = None
        self.owner_name = None
        self.make = None
        self.model = None
        self.signals = None
        self.configuration = None
        self.hardware_id = None
        self.attributes = {"experiment_id":1}

    def update_from_message_data(self, message_data: dict) -> None:
        if not isinstance(message_data, dict):
            raise ValueError("message_data must be a dictionary")
        
        for key in message_data:
            if hasattr(self, key):
                setattr(self, key, message_data[key])

class DeviceRegistrationProcessor(BaseProcessor):
    def __init__(self, message_data: dict) -> None:
        self.message_data = message_data
        self.hardware = Hardware()
        self.hardware_id = None
        

    def process(self) -> None:
        logger.info("Processing device registration message: %s", self.message_data)
        self.hardware.update_from_message_data(self.message_data)

        logger.info("Updated device registration message: %s", self.message_data)
        self.hardware_id = self.create_or_update_device(self.hardware)
        if self.hardware.attributes.get("experiment_id"):
            logger.info("Updating experiment_devices table with experiment_id: %s and device_id: %s", self.hardware.attributes.get("experiment_id"), self.hardware_id)
            self.update_experiment_devices_table(experiment_id=self.hardware.attributes.get("experiment_id"), device_id=self.hardware_id)            
        else:
            logger.error("Device could not be processed.")
        if self.hardware_id:
            logger.info("Device processed with ID: %s", self.hardware_id)
            return json.dumps(self.hardware_id)

    def get_hardware_id_from_alias(self, device_alias: str) -> int:
        query = """
        SELECT id FROM hardware WHERE alias = %s;
        """
        try:
            with DBManager.get_db_cursor(commit=True) as cur:
                cur.execute(query, (device_alias,))
                result = cur.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        except DatabaseError as e:
            logger.error("Failed to get device: %s", e)
            return None
        
    def insert_hardware(self):
        query = """
        INSERT INTO hardware (alias, region, location_desc, owner_name, make, model, signals, configuration)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        try:
            with DBManager.get_db_cursor(commit=True) as cur:
                cur.execute(query, (self.hardware.alias, self.hardware.region, self.hardware.location_desc, self.hardware.owner_name, self.hardware.make, self.hardware.model, self.hardware.signals, self.hardware.configuration))
                result = cur.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        except DatabaseError as e:
            logger.error("Failed to process device: %s", e)
            return None

    @staticmethod
    def create_or_update_device(hardware):
        query = """
        INSERT INTO hardware (alias, region, location_desc, owner_name, make, model, signals, configuration)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (alias) DO UPDATE SET
        region = EXCLUDED.region,
        location_desc = EXCLUDED.location_desc,
        owner_name = EXCLUDED.owner_name,
        make = EXCLUDED.make,
        model = EXCLUDED.model,
        signals = EXCLUDED.signals,
        configuration = EXCLUDED.configuration
        RETURNING id;
        """
        with DBManager.get_db_cursor(commit=True) as cur:
            cur.execute(query, (
                hardware.alias, hardware.region, hardware.location_desc, 
                hardware.owner_name, hardware.make, hardware.model, 
                hardware.signals, hardware.configuration))
            return cur.fetchone()[0]
        
        
    def update_device(self, device_id: int, device_alias: str, region: str, location_desc: str, owner_name: str, make: str, model: str, signals: str, configuration: str) -> None:
        """
        Updates the device with the given ID with the given parameters.
        """
        query = """
        UPDATE hardware
        SET alias = %s, region = %s, location_desc = %s, owner_name = %s, make = %s, model = %s, signals = %s, configuration = %s
        WHERE id = %s;
        """
        try:
            with DBManager.get_db_cursor(commit=True) as cur:
                cur.execute(query, (device_alias, region, location_desc, owner_name, make, model, signals, configuration, device_id))
        except DatabaseError as e:
            logger.error("Failed to update device: %s", e)

    def update_experiment_devices_table(self, experiment_id: int, device_id: int) -> bool:
        query = """
            INSERT INTO experiment_devices (experiment_id, device_id)
            VALUES (%s, %s)
            ON CONFLICT (experiment_id, device_id) DO NOTHING;
        """
        try:
            with DBManager.get_db_cursor(commit=True) as cur:
                cur.execute(query, (experiment_id, device_id))
                return True
        except DatabaseError as e:
            logger.error("Failed to update experiment_devices table: %s", e)
            return False
