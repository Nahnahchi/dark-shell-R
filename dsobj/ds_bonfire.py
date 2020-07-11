
class DSRBonfire:

    def __init__(self, source: str):
        source = source.split()
        self.bonfire_id = int(source[0]) if len(source) > 0 and source[0].isnumeric() else -1
        self.bonfire_name = " ".join(source[1:]) if len(source) > 1 else ""

    def get_id(self):
        return self.bonfire_id

    def get_name(self):
        return self.bonfire_name
