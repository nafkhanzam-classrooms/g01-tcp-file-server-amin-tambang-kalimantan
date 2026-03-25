import socket, threading, os, struct, sys

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

def receive_handler(sock):
    while True:
        data = recv_msg(sock)
        if not data:
            print("\nTerputus dari server.")
            os._exit(0)
        
        if data.startswith(b"FILE|"):
            _, filename, content = data.split(b"|", 2)
            fname = "dl_" + filename.decode()
            with open(fname, "wb") as f:
                f.write(content)
            print(f"\n[Berhasil mengunduh: {fname}]")
        else:
            print(f"\n{data.decode()}")

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 5000))
    
    threading.Thread(target=receive_handler, args=(s,), daemon=True).start()
    
    print("Commands: /list | /upload <file> | /download <file> | <pesan>")
    while True:
        cmd = input()
        if cmd.startswith("/upload "):
            filename = cmd.split(" ", 1)[1]
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    content = f.read()
                send_msg(s, b"UPLOAD|" + filename.encode() + b"|" + content)
            else:
                print("File tidak ditemukan.")
        elif cmd.startswith("/download "):
            filename = cmd.split(" ", 1)[1]
            send_msg(s, b"DOWNLOAD|" + filename.encode())
        elif cmd == "/list":
            send_msg(s, b"LIST")
        else:
            send_msg(s, b"MSG|" + cmd.encode())