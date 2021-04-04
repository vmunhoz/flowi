from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql import DataFrame

from components.component_base import ComponentBase
from components.preprocessing.preprocessing_utils import PreprocessingUtils
from utilities.audit import Audit


class Evaluation(ComponentBase):

    def __init__(self):
        self._audit = Audit(class_name=__name__)

        self._preprocessing_utils = PreprocessingUtils()

    def f1(self, input_variable_df: DataFrame, output_column_name: str,
           label_column_name: str) -> float:
        self._audit.debug("Computing F1 score")
        input_variable_df = input_variable_df.select([output_column_name, label_column_name])

        evaluator = MulticlassClassificationEvaluator(predictionCol=output_column_name, labelCol=label_column_name)
        f1_score = evaluator.evaluate(input_variable_df, {evaluator.metricName: "f1"})

        return f1_score
