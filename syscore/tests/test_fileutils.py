import pytest
import sys
import os
from syscore.fileutils import (
    resolve_path_and_filename_for_package,
    get_resolved_pathname,
)


@pytest.fixture()
def unix_project_dir(request):
    test_dir = os.path.dirname(request.module.__file__)
    project_dir = test_dir.replace("/syscore/tests", "")
    return project_dir


@pytest.fixture()
def win_project_dir(request):
    test_dir = os.path.dirname(request.module.__file__)
    project_dir = test_dir.replace("\\syscore\\tests", "")
    return project_dir


@pytest.fixture()
def platform():
    return sys.platform


class TestFileUtils:
    def test_resolve_path_absolute_unix(self, platform):
        if not sys.platform in ["linux", "darwin"]:
            pytest.skip("skipping linux/macos test")
        actual = get_resolved_pathname("/home/rob")
        assert actual == "/home/rob"

    def test_resolve_path_absolute_unix_trailing(self, platform):
        if not sys.platform in ["linux", "darwin"]:
            pytest.skip("skipping linux/macos test")
        actual = get_resolved_pathname("/home/rob/")
        assert actual == "/home/rob"

    def test_resolve_path_absolute_dotted_unix(self, platform):
        if not sys.platform in ["linux", "darwin"]:
            pytest.skip("skipping linux/macos test")
        actual = get_resolved_pathname(".home.rob")
        assert actual == "/home/rob"

    def test_resolve_path_absolute_windoze(self, platform):
        if not sys.platform.startswith("win"):
            pytest.skip("skipping windows-only test")
        actual = get_resolved_pathname("C:\\home\\rob\\")
        assert actual == "C:\\home\\rob"

    def test_resolve_path_relative_unix(self, unix_project_dir, platform):
        if not sys.platform in ["linux", "darwin"]:
            pytest.skip("skipping linux/macos test")
        actual = get_resolved_pathname("syscore.tests")
        assert actual == f"{unix_project_dir}/syscore/tests"

    def test_resolve_path_and_filename_for_package_unix(self, platform):
        if not sys.platform in ["linux", "darwin"]:
            pytest.skip("skipping linux/macos test")

        actual = resolve_path_and_filename_for_package("/home/rob/", "file.csv")
        assert actual == "/home/rob/file.csv"

        actual = resolve_path_and_filename_for_package("/home/rob/file.csv")
        assert actual == "/home/rob/file.csv"

        actual = resolve_path_and_filename_for_package(".home.rob.file.csv")
        assert actual == "/home/rob/file.csv"

    def test_resolve_path_and_filename_for_package_windoze(self, platform):
        if not sys.platform.startswith("win"):
            pytest.skip("skipping windows-only test")

        actual = resolve_path_and_filename_for_package("C:\\home\\rob\\", "file.csv")
        assert actual == "C:\\home\\rob\\file.csv"

        actual = resolve_path_and_filename_for_package("C:\home\\rob\\file.csv")
        assert actual == "C:\\home\\rob\\file.csv"

    def test_path_and_filename_for_package_modules_unix(
        self, unix_project_dir, platform
    ):
        if not sys.platform in ["linux", "darwin"]:
            pytest.skip("skipping linux/macos test")

        actual = resolve_path_and_filename_for_package("syscore.tests", "file.csv")
        assert actual == f"{unix_project_dir}/syscore/tests/file.csv"

        actual = resolve_path_and_filename_for_package("syscore.tests.file.csv")
        assert actual == f"{unix_project_dir}/syscore/tests/file.csv"

    def test_path_and_filename_for_package_modules_windoze(
        self, win_project_dir, platform
    ):
        if not sys.platform.startswith("win"):
            pytest.skip("skipping windows-only test")

        actual = resolve_path_and_filename_for_package("syscore.tests", "file.csv")
        assert actual == f"{win_project_dir}\\syscore\\tests\\file.csv"

        actual = resolve_path_and_filename_for_package("syscore.tests.file.csv")
        assert actual == f"{win_project_dir}\\syscore\\tests\\file.csv"
