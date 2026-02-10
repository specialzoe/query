import socket


class Query:
    """
    Interface for the minecraft query protocol

    Attributes
    ----------
    server : tuple(str, int)
        host ip and query port

    Methods
    -------
    basic_stat():
        basic statistics (notably numplayers) as defined in the query protocol
    full_stat():
        full statistics (notably list of players) as defined in the query protocol
    """
    __MAGIC = b'\xFE\xFD'
    __SESSION_ID = b'\x00\x00\x00\x00' # Session IDs are not necessary for the query protocol
    __PADDING = b'\x00\x00\x00\x00' # The content of the padding is arbitrary


    def __init__(self, host_ip: str, query_port: int):
        self.server = (host_ip, query_port)
        self.__udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__udp_sock.settimeout(2)


    def close(self):
        self.__udp_sock.close()


    def __get_challenge_bytes(self) -> bytes:
        """
        Raises:
            TimeoutError: If the socket times out
            ConnectionError: On any other exceptions related to the socket
        """
        try:
            self.__udp_sock.sendto(self.__MAGIC + b'\x09' + self.__SESSION_ID, self.server) # Handshake
            d, _ = self.__udp_sock.recvfrom(4096)
            return int(d[5:-1].decode()).to_bytes(4, byteorder='big', signed=True) # covert to big-endian int32
        except socket.timeout:
            raise TimeoutError
        except Exception as e:
            raise ConnectionError("Could not reach the server. Is enable-query=true in server.properties? " + str(e))


    def basic_stat(self) -> dict:
        """
        Basic statistics (https://minecraft.wiki/w/Query#Basic_stat)

        Returns:
            dict: dictionary with keys "type", "session_id", "motd", "gametype", "map", "numplayers", "maxplayers", "hostport", "hostip"

        Raises:
            KeyError: If the contents of the servers reply could not be parsed correctly
            TimeoutError: If the socket times out
            ConnectionError: On any other exceptions related to the socket
        """
        challenge_bytes = self.__get_challenge_bytes()
        self.__udp_sock.sendto(self.__MAGIC + b'\x00' + self.__SESSION_ID + challenge_bytes, self.server)
        d, _ = self.__udp_sock.recvfrom(4096)

        try:
            nts_data = d[5:-1].split(b'\x00')
            hostinfo = nts_data[5]

            return {
                "type": int.from_bytes(d[:1]),
                "session_id": int.from_bytes(d[1:5]),
                "motd": nts_data[0].decode(),
                "gametype": nts_data[1].decode(),
                "map": nts_data[2].decode(),
                "numplayers": int(nts_data[3].decode()),
                "maxplayers": int(nts_data[4].decode()),
                "hostport": int.from_bytes(hostinfo[:2], byteorder='little', signed=False),
                "hostip": hostinfo[2:].decode()
            }
        except:
            raise KeyError("Contents of the servers reply could not be parsed")


    def full_stat(self) -> dict:
        """
        Full statistics (https://minecraft.wiki/w/Query#Full_stat)

        Returns:
            dict: dictionary with keys "type", "session_id", "hostname", "gametype", "game_id", "version", "plugins", "map", "numplayers", "maxplayers", "hostport", "hostip", "players"

        Raises:
            KeyError: If the contents of the servers reply could not be parsed correctly
            TimeoutError: If the socket times out
            ConnectionError: On any other exceptions related to the socket
        """
        challenge_bytes = self.__get_challenge_bytes()
        self.__udp_sock.sendto(self.__MAGIC + b'\x00' + self.__SESSION_ID + challenge_bytes + self.__PADDING, self.server)
        d, _ = self.__udp_sock.recvfrom(4096)

        res = dict()

        try:
            res["type"] = int.from_bytes(d[:1])
            res["session_id"] = int.from_bytes(d[1:5])
            nts_data = d[16:].split(b'\x00')
            for key, value in zip(nts_data[0::2], nts_data[1::2]):
                if key != b'':
                    try: # convert to int when possible
                        res[key.decode()] = int(value.decode())
                    except ValueError:
                        res[key.decode()] = value.decode()
                else: break

            marker = b'\x01player_\x00\x00'
            i = d.find(marker)
            res["players"] = []
            for username in d[i + len(marker):-2].split(b'\x00'):
                res["players"].append(username.decode())
            return res
        except:
            raise KeyError("Contents of the servers reply could not be parsed")