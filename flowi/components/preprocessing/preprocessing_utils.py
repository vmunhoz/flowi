import numpy as np
import pandas as pd


from flowi.components.preprocessing.preprocessing_base import PreprocessingBase
from flowi.utilities.logger import Logger
import dask.dataframe as dd

# from flowi.utilities import df_utils


class PreprocessingUtils(PreprocessingBase):

    def __init__(self):
        logger = Logger(logger_name=__name__)
        super().__init__(logger=logger)

    def explode_columns(self, input_variable_df: pd.DataFrame, columns_to_explode: list,
                        output_column_names: list) -> dd.DataFrame:

        self._logger.debug(f"Exploding columns {columns_to_explode} to {output_column_names}.")

        df = input_variable_df.withColumn("tmp", arrays_zip(*columns_to_explode)).withColumn("tmp", explode("tmp"))
        df = df_utils.flatten_df(df)

        for column_to_explode, output_column_name in zip(columns_to_explode, output_column_names):
            if column_to_explode == output_column_name:
                df = df.drop(column_to_explode)

            df = df.withColumnRenamed('tmp_' + column_to_explode, output_column_name)

        return df

    @staticmethod
    def _scale(scaler, input_variable_df: dd.DataFrame) -> dd.DataFrame:

        scaler_model = scaler.fit(input_variable_df)
        df = scaler_model.transform(input_variable_df)

        return df

    def min_max_scaler(self, input_variable_df: dd.DataFrame,output_column_name: str, data_column_name: str) -> dd.DataFrame:
        self._logger.debug(f"MinMaxScaling")

        scaler = MinMaxScaler(inputCol=data_column_name, outputCol=output_column_name)
        scaler_model = scaler.fit(input_variable_df)
        df = scaler_model.transform(input_variable_df)

        return df

    def robust_scaler(self, input_variable_df: dd.DataFrame, output_variable_name_for_df: str,
                      output_column_name: str, data_column_name: str) -> dict:
        self._logger.debug(f"MinMaxScaling")

        scaler = RobustScaler(inputCol=data_column_name, outputCol=output_column_name, lower=0.25, upper=0.75,
                              withCentering=False, withScaling=True, relativeError=0.001)
        scaler_model = scaler.fit(input_variable_df)
        df = scaler_model.transform(input_variable_df)

        return df

    def scale(self, input_variable_df: dd.DataFrame, output_column_name: str, data_column_name: str,
              scale_method: str) -> dd.DataFrame:

        self._logger.debug(f"Scaling using {scale_method}")

        scale_chooser = {
            'min_max': self.min_max_scaler,
            'robust': self.robust_scaler
        }

        if str(input_variable_df.schema[data_column_name].dataType) != "VectorUDT":
            input_variable_df = df_utils.convert_column_to_vector(df=input_variable_df,
                                                                  data_column_name=data_column_name)

        return scale_chooser[scale_method](input_variable_df=input_variable_df,
                                           output_column_name=output_column_name,
                                           data_column_name=data_column_name)

    # def pad(self, input_variable_df: DataFrame, output_column_name: str, data_column_name: str, length: int,
    #         pad_number: int) -> DataFrame:
    #
    #     self._logger.debug(f"Padding with {pad_number} to length {length}")
    #
    #     @pandas_udf(spark_types.ArrayType(spark_types.DoubleType()), PandasUDFType.SCALAR)
    #     def pad(signals: pd.Series) -> pd.Series:
    #         padded_signals = []
    #         for signal in signals:
    #             padded_signals.append(np.concatenate((signal[:length], [pad_number] * (length - len(signal))), axis=0))
    #
    #         return pd.Series(padded_signals)
    #
    #     df = input_variable_df.withColumn(output_column_name, pad(col(data_column_name)))
    #
    #     return df
