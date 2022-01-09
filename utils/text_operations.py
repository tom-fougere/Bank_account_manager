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
