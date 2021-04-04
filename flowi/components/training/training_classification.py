import os
from pyspark.ml.classification import DecisionTreeClassifier, DecisionTreeClassificationModel
from pyspark.sql import DataFrame

from components.component_base import ComponentBase
from components.preprocessing.preprocessing_utils import PreprocessingUtils
from utilities import df_utils
from utilities.audit import Audit


class TrainingClassification(ComponentBase):

    def __init__(self):
        self._audit = Audit(class_name=__name__)

        self._preprocessing_utils = PreprocessingUtils()

    @staticmethod
    def _save_model(model, model_name: str):
        models_folder = 'saved_models/'
        if not os.path.isdir(models_folder):
            os.mkdir(models_folder)
        model.write().overwrite().save(os.path.join(models_folder, model_name))

    def decision_tree(self, input_variable_df: DataFrame, data_column_name: str, output_column_name: str,
                      label_column_name: str) -> DataFrame:
        self._audit.debug("Running SVM")

        if str(input_variable_df.schema[label_column_name].dataType) == "StringType":
            input_variable_df = df_utils.convert_string_to_categorical(df=input_variable_df,
                                                                       input_column=label_column_name)

        decision_tree = DecisionTreeClassifier(featuresCol=data_column_name, labelCol=label_column_name,
                                               predictionCol=output_column_name)
        model = decision_tree.fit(input_variable_df)
        self._save_model(model=model, model_name='decision_tree')

        df = model.transform(input_variable_df)

        return df.cache()
