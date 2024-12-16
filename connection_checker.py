import socket

def is_connected():
    """
    Check if there is an active internet connection.
    Returns True if connected, False otherwise.
    """
    try:
        # Attempt to connect to a public DNS server (Google's 8.8.8.8)
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False