"""
This module is not needed at this time. The Experiments are going to be put into the DB in a very manual and deliberate way.
"""


from datetime import datetime
import json
from logger import setup_logger
from psycopg2 import DatabaseError
from message_processors.base_processor import BaseProcessor
from db.db_manager import DBManager

logger = setup_logger(__name__, level="INFO")

class Experiment:
    def __init__(self) -> None:
        self.alias = None
        self.configuration = None
        self.description = None
        self.end_time = None
        self.experiment_id = None
        self.experiment_type = None
        self.region = None
        self.start_time = None

    def _set_default_attributes(self) -> None:
        self.alias = None
        self.configuration = None
        self.description = None
        self.end_time = None
        self.experiment_id = None
        self.experiment_type = 'unknown'
        self.region = None
        self.start_time = datetime.now('UTC')

    def update_from_message_data(self, message_data: dict) -> None:
        self.alias = message_data.get('alias', self.alias)
        self.configuration = message_data.get('configuration', self.configuration)
        self.description = message_data.get('description', self.description)
        self.end_time = message_data.get('end_time', self.end_time)
        self.experiment_type = message_data.get('type', self.experiment_type)
        self.region = message_data.get('region', self.region)
        self.start_time = message_data.get('start_time', self.start_time)

class ExperimentRegistrationProcessor(BaseProcessor):
    def __init__(self, message_data: dict) -> None:
        self.message_data = message_data
        self.experiment = Experiment()
        self.experiment._set_default_attributes()
        self.experiment = self.experiment.update_from_message_data(message_data)
        logger.info("Processing experiment registration message: %s", message_data)

    def process(self) -> int:
        experiment_id = self.create_experiment_if_not_exists()
        return experiment_id

    def get_experiment_by_id(self, experiment_id: int) -> Experiment:
        query = """
            SELECT * FROM experiments WHERE id = %s;
        """
        try:
            with DBManager.get_db_cursor(commit=True) as cur:
                cur.execute(query, (experiment_id,))
                result = cur.fetchone()
                if result:
                    experiment = Experiment()
                    experiment.update_from_message_data(result)
                    return experiment
                else:
                    return None
        except DatabaseError as e:
            logger.error("Failed to get experiment by ID: %s", e)
            return None
        

    def create_experiment_if_not_exists(self):
        """
        Inserts a new experiment into the experiments table if an experiment with the same alias does not already exist.
        
        Parameters:
        - alias (str): The unique alias for the experiment.
        - start_time (datetime): The start time of the experiment.
        - end_time (datetime): The end time of the experiment. Can be None.
        - description (str): The description of the experiment.
        - configuration (jsonb): The JSON configuration of the experiment.
        - region (str): The region where the experiment is conducted.
        - experiment_type (str): The type of the experiment ('Static', 'Dynamic', 'Hybrid').
        
        Returns:
        - experiment_id (int): The ID of the created experiment on success, or None if the experiment already exists or on failure.
        """
        query = """
            WITH upsert AS (
                INSERT INTO experiments (alias, start_time, end_time, description, configuration, region, type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (alias) DO NOTHING
                RETURNING id
            )
            SELECT id FROM upsert
            UNION ALL
            SELECT id FROM experiments WHERE alias = %s AND NOT EXISTS (SELECT 1 FROM upsert);
        """
        logger.info("Creating experiment with alias: %s", self.experiment.alias)
        try:
            with DBManager.get_db_cursor(commit=True) as cur:
                # Execute the query with parameters for the SELECT and the NOT EXISTS check, including the alias
                cur.execute(query, (self.experiment.alias, self.experiment.start_time, self.experiment.end_time, self.experiment.description, json.dumps(self.experiment.configuration), self.experiment.region, self.experiment.experiment_type, self.experiment.alias))
                result = cur.fetchone()
                if result:
                    experiment_id = result[0]
                    logger.info("Experiment created successfully with ID: %s", experiment_id)
                    return experiment_id
                else:
                    logger.info("Experiment with the given alias already exists or could not be created.")
                    return None
        except DatabaseError as e:
            logger.error("Failed to insert experiment: %s", e)
            return None



