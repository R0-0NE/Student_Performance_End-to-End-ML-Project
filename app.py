#from src.StudentMLProject.logger import logging
import sys
import os

# Add the 'src' directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from StudentMLProject.logger import logging
from StudentMLProject.exception import CustomException
from StudentMLProject.components.data_ingestion import DataIngestion
from StudentMLProject.components.data_ingestion import DataIngestionConfig
from src.StudentMLProject.components.data_transformation import DataTransformationConfig,DataTransformation

if __name__=="__main__":
    logging.info("The Execution has started")

    try:
        #data_ingestion_config=DataIngestionConfig()
        data_ingestion=DataIngestion()
        train_data_path,test_data_path=data_ingestion.initiate_data_ingestion()
        
        #data_transformation_config=DataTransformationConfig()
        data_transformation=DataTransformation()
        data_transformation.initiate_data_transformation(train_data_path,test_data_path)
        
    except Exception as e:
        logging.info("Custom Exception")
        raise CustomException(e,sys)