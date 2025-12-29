import pytest
import sys
from pathlib import Path
from syscore.fileutils import (
    resolve_path_and_filename_for_package,
    get_resolved_pathname,
)


@pytest.fixture()
def project_dir(request):
    module_path = Path(request.module.__file__)
    return str(module_path.parent.parent.parent.absolute())


@pytest.mark.skipif(sys.platform.startswith("win"), reason="Only runs on unix")
class TestFileUtilsUnix:
    def test_resolve_path_absolute(self):
        actual = get_resolved_pathname("/home/rob")
        assert actual == "/home/rob"

    def test_resolve_path_absolute_trailing(self):
        actual = get_resolved_pathname("/home/rob/")
        assert actual == "/home/rob"

    def test_resolve_path_absolute_dotted(self):
        actual = get_resolved_pathname(".home.rob")
        assert actual == "/home/rob"

    def test_resolve_path_relative(self, project_dir):
        actual = get_resolved_pathname("syscore.tests")
        assert actual == f"{project_dir}/syscore/tests"

    def test_resolve_path_non_existent(self, project_dir):
        actual = get_resolved_pathname("syscore.testz")
        assert actual == f"{project_dir}/syscore/testz"

    def test_resolve_path_and_filename_for_package(self):
        actual = resolve_path_and_filename_for_package("/home/rob/", "file.csv")
        assert actual == "/home/rob/file.csv"

        actual = resolve_path_and_filename_for_package("/home/rob/file.csv")
        assert actual == "/home/rob/file.csv"

        actual = resolve_path_and_filename_for_package(".home.rob.file.csv")
        assert actual == "/home/rob/file.csv"

    def test_path_and_filename_for_package_modules(self, project_dir):
        actual = resolve_path_and_filename_for_package("syscore.tests", "file.csv")
        assert actual == f"{project_dir}/syscore/tests/file.csv"

        actual = resolve_path_and_filename_for_package("syscore.tests.file.csv")
        assert actual == f"{project_dir}/syscore/tests/file.csv"

    @pytest.mark.xfail(reason="Cannot work with current implementation")
    def test_resolve_dotted_dir_name(self, tmp_path):
        directory = tmp_path / "dir.name.with.dots"
        directory.mkdir()
        file = directory / "hello.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = get_resolved_pathname(str(file))
        assert resolved_path == f"{tmp_path}/dir.name.with.dots/hello.txt"

    @pytest.mark.xfail(reason="Cannot work with current implementation")
    def test_resolve_resolve_path_and_filename_for_package_with_dotted_dir_name(
        self, tmp_path
    ):
        directory = tmp_path / "dir.name.with.dots"
        directory.mkdir()
        file = directory / "hello.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = resolve_path_and_filename_for_package(
            f"{tmp_path}/dir.name.with.dots", "hello.txt"
        )
        assert resolved_path == f"{tmp_path}/dir.name.with.dots/hello.txt"

    @pytest.mark.xfail(reason="Cannot work with current implementation")
    def test_resolve_dotted_file_name(self, tmp_path):
        directory = tmp_path / "dir_name"
        directory.mkdir()
        file = directory / "dotted.filename.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = get_resolved_pathname(str(file))
        assert resolved_path == f"{tmp_path}/dir_name/dotted.filename.txt"

    @pytest.mark.xfail(reason="Cannot work with current implementation")
    def test_resolve_resolve_path_and_filename_for_package_with_dotted_file_name(
        self, tmp_path
    ):
        directory = tmp_path / "dir_name"
        directory.mkdir()
        file = directory / "dotted.filename.txt"
        file.write_text("content", encoding="utf-8")
        resolved_path = resolve_path_and_filename_for_package(
            f"{tmp_path}/dir_name/dotted.filename.txt"
        )
        assert resolved_path == f"{tmp_path}/dir_name/dotted.filename.txt"


@pytest.mark.skipif(sys.platform in ["linux", "darwin"], reason="Only runs on windows")
class TestFileUtilsWindoze:
    def test_resolve_path_absolute(self):
        actual = get_resolved_pathname("C:\\home\\rob\\")
        assert actual == "C:\\home\\rob"

    def test_resolve_path_absolute_trailing(self):
        actual = get_resolved_pathname("C:\\home\\rob\\")
        assert actual == "C:\\home\\rob"

    def test_resolve_path_absolute_dotted(self):
        actual = get_resolved_pathname(".home.rob")
        assert actual == "\\home\\rob"

    def test_resolve_path_relative(self, project_dir):
        actual = get_resolved_pathname("syscore.tests")
        assert actual == f"{project_dir}\\syscore\\tests"

    def test_resolve_path_and_filename_for_package(self):
        actual = resolve_path_and_filename_for_package("C:\\home\\rob\\", "file.csv")
        assert actual == "C:\\home\\rob\\file.csv"

        actual = resolve_path_and_filename_for_package("C:\\home\\rob\\file.csv")
        assert actual == "C:\\home\\rob\\file.csv"

    def test_path_and_filename_for_package_modules(self, project_dir):
        actual = resolve_path_and_filename_for_package("syscore.tests", "file.csv")
        assert actual == f"{project_dir}\\syscore\\tests\\file.csv"

        actual = resolve_path_and_filename_for_package("syscore.tests.file.csv")
        assert actual == f"{project_dir}\\syscore\\tests\\file.csv"
