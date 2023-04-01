import os
import pathlib
import unittest
from unittest import mock

from mightstone.config import MainSettings


class TestConfig(unittest.TestCase):
    def test_paths_search_toml(self):
        paths = MainSettings.__config__.candidate_paths()

        files = [path for path in paths if str(path).endswith(".toml")]
        self.assertTrue(any(files))
        self.assertEqual(paths.index(files[0]), 3)  # fourth priority

    def test_paths_search_yaml(self):
        paths = MainSettings.__config__.candidate_paths()
        files = [path for path in paths if str(path).endswith(".yaml")]
        self.assertTrue(any(files))
        self.assertEqual(paths.index(files[0]), 0)  # first priority

    def test_paths_search_yml(self):
        paths = MainSettings.__config__.candidate_paths()
        files = [path for path in paths if str(path).endswith(".yml")]
        self.assertTrue(any(files))
        self.assertEqual(paths.index(files[0]), 1)  # second priority

    def test_paths_search_json(self):
        paths = MainSettings.__config__.candidate_paths()
        files = [path for path in paths if str(path).endswith(".json")]
        self.assertTrue(any(files))
        self.assertEqual(paths.index(files[0]), 2)  # third priority

    @mock.patch.dict(os.environ, {"MIGHTSTONE_CONFIG_FILE": "/path/to/my/config.toml"})
    def test_paths_contains_only_env_var(self):
        paths = MainSettings.__config__.candidate_paths()

        self.assertEqual([pathlib.Path("/path/to/my/config.toml")], paths)
