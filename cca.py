#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy.integrate import odeint
import math
import os
import sys
import matplotlib.pyplot as plt

def main():
	ifname = sys.argv[1]
	ofname = sys.argv[2]
	cipherImage, header = read_bmp_image(ifname)
	width = len(cipherImage)
	height = len(cipherImage[0])

	chosenImage1 = [[0 for j in range(height)] for i in range(width)]
	save_bmp_image(chosenImage1, header, "chosen_ciphered_image_1.bmp")
	os.system("python decrypt2.py chosen_ciphered_image_1.bmp keystream.bmp")
	keystream, header = read_bmp_image("keystream.bmp")

	phl = [[0 for j in range(height)] for i in range(width)]
	for i in range(width):
		for j in range(height):
			phl[i][j] = cipherImage[i][j]^keystream[i][j]

	chosenImage2 = [[i^keystream[i][j] for j in range(height)] for i in range(width)]
	save_bmp_image(chosenImage2, header, "chosen_ciphered_image_2.bmp")
	os.system("python decrypt.py chosen_ciphered_image_2.bmp shuffled_image_21.bmp")
	ih, header = read_bmp_image("shuffled_image_21.bmp")

	chosenImage3 = [[j^keystream[i][j] for j in range(height)] for i in range(width)]
	save_bmp_image(chosenImage3, header, "chosen_ciphered_image_3.bmp")
	os.system("python decrypt.py chosen_ciphered_image_3.bmp shuffled_image_22.bmp")
	jh, header = read_bmp_image("shuffled_image_22.bmp")

	plainJ = [[] for i in range(width)]
	for i in range(width):
		plainJ[i] = jh[ih[i][0]]

	ph = [[0 for j in range(height)] for i in range(width)]
	for i in range(width):
		for j in range(height):
			ph[i][j] = phl[i][plainJ[i][j]]

	plainImage = [[] for j in range(width)]
	for i in range(width):
		plainImage[i] = ph[ih[i][0]]

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
