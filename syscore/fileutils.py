import glob
import datetime
import time
import os
import re
from pathlib import Path, PurePath
from typing import List, Tuple, TextIO

from syscore import PYSYS_PROJECT_DIR
from syscore.dateutils import SECONDS_PER_DAY


"""

    FILE RENAMING AND DELETING

"""


def rename_files_with_extension_in_pathname_as_archive_files(
    pathname: str, extension: str = ".txt", archive_extension: str = ".arch"
) -> None:
    """
    Find all the files with a particular extension in a directory, and rename them
     eg thing.txt will become thing_yyyymmdd.txt where yyyymmdd is todays date

    """

    resolved_pathname = get_resolved_pathname(pathname)
    list_of_files = files_with_extension_in_resolved_pathname(
        resolved_pathname, extension=extension
    )

    for filename in list_of_files:
        full_filename = os.path.join(resolved_pathname, filename)
        rename_file_as_archive(
            full_filename, old_extension=extension, archive_extension=archive_extension
        )


def rename_file_as_archive(
    full_filename: str, old_extension: str = ".txt", archive_extension: str = ".arch"
) -> None:
    """
    Rename a file with archive suffix and extension
     eg thing.txt will become thing_yyyymmdd.arch where yyyymmdd is todays date

    """

    old_filename = "%s%s" % (full_filename, old_extension)
    date_label = datetime.datetime.now().strftime("%Y%m%d")
    new_filename = "%s_%s%s" % (full_filename, date_label, archive_extension)

    os.rename(old_filename, new_filename)


def delete_old_files_with_extension_in_pathname(
    pathname: str, days_old: int = 30, extension: str = ".arch"
) -> None:
    """
    Find all the files with a particular extension in a directory, and delete them
    if older than x days

    """

    resolved_pathname = get_resolved_pathname(pathname)
    list_of_files = glob.glob(resolved_pathname + "/**/*" + extension, recursive=True)

    for filename in list_of_files:
        delete_file_if_too_old(filename, days_old=days_old)


def delete_file_if_too_old(full_filename_with_ext: str, days_old: int = 30) -> None:
    file_age = get_file_or_folder_age_in_days(full_filename_with_ext)
    if file_age > days_old:
        print("Deleting %s" % full_filename_with_ext)
        os.remove(full_filename_with_ext)


def get_file_or_folder_age_in_days(full_filename_with_ext: str) -> float:
    # time will be in UNIX seconds
    file_time = os.stat(full_filename_with_ext).st_ctime
    time_now = time.time()

    age_seconds = time_now - file_time
    age_days = age_seconds / SECONDS_PER_DAY

    return age_days


"""

    FILENAME RESOLUTION

"""


def resolve_path_and_filename_for_package(
    path_and_filename: str, separate_filename: str | None = None
) -> str:
    """
    A way of resolving relative and absolute filenames, and dealing with awkward OS specific things

    >>> resolve_path_and_filename_for_package("/home/rob/", "file.csv")
    '/home/rob/file.csv'

    >>> resolve_path_and_filename_for_package(".home.rob", "file.csv")
    '/home/rob/file.csv'

    >>> resolve_path_and_filename_for_package('C:\\home\\rob\\'', "file.csv")
    'C:\\home\\rob\\file.csv'

    >>> resolve_path_and_filename_for_package("syscore.tests", "file.csv")
    '/home/rob/pysystemtrade/syscore/tests/file.csv'

    >>> resolve_path_and_filename_for_package("/home/rob/file.csv")
    '/home/rob/file.csv'

    >>> resolve_path_and_filename_for_package(".home.rob.file.csv")
    '/home/rob/file.csv'

    >>> resolve_path_and_filename_for_package("C:\\home\\rob\\file.csv")
    'C:\\home\\rob\\file.csv'

    >>> resolve_path_and_filename_for_package("syscore.tests.file.csv")
    '/home/rob/pysystemtrade/syscore/tests/file.csv'

    """

    path_and_filename_as_list = _transform_path_into_list(path_and_filename)
    if separate_filename is None:
        (
            path_as_list,
            separate_filename,
        ) = _extract_filename_from_combined_path_and_filename_list(
            path_and_filename_as_list
        )
    else:
        path_as_list = path_and_filename_as_list

    absolute_path = _make_absolute(path_as_list)
    result = absolute_path / separate_filename

    return str(result)


def get_resolved_pathname(pathname: str) -> str:
    """
    >>> get_resolved_pathname("/home/rob/")
    '/home/rob'

    >>> get_resolved_pathname(".home.rob")
    '/home/rob'

    >>> get_resolved_pathname('C:\\home\\rob\\'')
    'C:\\home\\rob'

    >>> get_resolved_pathname("syscore.tests")
    '/home/rob/pysystemtrade/syscore/tests'

    """

    if isinstance(pathname, Path) and pathname.exists():
        # special case when already a Path
        return str(pathname.absolute())
    else:
        pathname = str(pathname)
        if "@" in pathname or "::" in pathname:
            # This is an ssh address for rsync - don't change
            return pathname

        path_as_list = _transform_path_into_list(pathname)
        result = _make_absolute(path_as_list)

        return str(result)


## something unlikely to occur naturally in a pathname
RESERVED_CHARACTERS = "&!*"


def _make_absolute(path_as_list: list[str]) -> PurePath:
    # handle absolute unix
    if path_as_list[0] == "":
        path_as_list[0] = os.sep
    # handle absolute windows
    if re.match("[A-Za-z]:$", path_as_list[0]):
        path_as_list[0] = f"{path_as_list[0]}{os.sep}"
    path_obj = PurePath(*path_as_list)
    if not path_obj.is_absolute():
        path_obj = PYSYS_PROJECT_DIR / path_obj

    return path_obj


def _transform_path_into_list(pathname: str) -> List[str]:
    """
    >>> _transform_path_into_list("/home/rob/test.csv")
    ['', 'home', 'rob', 'test', 'csv']

    >>> _transform_path_into_list("/home/rob/")
    ['', 'home', 'rob']

    >>> _transform_path_into_list(".home.rob")
    ['', 'home', 'rob']

    >>> _transform_path_into_list('C:\\home\\rob\\'')
    ['C:', 'home', 'rob']

    >>> _transform_path_into_list('C:\\home\\rob\\test.csv')
    ['C:', 'home', 'rob', 'test', 'csv']

    >>> _transform_path_into_list("syscore.tests.fileutils.csv")
    ['syscore', 'tests', 'fileutils', 'csv']

    >>> _transform_path_into_list("syscore.tests")
    ['syscore', 'tests']

    """

    pathname_replace = _add_reserved_characters_to_pathname(pathname)
    path_as_list = pathname_replace.rsplit(RESERVED_CHARACTERS)

    if path_as_list[-1] == "":
        path_as_list.pop()

    return path_as_list


def _add_reserved_characters_to_pathname(pathname: str) -> str:
    pathname_replace = pathname.replace(".", RESERVED_CHARACTERS)
    pathname_replace = pathname_replace.replace("/", RESERVED_CHARACTERS)
    pathname_replace = pathname_replace.replace("\\", RESERVED_CHARACTERS)

    return pathname_replace


def _extract_filename_from_combined_path_and_filename_list(
    path_and_filename_as_list: list[str],
) -> Tuple[list[str], str]:
    """
    >>> _extract_filename_from_combined_path_and_filename_list(['home', 'rob','file', 'csv'])
    (['home', 'rob'], 'file.csv')
    """
    ## need -2 because want extension
    extension = path_and_filename_as_list.pop()
    filename = path_and_filename_as_list.pop()

    separate_filename = ".".join([filename, extension])

    return path_and_filename_as_list, separate_filename


"""

    HTML

"""


def write_list_of_lists_as_html_table_in_file(
    file: TextIO, list_of_lists: list[str]
) -> None:
    file.write("<table>")
    for sublist in list_of_lists:
        file.write("  <tr><td>")
        file.write("    </td><td>".join(sublist))
        file.write("  </td></tr>")

    file.write("</table>")


def files_with_extension_in_pathname(
    pathname: str, extension: str = ".csv"
) -> List[str]:
    """
    Find all the files with a particular extension in a directory

    """
    resolved_pathname = get_resolved_pathname(pathname)

    return files_with_extension_in_resolved_pathname(
        resolved_pathname, extension=extension
    )


def files_with_extension_in_resolved_pathname(
    resolved_pathname: str, extension: str = ".csv"
) -> List[str]:
    """
    Find all the files with a particular extension in a directory
    """

    file_list = [
        os.path.basename(f) for f in glob.glob(f"{resolved_pathname}/*{extension}")
    ]
    file_list_no_extension = [filename.split(".")[0] for filename in file_list]

    return file_list_no_extension


def full_filename_for_file_in_home_dir(filename: str) -> str:
    return str(Path.home() / filename)


def does_filename_exist(filename: str) -> bool:
    resolved_filename = resolve_path_and_filename_for_package(filename)
    file_exists = does_resolved_filename_exist(resolved_filename)
    return file_exists


def does_resolved_filename_exist(resolved_filename: str) -> bool:
    return Path(resolved_filename).exists()
