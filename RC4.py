import sys
import numpy as np

def crypt(PlainBytes, KeyBytes):
    cipherList = []
    keyLen = len(KeyBytes)
    plainLen = len(PlainBytes)
    S = np.arange(256)
    j = 0
    for i in range(256):
        j = (j + S[i] + KeyBytes[i % keyLen]) % 256
        S[i], S[j] = S[j], S[i]
    i = 0
    j = 0
    for m in range(plainLen):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        k = S[(S[i] + S[j]) % 256]
        cipherList.append(k ^ PlainBytes[m])
    l=len(cipherList)
    return np.array(cipherList,dtype=uint8).reshape(l,1)

def text_to_bytes(filename):
    byteList = []
    f = open(filename, 'r')
    s = f.read()
    f.close()
    for byte in s:
        byteList.append(ord(byte))
    return byteList

def bytes_to_text(ByteList):
    s = ''
    for byte in ByteList:
        s += chr(byte)
    f = open('test.txt', 'w')
    f.write(s)
    f.close()

# PlainBytes = text_to_bytes('plain.txt')
# PlainBytes = [25,45,64]
# KeyBytes = text_to_bytes('key.txt')
# CipherBytes = crypt(PlainBytes, KeyBytes)
# PlainBytes_ = crypt(CipherBytes, KeyBytes)

# bytes_to_text(PlainBytes_)
