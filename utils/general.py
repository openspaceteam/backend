def str_to_bool(s):
    return s.strip().lower() if type(s) is str else s in ["true", "1", 1]


def str_is_bool(s):
    return s.strip().lower() if type(s) is str else s in ["true", "false", "1", "0", 1, 0]
