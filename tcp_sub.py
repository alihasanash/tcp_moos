import time
import json
import socket
import pymoos

class MOOSBridge:
    def __init__(self, moos_host="localhost", moos_port=9000, tcp_host="0.0.0.0", tcp_port=5000):
        self.moos_host = moos_host
        self.moos_port = moos_port
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.comms = pymoos.comms()
        self.comms.set_on_connect_callback(self.on_connect)
        self.comms.set_on_mail_callback(self.on_new_mail)

        self.data = {key: None for key in [
            "NAV_LAT",
            "NAV_LONG",
            "NAV_DEPTH",
            "NAV_HEADING",
            "NAV_HEADING_OVER_GROUND",
            "NAV_SPEED",
            "NAV_SPEED_OVER_GROUND",
            "NAV_YAW",
            "NAV_Z",
            "MAP_INFO_REQ"
        ]}

        self.client_socket = None
        self.server_socket = self.setup_socket()

    def setup_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.tcp_host, self.tcp_port))
        sock.listen(1)
        print(f"[INFO] Waiting for client on port {self.tcp_port}...")
        self.client_socket, _ = sock.accept()
        print("[INFO] Client connected.")
        return sock

    def run(self):
        if not self.comms.run(self.moos_host, self.moos_port, "MOOSBridge"):
            print("[ERROR] Failed to connect to MOOSDB.")
            return

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down.")
            if self.client_socket:
                self.client_socket.close()
            self.server_socket.close()
            self.comms.close(True)

    def on_connect(self):
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
            self.send_to_client()

        return True

    def send_to_client(self):
        try:
            json_data = json.dumps(self.data).encode('utf-8')
            self.client_socket.sendall(json_data)
            print(f"[SEND] {json_data}")
        except (socket.error, BrokenPipeError):
            print("[WARN] Connection lost. Waiting for new client...")
            self.client_socket, _ = self.server_socket.accept()
            print("[INFO] Client reconnected.")

if __name__ == "__main__":
    bridge = MOOSBridge()
    bridge.run()
