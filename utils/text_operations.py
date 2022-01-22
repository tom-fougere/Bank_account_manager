import os


def find_substring_with_dict(text, dictionary):

    value = None
    for key in dictionary:
        if key in text:
            value = dictionary[key]
            break
    return value


def remove_substring_with_list(text, list_substrings):

    for substring in list_substrings:
        text = text.replace(substring, '')
    return text


def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
