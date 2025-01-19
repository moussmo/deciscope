# logging_config.py
import logging

# Configure the root logger
logging.basicConfig(
    level=logging.DEBUG,  # Adjust as needed: DEBUG, INFO, WARNING, etc.
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),   # Log to a file
        logging.StreamHandler()          # Log to the console
    ]
)