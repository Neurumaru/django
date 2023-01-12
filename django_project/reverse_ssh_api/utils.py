def map_dictionary_keys(dictionary: dict, mapping: dict) -> dict:
    return dict((mapping[key], value) if key in mapping else (key, value) for (key, value) in dictionary.items())
