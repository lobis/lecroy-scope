from .file import trc_description


class Header:
    def __init__(self, header: dict):
        for name, _ in trc_description:
            setattr(self, f"_{name}", header[name])


# add header fields as properties
for (_name, _) in trc_description:
    setattr(
        Header,
        _name,
        property(lambda self, name=_name: self.__getattribute__(f"_{name}")),
    )
del _name
