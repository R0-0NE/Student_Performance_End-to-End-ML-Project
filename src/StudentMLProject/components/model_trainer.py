import numpy as np
import os
import sys
from dataclasses import dataclass
from urllib.parse import urlparse
from catboost import CatBoostRegressor
from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
import mlflow
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error,mean_squared_error
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.StudentMLProject.exception import CustomException
from src.StudentMLProject.logger import logging
from src.StudentMLProject.utils import evaluate_model,save_object

@dataclass
class ModelTrainerConfig:
    trained_model_file_path=os.path.join('artifacts',"model.pkl")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config=ModelTrainerConfig()

    def eval_metrics(self,actual,pred):
        rmse=np.sqrt(mean_squared_error(actual,pred))
        mae=mean_absolute_error(actual,pred)
        r2=r2_score(actual,pred)
        return rmse,mae,r2
    
    def initiate_model_trainer(self,train_array,test_array):
        try:
            logging.info("Split train test data")
            X_train, y_train, X_test,y_test =(
                train_array[:,:-1],
                train_array[:,-1],
                test_array[:,:-1],
                test_array[:,-1]

            )
            models = {
                    "Linear Regression": LinearRegression(),
                    "Gradient Boosting": GradientBoostingRegressor(),
                    ##"Lasso": Lasso(),
                    ##"Ridge": Ridge(),
                    ##"K-Neighbors Regressor": KNeighborsRegressor(),
                    "Decision Tree": DecisionTreeRegressor(),
                    "Random Forest Regressor": RandomForestRegressor(),
                    "XGBRegressor": XGBRegressor(), 
                    "CatBoosting Regressor": CatBoostRegressor(verbose=False),
                    "AdaBoost Regressor": AdaBoostRegressor(),
                }
            params={
                "Decision Tree":{
                    'criterion':['squared_error','friedman_mse','absolute_error','poisson']
                },
                "Random Forest Regressor":{
                    'n_estimators':[8,16,32,64,128,256]
                },
                "Gradient Boosting":{
                    'learning_rate':[.1,.01,.05,.001],
                    'subsample':[0.6,0.7,0.75,0.8,0.85,0.9],
                    'n_estimators':[8,16,32,64,128,256]
                },
                "Linear Regression":{},
                "XGBRegressor":{
                    'learning_rate':[.1,.01,.05,.001],
                    'n_estimators':[8,16,32,64,128,256]
                },
                "CatBoosting Regressor":{
                    'depth':[6,8,10],
                    'learning_rate':[.1,.01,.05,.001],
                    'iterations':[30,50,10]
                },
                "AdaBoost Regressor":{
                    'learning_rate':[.1,.01,.05,.001],
                    'n_estimators':[8,16,32,64,128,256]
                }
            }
            model_report:dict=evaluate_model(X_train,y_train,X_test,y_test,models,params)
            ## to get best model score from dict
            best_model_score=max(sorted(model_report.values()))

            ##to get best model name from dict
            best_model_name=list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model=models[best_model_name]

            print("This is the best model:")
            print(best_model_name)

            model_names=list(params.keys())

            actual_model=""

            for model in model_names:
                if best_model_name==model:
                    actual_model = actual_model + model

            best_params= params[actual_model]
            
            ## ML flow
            mlflow.set_registry_uri("https://dagshub.com/R0-0NE/Student_Performance_End-to-End-ML-Project.mlflow")
            tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

            with mlflow.start_run():
                predicted_qualities = best_model.predict(X_test)

                (rmse,mae,r2)=self.eval_metrics(y_test,predicted_qualities)

                mlflow.log_params(best_params)

                mlflow.log_metric("rmse",rmse)
                mlflow.log_metric("r2",r2)
                mlflow.log_metric("mae",mae)


                #model registry doesnt work with file store
                if tracking_url_type_store != "file":

                    #there are other ways to use model registry
                    mlflow.sklearn.log_model(best_model,"model",registered_model_name=actual_model)
                else:
                    mlflow.sklearn.log_model(best_model,"model")




            if best_model_score<0.6:
                raise CustomException("No best model found")
            logging.info(f"best found model on both training & testing dataset")

            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )
            predicted=best_model.predict(X_test)

            r2_square=r2_score(y_test,predicted)
            return r2_square

        except Exception as e:
            raise CustomException(e,sys)
        
        