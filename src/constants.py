from pathlib import Path

MAIN_DOC_URL = "https://docs.python.org/3/"
PEP_DOC_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

# Шаблон для поиска версии и статуса для функции latest_versions:
PATTERN = r"Python (?P<version>\d\.\d+) \((?P<status>.*)\)"

# заголовки отчета для функции whats_new:
WHATS_NEW = ('Ссылка на статью', 'Заголовок', 'Редактор, Автор')

# заголовки отчета для функции latest_versions:
LATEST_VERSIONS = ('Ссылка на документацию', 'Версия', 'Статус')

# заголовки отчета для функции pep:
PEP = ['Статус', 'Количество']
