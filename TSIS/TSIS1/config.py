from configparser import ConfigParser
from pathlib import Path


def load_config(filename='database.ini', section='postgresql'):
    """Read database connection parameters from *filename* and return a dict.
    
    Looks for the file next to config.py itself, so it works regardless of
    which directory you run the script from.
    """
    # Resolve path relative to this file's directory
    base_dir = Path(__file__).parent
    filepath = base_dir / filename

    parser = ConfigParser()
    parser.read(filepath, encoding='utf-8')

    if not parser.has_section(section):
        raise Exception(
            f'Section [{section}] not found in {filepath}\n'
            f'Make sure database.ini exists in: {base_dir}'
        )

    return dict(parser.items(section))


if __name__ == '__main__':
    print(load_config())
