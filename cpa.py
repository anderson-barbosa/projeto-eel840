#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Este programa realiza a criptoanálise de uma imagem criptografada pelo
programa encrypt.py e utiliza o ataque do texto-limpo escolhido.

Para utilizar este programa, devem ser passados como parâmetros na linha de comando,
respectivamente, o nome da imagem a ser recuperada e o nome que deve ter a 
imagem-limpa, incluindo a extensão .bmp. Exemplo:

python cpa.py ciphered_image.bmp plain_image.bmp

'''

import numpy as np
from scipy.integrate import odeint
import math
import os
import sys

def main():
	ifname = sys.argv[1]
	ofname = sys.argv[2]
	cipherImage, header = read_bmp_image(ifname)
	width = len(cipherImage)
	height = len(cipherImage[0])

	chosenImage1 = [[0 for j in range(height)] for i in range(width)]
	save_bmp_image(chosenImage1, header, "chosen_plain_image_1.bmp")
	os.system("python encrypt.py chosen_plain_image_1.bmp keystream.bmp")
	keystream, header = read_bmp_image("keystream.bmp")

	phl = [[0 for j in range(height)] for i in range(width)]
	for i in range(width):
		for j in range(height):
			phl[i][j] = cipherImage[i][j]^keystream[i][j]

	chosenImage2 = [[j for j in range(height)] for i in range(width)]
	save_bmp_image(chosenImage2, header, "chosen_plain_image_2.bmp")
	os.system("python encrypt.py chosen_plain_image_2.bmp shuffled_image_11.bmp")
	shuffled1, header = read_bmp_image("shuffled_image_11.bmp")

	jhl = [[0 for j in range(height)] for i in range(width)]
	for i in range(width):
		for j in range(height):
			jhl[i][j] = shuffled1[i][j]^keystream[i][j]

	ph = [[0 for j in range(height)] for i in range(width)]
	for i in range(width):
		for j in range(height):
			ph[i][jhl[i][j]] = phl[i][j]

	chosenImage3 = [[i for j in range(height)] for i in range(width)]
	save_bmp_image(chosenImage3, header, "chosen_plain_image_3.bmp")
	os.system("python encrypt.py chosen_plain_image_3.bmp shuffled_image_12.bmp")
	shuffled2, header = read_bmp_image("shuffled_image_12.bmp")

	ihl = [[0 for j in range(height)] for i in range(width)]
	for i in range(width):
		for j in range(height):
			ihl[i][j] = shuffled2[i][j]^keystream[i][j]

	plainImage = [[0 for j in range(height)] for i in range(width)]
	for i in range(width):
		plainImage[ihl[i][0]] = ph[i]

	save_bmp_image(plainImage, header, ofname)

def read_bmp_image(imgName):
	'''
	Lê uma imagem no formato BMP de 256 cores com o nome imgName e retorna o cabeçalho 
	e uma lista de listas em que cada elemento representa um pixel da imagem.
	'''
	with open(imgName, "rb") as imagefile:
		f = imagefile.read()
		b = list(bytearray(f))

	hex_str1 = "0x"
	hex_str2 = "0x"
	for i in range(18, 22):
		hex_str1 += hex(b[i])[2:]
		hex_str2 += hex(b[i+4])[2:]
	imgWidth = int(hex_str1, 16)
	imgHeight = int(hex_str2, 16)

	matrix = [[0 for j in range(imgHeight)] for i in range(imgWidth)]
	for i in range(imgWidth):
		for j in range(imgHeight):
			matrix[i][j] = b[i*imgHeight+j+1078]

	header = b[:1078]
	matrix.reverse()
	return matrix, header

def save_bmp_image(matrix, header, imgName):
	'''
	Salva a imagem representada por matrix no formato BMP de 256 cores, com o cabeçalho header e 
	com o nome imgName
	'''
	b = header[:]
	for i in range(len(matrix)):
		for j in range(len(matrix[0])):
			b.append(matrix[len(matrix)-i-1][j])
	fl = open(imgName, "wb")
	fl.write(bytearray(b))
	fl.close()

if __name__ == "__main__":
	main()
