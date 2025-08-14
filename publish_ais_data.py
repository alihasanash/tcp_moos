import pymoos

def publish_ais_data():
    moos = pymoos.comms()

    def on_connect():
        print("[MOOS] Connected to MOOSDB")
        return True

    moos.set_on_connect_callback(on_connect)
    if not moos.run('localhost', 9000, 'AISPublisher'):
        print("[ERROR] Failed to connect to MOOSDB")
        return

    if not moos.is_connected():
        print("[ERROR] Not connected to MOOSDB")
        return

    # Publish two different AIS_DATA alternately
    ais_data_list = ["AIS Data String 1", "AIS Data String 2"]
    for i, ais_data in enumerate(ais_data_list):
        print(f"[DEBUG] Attempting to send AIS_DATA ({i+1}/2): {ais_data}")
        if moos.notify("AIS_DATA", ais_data):
            print(f"[INFO] AIS_DATA sent successfully ({i+1}/2)")
        else:
            print(f"[ERROR] Failed to send AIS_DATA ({i+1}/2)")

if __name__ == "__main__":
    publish_ais_data()