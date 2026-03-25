# Shared - Start
import socket, os, struct

def send_msg(sock, data):
    header = struct.pack(">I", len(data))
    sock.sendall(header + data)

def recv_msg(sock):
    try:
        header = sock.recv(4)
        if len(header) < 4: return None
        length = struct.unpack(">I", header)[0]
        buf = b""
        while len(buf) < length:
            chunk = sock.recv(length - len(buf))
            if not chunk: return None
            buf += chunk
        return buf
    except:
        return None

def process_client_data(sock, data, clients_list):
    if data.startswith(b"UPLOAD|"):
        _, filename, content = data.split(b"|", 2)
        with open("srv_" + filename.decode(), "wb") as f:
            f.write(content)
        send_msg(sock, b"[Server]: Upload berhasil!")
        
    elif data.startswith(b"DOWNLOAD|"):
        filename = data.split(b"|", 1)[1].decode()
        fname = "srv_" + filename
        if os.path.exists(fname):
            with open(fname, "rb") as f:
                content = f.read()
            send_msg(sock, b"FILE|" + filename.encode() + b"|" + content)
        else:
            send_msg(sock, b"[Server]: File tidak ditemukan.")
            
    elif data == b"LIST":
        files = "\n".join([f.replace("srv_", "") for f in os.listdir('.') if f.startswith('srv_')])
        send_msg(sock, b"[Server Files]:\n" + (files.encode() if files else b"Kosong"))
        
    elif data.startswith(b"MSG|"):
        msg = data.split(b"|", 1)[1]
        for c in clients_list:
            if c != sock:
                try: send_msg(c, b"[Broadcast]: " + msg)
                except: pass
# Shared - Finish

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 5000))
    s.listen(5)
    print("Sync Server Started")

    while True:
        conn, addr = s.accept()
        print(f"Connected: {addr}")
        clients = [conn]
        while True:
            data = recv_msg(conn)
            if not data:
                print(f"Disconnected: {addr}")
                conn.close()
                break
            process_client_data(conn, data, clients)