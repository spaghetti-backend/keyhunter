from typing import Final


#
# Settings
#
APP_NAME: Final = "keyhunter"
TYPING_SESSIONS_STORAGE_NAME: Final = "stat.db"
SETTINGS_STORAGE_NAME: Final = "settings.json"
DATASETS_STORAGE_PATH: Final = "keyhunter.content.datasets"
NATURAL_LANGUAGE_KEY: Final = "natural_language"
PROGRAMMING_LANGUAGE_KEY: Final = "programming_language"
SIMPLE_FILENAME: Final = "simple_text/simple"
COMMON_DIR: Final = "common"

THEME: Final = "nord"

SLE_WIDTH: Final = 70
SLE_MIN_WIDTH: Final = 50
SLE_MAX_WIDTH: Final = 120
SLE_WIDTH_STEPS: Final = 8
SLE_HEIGHT: Final = 1
SLE_MIN_HEIGHT: Final = 1
SLE_MAX_HEIGHT: Final = 1
SLE_START_FROM_CENTER: Final = True

SE_WIDTH: Final = 70
SE_MIN_WIDTH: Final = 50
SE_MAX_WIDTH: Final = 120
SE_WIDTH_STEPS: Final = 8
SE_HEIGHT: Final = 5
SE_MIN_HEIGHT: Final = 3
SE_MAX_HEIGHT: Final = 9
SE_HEIGHT_STEPS: Final = 4

WORDS_COUNT: Final = 50
MIN_WORDS_COUNT: Final = 20
MAX_WORDS_COUNT: Final = 100

KEYWORDS_COUNT: Final = 50
MIN_KEYWORDS_COUNT: Final = 20
MAX_KEYWORDS_COUNT: Final = 100
#
# Field keys
#
THEME_KEY: Final = "theme"
LANGUAGE_KEY: Final = "language"
TYPER_KEY: Final = "typer"
CONTENT_KEY: Final = "content"

ENGINE_KEY: Final = "engine"
BORDER_KEY: Final = "border"
SLE_KEY: Final = "single_line_engine"
SE_KEY: Final = "standard_engine"

WIDTH_KEY: Final = "width"
MIN_WIDTH_KEY: Final = "min_width"
MAX_WIDTH_KEY: Final = "max_width"

HEIGHT_KEY: Final = "height"
MIN_HEIGHT_KEY: Final = "min_height"
MAX_HEIGHT_KEY: Final = "max_height"

SLE_START_FROM_CENTER_KEY: Final = "start_from_center"

CONTENT_TYPE_KEY: Final = "content_type"
CATEGORY_KEY: Final = "category"
CONTENT_FILES_KEY: Final = "content_files"
COMMON_WORDS_KEY: Final = "common_words"
WORDS_COUNT_KEY: Final = "words_count"
WORDS_MIN_COUNT_KEY: Final = "min_words_count"
WORDS_MAX_COUNT_KEY: Final = "max_words_count"
KEYWORDS_COUNT_KEY: Final = "keywords_count"
KEYWORDS_MIN_COUNT_KEY: Final = "min_keywords_count"
KEYWORDS_MAX_COUNT_KEY: Final = "max_keywords_count"
# CONTENT_LENGHT_KEY: Final = "content_lenght"  #
CODE_SAMPLE_TYPE_KEY: Final = "sample_type"

CHAR_KEY: Final = "char"
TOTAL_KEY: Final = "total"
CORRECT_KEY: Final = "correct"
TOTAL_CHARS_KEY: Final = "total_chars"
CORRECT_CHARS_KEY: Final = "correct_chars"
ELAPSED_TIME_MS_KEY: Final = "elapsed_time_ms"
ACCURACY_KEY: Final = "accuracy"
SPEED_KEY: Final = "speed"
TYPING_SESSION_ID_KEY: Final = "typing_session_id"

#
# Keystrokes
#
MILLISECONDS_MULTIPLIER: Final = 1000
PERCENT_SCALE_2DP: Final = 10_000
FLOAT_TO_INT_SCALE_2DP: Final = 100

#
# Typer
#
BORDER_EXPANSION: Final = 2
