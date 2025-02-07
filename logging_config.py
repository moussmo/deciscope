import logging
from utils.utils import get_today

logging.basicConfig(
    level=logging.INFO,  
    filename="logs_{}.txt".format(get_today().replace(' ', '')),
    format="%(asctime)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  
        logging.StreamHandler()         
    ]
)