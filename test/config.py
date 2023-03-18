"""Configuration of tests, mainly relating to test assets."""

import pathlib

_HERE = pathlib.Path(__file__).parent
_EXAMPLES_FOLDER = _HERE.joinpath('examples')

TEST_CONFIG_PATH = _EXAMPLES_FOLDER.joinpath('maildaemon_test_config.json')

TEST_MESSAGE_1_PATH = _EXAMPLES_FOLDER.joinpath('message1.txt')
TEST_MESSAGE_2_PATH = _EXAMPLES_FOLDER.joinpath('message2.txt')

TEST_MESSAGE_PATHS = [TEST_MESSAGE_1_PATH, TEST_MESSAGE_2_PATH]
