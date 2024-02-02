from message_processors.gngga_processor import GNGGAProcessor

def get_processor(message_data: dict):
    if message_data.get("message_type") == "GNGGA":
        return GNGGAProcessor(message_data)
    # Add other conditions for different message types
    else:
        raise ValueError("Unsupported message type")
