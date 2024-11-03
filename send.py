import pika
from os import system
from time import sleep
from colorama import Fore, Style, Back, init

def criptografar(key, msg):
    def broke_message(msg):
        encodeMessage = bytearray(msg.encode('utf-8'))
        arrBlocks = []

        for i in range(0, 128, 16): # Loop para particionar a mensagem de formato bytes em 8 byte arrays
            arrBlocks.append(encodeMessage[i:i+16])
            if (i == 112 and len(encodeMessage) > 128):
                arrBlocks.append(encodeMessage[i+16:i+32])
                if len(encodeMessage) > 144:
                    arrBlocks.append(encodeMessage[i+32:i+48])

        for i in range(len(arrBlocks) - 1, -1, -1): # Loop para tirar os arrays bytes que não fazem parte da mensagem
            if len(arrBlocks[i]) == 0:
                arrBlocks.pop()
        for i in range(0, len(arrBlocks)):  # Loop para completar os blocos que não estiverem com os índices completos por valores com 0 para formar blocos de 16
            tam = len(arrBlocks[i])
            if tam < 16:
                for _ in range(0, 16 - tam + 1):
                    arrBlocks[i].append(0)
        
        return arrBlocks
    def message_to_state(byte_message):
        # Inicializa o estado (4x4)
        state = [[0]*4 for _ in range(4)]
        
        # Preenche o estado com os bytes da mensagem
        for i in range(4):
            for j in range(4):
                # Calcula o índice do byte na mensagem
                index = i * 4 + j
                if index < len(byte_message):
                    state[i][j] = byte_message[index]
                else:
                    state[i][j] = 0  # Preencher com 0 se não houver mais bytes
        return state
    def key_to_round_key(key):
        # Converte a chave para bytes, caso seja uma string
        if isinstance(key, str):
            byte_key = key.encode('utf-8')
        else:
            byte_key = key
        
        # Inicializa a matriz de chave 4x4 (4 linhas, 4 colunas)
        round_key = [[0]*4 for _ in range(4)]
        
        # Preenche a matriz de chave em ordem de coluna
        for i in range(4):  # Para cada coluna
            for j in range(4):  # Para cada linha
                index = i * 4 + j
                if index < len(byte_key):
                    round_key[j][i] = byte_key[index]  # Preencher em ordem de coluna
                else:
                    round_key[j][i] = 0  # Preenche com 0 se a chave for menor que 16 bytes

        return round_key
    def sub_bytes(state, S_BOX):
        for i in range(4):
            for j in range(4):
                state[i][j] = S_BOX[state[i][j]]
        return state
    def shift_rows(state):
        for i in range(1, 4):
            state[i] = state[i][i:] + state[i][:i]
        return state
    def add_round_key(state, round_key):
        """Aplica a operação AddRoundKey usando XOR entre o estado e a chave da rodada"""
        for i in range(4):  # Para cada linha
            for j in range(4):  # Para cada coluna
                state[i][j] ^= round_key[i][j]  # Realiza a operação XOR
        return state
    def msg_final(state):
        msg = ""

        for i in range(4):
            for j in range(4):
                msg += f"0x{state[i][j]:02x}"

        return msg
    def criptografar_texto_to_cesar(msg):
        msg_final = ""
        words = list(msg)

        for i in range(len(msg)):
            letter = msg[i]
            asc = ord(letter)

            if not (asc >= 33 and asc <= 126):
                asc = ord(words[i - 1]) + 1
            ready = asc - 3

            letter = chr(ready)
            words[i] = letter
        msg_final = ''.join(words)

        return msg_final
    S_BOX = [
        0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
        0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
        0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
        0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
        0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
        0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
        0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
        0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
        0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
        0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
        0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
        0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
        0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
        0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
        0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
        0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
    ]

    message_blocks = []
    final_message = ""
    byteArray = broke_message(msg)

    for i in range(len(byteArray)):
        state_msg = message_to_state(byteArray[i])
        state_subbytes = sub_bytes(state_msg, S_BOX)
        state_shifrows = shift_rows(state_subbytes)
        key_round_key = key_to_round_key(key)
        state_roundkey = add_round_key(state_shifrows, key_round_key)
        msg_aes = msg_final(state_roundkey)

        message_blocks.append(criptografar_texto_to_cesar(msg_aes))

    for i in message_blocks:
        final_message += i

    return final_message

def animacao_envio():
    mensagem_base = Fore.YELLOW + "Enviando mensagem"
    pontos = ""
    for _ in range(4):
        print(f"\r{mensagem_base}{pontos}", end="")
        pontos += "."
        
        if len(pontos) > 3:
            pontos = ""

        sleep(0.5)

    print(Fore.GREEN + "\rMensagem enviada com sucesso! Aguarde pela resposta.")
    sleep(2)

init()

# connection = pika.BlockingConnection(pika.ConnectionParameters(host="4.228.50.58", credentials=pika.PlainCredentials('vm-user', 'RabbitMQ1234')))
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="fila")

system("cls")

print(Back.BLUE + r'''
*******************************************************************************************************
*    ____ ____  ___ ____ _____ ___   ____ ____      _    _____ ___    _            _    _____ ____    *
*   / ___|  _ \|_ _|  _ \_   _/ _ \ / ___|  _ \    / \  |  ___|_ _|  / \          / \  | ____/ ___|   *
*  | |   | |_) || || |_) || || | | | |  _| |_) |  / _ \ | |_   | |  / _ \        / _ \ |  _| \___ \   *
*  | |___|  _ < | ||  __/ | || |_| | |_| |  _ <  / ___ \|  _|  | | / ___ \      / ___ \| |___ ___) |  *
*   \____|_| \_\___|_|    |_| \___/ \____|_| \_\/_/   \_\_|   |___/_/   \_\    /_/   \_\_____|____/   *
*                                                                                                     *
*******************************************************************************************************''' + Style.RESET_ALL)
key = input(Back.LIGHTBLACK_EX + "Informe a chave a ser utilizada:" + Style.RESET_ALL + " ")
print()
msg = input(Back.LIGHTBLACK_EX + "Mensagem a ser enviada:" + Style.RESET_ALL + " ")
system("cls")


channel.basic_publish(exchange="", routing_key="fila", body=criptografar(key, msg))
animacao_envio()

connection.close()
