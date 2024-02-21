from message_processors.gngga_processor import GNGGAProcessor
from message_processors.device_registration import DeviceRegistrationProcessor
from message_processors.experiment_registration import ExperimentRegistrationProcessor
from message_processors.pvt_processor import NavPVTProcessor
from logger import setup_logger

logger = setup_logger(__name__, level="INFO")


def get_processor(message_data: dict):
    logger.debug("Creating processor for message: %s", message_data)
    if message_data.get("message_type") == "GNGGA":
        message_data.pop("message_type")
        return GNGGAProcessor(message_data)
    elif message_data.get("message_type") == "device_registration":
        message_data.pop("message_type")
        logger.info("Creating DeviceRegistrationProcessor with data: %s", message_data)
        return DeviceRegistrationProcessor(message_data)
    elif message_data.get("message_type") == "experiment_registration":
        message_data.pop("message_type")
        return ExperimentRegistrationProcessor(message_data)
    elif message_data.get("message_type") == "NAV-PVT":
        return NavPVTProcessor(message_data)
    else:
        raise ValueError(f"Unsupported message type: {message_data.get('message_type')}")

