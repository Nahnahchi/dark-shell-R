
class DSRBonfire:

    def __init__(self, res: str):
        res = res.split()
        self.b_id = int(res[0])
        self.b_name = " ".join(res[1:])

    def get_id(self):
        return self.b_id

    def get_name(self):
        return self.b_name
