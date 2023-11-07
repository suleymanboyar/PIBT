import argparse
import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

acceptable_formats = [
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",  # Image formats
    ".mp4", ".mov", ".avi", ".mkv", ".wmv",  # Video formats
]

months = [
    "01-January", "02-February", "03-March",
    "04-April", "05-May", "06-June",
    "07-July", "08-August", "09-September",
    "10-October", "11-November", "12-December"
]

def days_type(value):
    if value.lower() == 'all':
        return 'all'
    try:
        days = int(value)
        if days < 0:
            raise argparse.ArgumentTypeError("Days argument must be a non-negative integer or 'all'.")
        return days
    except ValueError:
        raise argparse.ArgumentTypeError("Days argument must be a non-negative integer or 'all'.")


def dir_type(value):
    try:
        path = Path(value)
        if not path.is_dir():
            raise argparse.ArgumentTypeError(f"'{value}' is not a valid directory path")
        return path
    except TypeError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid directory path")


# Modified https://stackoverflow.com/a/33283187 to use the format base()
def safe_copy(file_path, out_dir, dst = None):
    """Safely copy a file to the specified directory. If a file with the same name already
    exists, the copied file name is altered to preserve both.

    :param str file_path: Path to the file to copy.
    :param str out_dir: Directory to copy the file into.
    :param str dst: New name for the copied file. If None, use the name of the original
        file.
    """
    name = dst or os.path.basename(file_path)
    if not os.path.exists(os.path.join(out_dir, name)):
        shutil.copy(file_path, os.path.join(out_dir, name))
    else:
        base, extension = os.path.splitext(name)
        i = 1
        while os.path.exists(os.path.join(out_dir, '{}({}){}'.format(base, i, extension))):
            i += 1
        shutil.copy(file_path, os.path.join(out_dir, '{}({}){}'.format(base, i, extension)))

def main():
    parser = argparse.ArgumentParser(description="Sort pictures and videos by year and month.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Add the source directory argument
    parser.add_argument("source_directory",
                    type=dir_type,
                    help="Directory containing pictures and videos")
    parser.add_argument("dest_directory",
                    type=dir_type,
                    help="Directory where pictures and videos will be copied over")
    parser.add_argument("-d", "--days",
                    type=days_type,
                    default=90,
                    help="Filter files older than N days (use 'all' to copy all files)")


    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        exit(1)


    args = parser.parse_args()

    # Use the arguments in your program
    source_directory = args.source_directory
    dest_parent_directory = args.dest_directory
    days_argument = args.days

    today = datetime.now()
    all_files = (p.resolve() for p in source_directory.glob("**/*") if p.suffix in acceptable_formats)
    for f in all_files:
        d = datetime.fromtimestamp(f.stat().st_mtime)
        delta = today - d
        if days_argument == 'all' or delta.days >= days_argument:
            dest = dest_parent_directory/f"{d.year}/{months[d.month]}"
            dest.mkdir(parents=True, exist_ok=True)
            safe_copy(f, dest)

if __name__ == "__main__":
    main()
