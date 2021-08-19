
class DummyPhantom():

    def __init__(self):
        pass
    
    def write(self, data):
        print(data)

    def reset_input_buffer(self):
        print("resetting input buffer")

    def reset_output_buffer(self):
        print("resetting output buffer")