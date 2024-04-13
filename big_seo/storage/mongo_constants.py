import os
DEFAULT_WEB_PAGES_COLLECTION = 'web_pages' if os.getenv(
    'DEFAULT_WEB_PAGES_COLLECTION') is None else os.getenv('DEFAULT_WEB_PAGES_COLLECTION')
DEFAULT_DB = 'web_pages' if os.getenv(
    'DEFAULT_DB') is None else os.getenv('DEFAULT_DB')
