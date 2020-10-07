from ftfy import fix_text
import pathlib


def better_fix_text(text):
    """
    Fix problems with data encoding.

    Parameters
    ----------
    text: str
        Text to fix
    Returns
    -------
    Text with fixed encoding.

    Notes
    -----
    Uses fix_text and then fix problems with letter "Ż".
    """
    text = fix_text(text)
    if text.find("Å»") != -1:
        return text.replace("Å»", "Ż")
    else:
        return text


def check_if_path(path):
    """
    Check if path type is pathlib.Path, if not converts it to this type.

    Parameters
    ----------
    path: pathlib.Path or path-like
        Path to convert.

    Returns
    -------
    pathlib.Path
        Converted path.
    """
    if not isinstance(path, pathlib.Path):
        try:
            path = pathlib.Path(path)
        except TypeError:
            print("Wrong path type.")
    return path
