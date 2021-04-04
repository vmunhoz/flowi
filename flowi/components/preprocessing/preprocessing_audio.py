import io

# import librosa
import numpy as np
import pandas as pd
# from pydub import AudioSegment
from tqdm import tqdm

from flowi.components.preprocessing.preprocessing_base import PreprocessingBase
from flowi.components.preprocessing.preprocessing_utils import PreprocessingUtils
from flowi.utilities.logger import Logger


class PreprocessingAudio(PreprocessingBase):

    def __init__(self):
        logger = Logger(logger_name=__name__)
        super().__init__(logger=logger)

        self._preprocessing_utils = PreprocessingUtils()

    # def mel_spectrogram(self, input_variable_df: dd.DataFrame, data_column_name: str, output_column_name: str,
    #                     n_mels: int = 20, fmax: int = 8000, dct_type: int = 2,
    #                     returning_mels: list = [0], merge_policy: str or None = 'sum') -> dd.DataFrame:
    #
    #     @pandas_udf(spark_types.ArrayType(spark_types.DoubleType()), PandasUDFType.SCALAR)
    #     def mel_spectrogram_udf(binaries):
    #         audio_list = []
    #         for binary in tqdm(binaries):
    #             sound = AudioSegment.from_file(io.BytesIO(binary))
    #             sound = sound.set_frame_rate(8000)
    #             sound = sound.set_channels(1)
    #             sr = sound.frame_rate
    #             samples = sound.get_array_of_samples()
    #             signal = np.array(samples).astype(np.float32)
    #             signal = signal / sound.max_possible_amplitude
    #             mel_spectrogram = librosa.feature.melspectrogram(y=signal, sr=sr, n_mels=n_mels, fmax=fmax)
    #             mfcc = librosa.feature.mfcc(S=librosa.power_to_db(mel_spectrogram), dct_type=dct_type)
    #             mfcc = mfcc.T
    #             feature = mfcc[:, returning_mels]
    #
    #             if merge_policy == 'sum':
    #                 feature = np.sum(feature, axis=1)
    #
    #             self._logger.debug('Returning MFCC: {}'.format(feature))
    #
    #             audio_list.append(feature)
    #
    #         return pd.Series(audio_list)
    #
    #     df = input_variable_df.withColumn(output_column_name, mel_spectrogram_udf(col(data_column_name)))
    #     return df.cache()
    #
    # def split_sound_by_threshold(self, input_variable_df: DataFrame,output_column_name: str, data_column_name: str,
    #                              label_column: str, threshold: int = -170, min_window: int = 10) -> DataFrame:
    #
    #     @pandas_udf(spark_types.ArrayType(spark_types.ArrayType(spark_types.DoubleType())))
    #     def split_sound_by_threshold_udf(audios):
    #         audio_list = []
    #         for audio in tqdm(audios):
    #             signals = []
    #             init = None
    #             final = None
    #             signal_is_raising = -1
    #
    #             for i, f in enumerate(audio):
    #                 if (signal_is_raising == -1) and f > threshold:
    #                     signal_is_raising = 1
    #                     init = i
    #                 elif (signal_is_raising == 1) and f < threshold and i - init > min_window:
    #                     signal_is_raising = -1
    #                     final = i + 1
    #                     signals.append(audio[init:final])
    #                     self._logger.debug('Signals init: {}, final: {}'.format(init, final))
    #                     init = final = None
    #
    #             if init is not None and final is None:
    #                 signals.append(audio[init:final])
    #                 self._logger.debug('Signals init: {}, final: {}'.format(init, final))
    #
    #             audio_list.append(signals)
    #
    #         return pd.Series(audio_list)
    #
    #     df = input_variable_df.withColumn(output_column_name, split_sound_by_threshold_udf(col(data_column_name)))
    #
    #     if label_column:
    #         df = self._preprocessing_utils.explode_columns(input_variable_df=df,
    #                                                        columns_to_explode=[label_column, output_column_name],
    #                                                        output_column_names=[label_column, output_column_name])
    #     else:
    #         df = df.withColumn(output_column_name, explode(col(output_column_name)))
    #
    #     return df
