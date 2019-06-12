class Tops:
    def __init__(self, name, tag, th, s_tro, e_tro, s_don, e_don):
        self.name = name
        self.tag = tag
        self.townhall = th
        self.s_trophy = s_tro
        self.e_trophy = e_tro
        self.s_donation = s_don
        self.e_donation = e_don

    def __str__(self):
        return self.name