from components.preprocessing.preprocessing_base import PreprocessingBase
from utilities.audit import Audit


class PreprocessingLabels(PreprocessingBase):

    def __init__(self):
        audit = Audit(class_name=__name__)
        super().__init__(audit=audit)

    @staticmethod
    def _split_labels_from_string(data: tuple, label: str, separator: str = ','):
        return data, label.split(separator)
