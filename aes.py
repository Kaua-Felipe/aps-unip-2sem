def message_to_state(message):
    # Converte a mensagem para bytes usando UTF-8
    byte_message = message.encode('utf-8')
    
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

def sub_bytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = S_BOX[i][j]
    return state

def shift_rows(state):
    for i in range(1, 4):
        state[i] = state[i][i:] + state[i][:i]
    return state

def xtime(byte):
    """Multiplica o byte por 2 em GF(2^8)"""
    return ((byte << 1) ^ (0x1b if (byte & 0x80) else 0)) & 0xff

def mix_columns(state):
    for j in range(4):
        a = [state[i][j] for i in range(4)]

        state[0][j] = xtime(a[0]) ^ a[1] ^ a[2] ^ a[3]
        state[1][j] = a[0] ^ xtime(a[1]) ^ a[2] ^ a[3]
        state[2][j] = a[0] ^ a[1] ^ xtime(a[2]) ^ a[3]
        state[3][j] = a[0] ^ a[1] ^ a[2] ^ xtime(a[3])
        
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
            msg += hex(state[i][j])

    return msg

S_BOX = [
    [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5],
    [0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
    [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0],
    [0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0],
    [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc],
    [0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15],
    [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a],
    [0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75],
    [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0],
    [0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84],
    [0x53, 0x99, 0x61, 0x17, 0x2b, 0x04, 0x7e, 0x94],
    [0x6c, 0x9e, 0x0a, 0x67, 0x1d, 0x0c, 0x13, 0x1b],
    [0x00, 0x25, 0x9c, 0x6b, 0x07, 0x3d, 0x1e, 0x6f],
    [0xc2, 0x0c, 0x99, 0xb5, 0x7f, 0x58, 0x07, 0x09],
    [0x4e, 0x3b, 0x8c, 0x79, 0x77, 0xa3, 0x91, 0x9d],
    [0xd1, 0x11, 0xf1, 0xc0, 0x4b, 0x5f, 0x1b, 0xd0],
    [0x37, 0xf4, 0x50, 0x6e, 0x76, 0xe3, 0x3d, 0x5b]
]
round_key = [
    [0x2b, 0x7e, 0x15, 0x16],
    [0x28, 0xae, 0xd2, 0xa6],
    [0xab, 0xf7, 0x90, 0x5b],
    [0x6d, 0x51, 0x63, 0x3f],
]

msg_state = message_to_state("alguma mensagem aqui")
print(msg_state ,"\n")

new_state = sub_bytes(msg_state)
print(new_state, "\n")

new_state_shifrows = shift_rows(new_state)
print(new_state_shifrows, "\n")

new_state_mixcolumns = mix_columns(new_state_shifrows)
print(new_state_mixcolumns, "\n")

new_state_roundkey = add_round_key(new_state_mixcolumns, round_key)
print(new_state_roundkey, "\n")

print(msg_final(new_state_roundkey))
