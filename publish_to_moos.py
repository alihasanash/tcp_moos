import pymoos

def publish_to_moos():
    # Inisialisasi komunikasi dengan MOOSDB
    comms = pymoos.comms()
    
    # Konfigurasi server MOOSDB (ganti dengan alamat dan port MOOSDB Anda)
    moos_server = "localhost"
    moos_port = 9000

    # Hubungkan ke MOOSDB
    if not comms.run(moos_server, moos_port, "python_publisher"):  # Nama aplikasi MOOS
        print("Failed to connect to MOOSDB")
        return

    # String yang akan dipublikasikan
    key = "AIS_DATA"
    value = "!AIVDM,1,1,,B,15N9qL0P1cI>9g4@j>@oMwwn00RM,0*43"

    # Publish string ke MOOSDB
    comms.notify(key, value)
    print(f"Published: {key} -> {value}")

    # Tutup koneksi setelah publish
    comms.close(nice=True)

if __name__ == "__main__":
    publish_to_moos()