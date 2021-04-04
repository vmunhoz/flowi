from flowi.components.load.base_loader import BaseLoader
from flowi.utilities.logger import Logger


class LoadLocal(BaseLoader):

    def __init__(self):
        super().__init__()
        self._audit = Logger(logger_name=__name__)

    def load_file(self, path: str, file_type: str):
        self._audit.debug('Loading files from directory: {}'.format(path))

        return self.load(file_type=file_type)(path)
