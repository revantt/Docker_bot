CTI = {
    ""
}
class Labeling:
    def __init__(self):
        self.Tokens = [ "overlap", "position", "barcode","scan"]
class Upps:
    def __init__(self):
        self.Tokens = ["return address"]
class CRS:
    def __init__(self):
        self.Tokens = ["crs", "route","routing","cr","cris","carrierroutingservice","carrierroutingservices","getroutingdata"]
class IDGS:
    def __init__(self):
        self.Tokens = ["tracking", "id"]

class Manifest:
    def __init__(self):
        self.Tokens = ["manifest","manif"]
