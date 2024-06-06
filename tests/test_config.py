import os
import pathlib
import unittest
from unittest import mock

from mightstone.config import SettingsSourceGenerator


class TestSettingsSourceGenerator(unittest.TestCase):
    def test_paths_search_toml(self):
        paths = SettingsSourceGenerator().candidate_paths()

        files = [path for path in paths if str(path).endswith(".toml")]
        self.assertTrue(any(files))
        self.assertEqual(paths.index(files[0]), 3)  # fourth priority

    def test_paths_search_yaml(self):
        paths = SettingsSourceGenerator().candidate_paths()
        files = [path for path in paths if str(path).endswith(".yaml")]
        self.assertTrue(any(files))
        self.assertEqual(paths.index(files[0]), 0)  # first priority

    def test_paths_search_yml(self):
        paths = SettingsSourceGenerator().candidate_paths()
        files = [path for path in paths if str(path).endswith(".yml")]
        self.assertTrue(any(files))
        self.assertEqual(paths.index(files[0]), 1)  # second priority

    def test_paths_search_json(self):
        paths = SettingsSourceGenerator().candidate_paths()
        files = [path for path in paths if str(path).endswith(".json")]
        self.assertTrue(any(files))
        self.assertEqual(paths.index(files[0]), 2)  # third priority

    @mock.patch.dict(os.environ, {"MIGHTSTONE_CONFIG_FILE": "/path/to/my/config.toml"})
    def test_paths_contains_only_env_var(self):
        paths = SettingsSourceGenerator().candidate_paths()

        self.assertEqual([pathlib.Path("/path/to/my/config.toml")], paths)

    def test_app_name_is_slugified(self):
        self.assertEqual("foo_du_fafa", SettingsSourceGenerator("foo du fafa").app_name)
        self.assertEqual("foo", SettingsSourceGenerator("FoO").app_name)
        self.assertEqual("foo_bar", SettingsSourceGenerator("foo-bar").app_name)

    @mock.patch.dict(os.environ, {"FOO_DU_FAFA_CONFIG_FILE": "/path/to/my/config.toml"})
    def test_paths_contains_only_env_var_with_specific_name(self):
        paths = SettingsSourceGenerator("foo du fafa").candidate_paths()

        self.assertEqual([pathlib.Path("/path/to/my/config.toml")], paths)
