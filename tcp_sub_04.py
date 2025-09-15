import time
import json
import socket
import pymoos
import threading

# UPDATE NOTES v1.0:
# Added threading for client connection and periodic checks
# Print data each time data is sent and status of the send
# Add periodic check to send data every 10 seconds if no updates
# Added error handling for socket communication

# UPDATE NOTES v2.0:
# Added additional variables for navigation and route information

# UPDATE NOTES v3.0:
# If not connected to MOOSDB, do not send data to client

# UPDATE NOTES v4.0:
# Added more navigation variables: NAV_ALTITUDE, NAV_LAT_DMS, NAV_LONG_DMS, NAV_COG

class MOOSBridge:
    def __init__(self, moos_host="localhost", moos_port=9000, tcp_port=5000):
        self.moos_host = moos_host
        self.moos_port = moos_port
        self.tcp_port = tcp_port
        self.comms = pymoos.comms()
        self.comms.set_on_connect_callback(self.on_connect)
        self.comms.set_on_mail_callback(self.on_new_mail)

        self.data = {key: None for key in [
            "NAV_LAT", "NAV_LONG", "NAV_DEPTH",
            "NAV_HEADING", "NAV_HEADING_OVER_GROUND",
            "NAV_SPEED", "NAV_SPEED_OVER_GROUND",
            "NAV_YAW", "NAV_Z", "MAP_INFO_REQ", "WAIS_NMEA",
            
            "NAV_STW", "NAV_DRIFT", "NAV_DRIFT_ANGLE", "NAV_SET",
            "NAV_ROT", "NAV_DEPTH_BELOW_KEEL",
            "RTE_WP_BRG", "RTE_XTD", "RTE_CRS",
            "RTE_CTM", "RTE_DTG", "RTE_TTG",
            "RTE_ETA",

            "NAV_ALTITUDE", "NAV_LAT_DMS", "NAV_LONG_DMS", "NAV_COG"
        ]}

        self.client_socket = None
        self.last_update_time = time.time()
        self.moos_connected = False  # status koneksi MOOSDB

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", self.tcp_port))
        self.server_socket.listen(1)

        threading.Thread(target=self.accept_client_thread, daemon=True).start()
        threading.Thread(target=self.periodic_check_thread, daemon=True).start()

    def accept_client_thread(self):
        while True:
            print(f"[INFO] Waiting for client on port {self.tcp_port}...")
            client, addr = self.server_socket.accept()
            self.client_socket = client
            print(f"[INFO] Client connected from {addr}")

    def periodic_check_thread(self):
        while True:
            time.sleep(1)
            # hanya kirim periodic jika konek ke MOOSDB
            if self.moos_connected and time.time() - self.last_update_time >= 10:
                self.send_to_client(force=True)
                self.last_update_time = time.time()

    def run(self):
        if not self.comms.run(self.moos_host, self.moos_port, "MOOSBridge"):
            print("[ERROR] Failed to connect to MOOSDB.")
            return

        try:
            while True:
                time.sleep(0.1)
                # deteksi disconnect MOOSDB
                if not self.comms.is_connected() and self.moos_connected:
                    print("[WARN] Disconnected from MOOSDB.")
                    self.moos_connected = False
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down.")
            if self.client_socket:
                self.client_socket.close()
            self.server_socket.close()
            self.comms.close(True)

    def on_connect(self):
        self.moos_connected = True
        print("[INFO] Connected to MOOSDB.")
        for var in self.data:
            self.comms.register(var, 0)
            print(f"[INFO] Subscribed to {var}")
        return True

    def on_new_mail(self):
        updated = False
        for msg in self.comms.fetch():
            key = msg.key()
            if key in self.data:
                new_value = msg.double() if msg.is_double() else msg.string()
                if self.data[key] != new_value:
                    self.data[key] = new_value
                    updated = True

        if updated:
            self.last_update_time = time.time()
            self.send_to_client()
        return True

    def send_to_client(self, force=False):
        # jangan kirim kalau tidak konek ke MOOSDB
        if not self.moos_connected:
            return

        json_data = json.dumps(self.data)
        if self.client_socket:
            try:
                self.client_socket.sendall(json_data.encode('utf-8'))
                status = "(DATA SENT [V])" if not force else "(PERIODIC DATA SENT [V])"
                print(f"[SEND] {json_data} {status}")
            except (socket.error, BrokenPipeError):
                print("[WARN] Connection lost.")
                self.client_socket = None
        else:
            status = "(DATA NOT SENT [X])" if not force else "(PERIODIC DATA NOT SENT [X])"
            print(f"[SEND] {json_data} {status}")

if __name__ == "__main__":
    bridge = MOOSBridge()
    bridge.run()
