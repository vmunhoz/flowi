from pyspark.sql import DataFrame
from pyspark.sql.functions import substring_index, split, col, regexp_replace, explode

from components.preprocessing.preprocessing_base import PreprocessingBase
from utilities.audit import Audit


class PreprocessingString(PreprocessingBase):

    def __init__(self):
        audit = Audit(class_name=__name__)
        super().__init__(audit=audit)

    def replace_string(self, input_variable_df: DataFrame, output_column_name: str, data_column_name: str,
                       pattern: str, replacement: str) -> DataFrame:
        self._audit.debug(f"Replacing regex pattern {pattern} by {replacement}."
                          f"In column {data_column_name} Out column {output_column_name}")

        return input_variable_df.withColumn(output_column_name,
                                            regexp_replace(col(data_column_name), pattern, replacement))

    def substring(self, input_variable_df: DataFrame, output_column_name: str, data_column_name: str, delimiter: str,
                  count: int) -> DataFrame:
        self._audit.debug(f"Substring delimiter {delimiter} count {count}")

        return input_variable_df.withColumn(output_column_name,
                                            substring_index(col(data_column_name), delimiter, count))

    def split(self, input_variable_df: DataFrame, output_column_name: str, data_column_name: str, explode_split: str,
              pattern: str, limit: int) -> DataFrame:
        self._audit.debug(f"Substring delimiter {pattern} count {limit}")

        df = input_variable_df.withColumn(output_column_name, split(col(data_column_name), pattern, limit))
        if explode_split == "true":
            df = df.withColumn(output_column_name, explode(col(output_column_name)))

        return df
