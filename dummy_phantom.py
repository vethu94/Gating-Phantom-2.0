
class DummyPhantom():

    def __init__(self):
        pass
    
    def write(self, data):
        print(data)

    def flushInput(self):
        print("resetting input buffer")

    def flashOutput(self):
        print("resetting output buffer")
