import pymoos

class AISDataPublisher:
    def __init__(self, moos_host="localhost", moos_port=9000):
        self.comms = pymoos.comms()
        self.comms.set_on_connect_callback(self.on_connect)
        if not self.comms.run(moos_host, moos_port, "AISDataPublisher"):
            print("Failed to connect to MOOS database")
        else:
            print(f"Attempting to connect to MOOS database at {moos_host}:{moos_port}")

    def on_connect(self):
        print("Successfully connected to MOOS database")
        return True

    def publish(self):
        ais_data_list = ["AIS Data String 1", "AIS Data String 2"]
        for i, ais_data in enumerate(ais_data_list):
            print(f"[DEBUG] Attempting to send AIS_DATA ({i+1}/2): {ais_data}")
            if self.comms.notify("AIS_DATA", ais_data):
                print(f"[INFO] AIS_DATA sent successfully ({i+1}/2)")
            else:
                print(f"[ERROR] Failed to send AIS_DATA ({i+1}/2)")

if __name__ == "__main__":
    publisher = AISDataPublisher()
    publisher.publish()
