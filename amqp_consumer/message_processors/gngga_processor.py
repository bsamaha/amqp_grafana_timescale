from message_processors.base_processor import BaseProcessor
from db.db_manager import DBManager

class GNGGAProcessor(BaseProcessor):
    def process(self):
        # Assuming self.data is a dict that contains all necessary information
        # This is where you'd implement the logic specific to GNGGA messages
        # For example, inserting the data into a database
        DBManager.insert_into_db(self.data)
