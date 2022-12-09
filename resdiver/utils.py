def map_value(x, map: dict):
    if x in map:
        return map[x]
    else:
        return x


class NonMutableDict(dict):
    """Dict where keys can only be added but not modified.

    Will raise an error if the user try to overwrite one key. The error message
    can be customized during construction. It will be formatted using {key} for
    the overwritten key.
    """

    def __init__(self, *args, **kwargs):
        self._error_msg = kwargs.pop(
            "error_msg",
            "Try to overwrite existing key: {key}",
        )
        if kwargs:
            raise ValueError("NonMutableDict cannot be initialized with kwargs.")
        super(NonMutableDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if key in self:
            raise ValueError(self._error_msg.format(key=key))
        return super(NonMutableDict, self).__setitem__(key, value)

    def update(self, other):
        if any(k in self for k in other):
            raise ValueError(self._error_msg.format(key=set(self) & set(other)))
        return super(NonMutableDict, self).update(other)


def flatten_nest_dict(d):
    """Return the dict with all nested keys flattened joined with '/'."""
    # Use NonMutableDict to ensure there is no collision between features keys
    flat_dict = NonMutableDict()
    for k, v in d.items():
        if isinstance(v, dict):
            flat_dict.update({"{}/{}".format(k, k2): v2 for k2, v2 in flatten_nest_dict(v).items()})
        else:
            flat_dict[k] = v
    return flat_dict
