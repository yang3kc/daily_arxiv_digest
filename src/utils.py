def merge_dicts(list_of_dicts):
    merged = {}
    for d in list_of_dicts:
        merged.update(d)
    return merged
