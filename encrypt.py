#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Este programa criptografa uma imagem no formato BMP de 256 cores.

Para utilizar este programa, devem ser passados como parâmetros na linha de comando,
respectivamente, o nome da imagem a ser criptografada e o nome que deve ter a imagem
cifrada, incluindo a extensão .bmp. Exemplo:

python encrypt.py plain_image.bmp ciphered_image.bmp

'''

import numpy as np
from scipy.integrate import odeint
import math
import sys

# Parâmetro do mapa logístico
R = 4

# Número de vezes que o mapa logístico é iterado antes do ínicio do embaralhamento
L0 = 10

# Constantes do sistema hipercaótico
A = 36
B = 3 
C = 28 
D = -16 
K = 0.2 

# Chave a ser usada na encriptação
# O primeiro elemento é o valor inicial do mapa logístico e os demais são os valores iniciais do sistema hipercaótico
KEY = [0.45, 0.3, -0.4, 1.2, 1]

# Número de vezes que o sistema hipercaótico é iterado antes do início da encriptação
N0 = 3000

def main():
	ifname = sys.argv[1]
	ofname = sys.argv[2]
	plainImage, header = read_bmp_image(ifname)
	width = len(plainImage)
	height =len(plainImage[0])

	xn1 = KEY[0]
	for i in range(L0):
		xn1 = logistic_map(xn1)

	h_list = []
	while len(h_list)<width:
		hi = int((xn1*10**14)%width)
		if hi not in h_list:
			h_list.append(hi)
		xn1 = logistic_map(xn1)
	ph = shuffle_rows(plainImage, h_list)

	phl = []
	for i in range(width):
		l_list = []
		while len(l_list)<height:
			li = int((xn1*10**14)%256)
			if li not in l_list:
				l_list.append(li)
			xn1 = logistic_map(xn1)
		phl.append(shuffle_cols(ph[i], l_list))

	time = 0
	currState = KEY[1:]
	currState = iterate_system(N0, currState, time)
	time = 0.03

	cipheredImage = [[0 for i in range(height)] for j in range(width)]
	for i in range(math.ceil(width*height/3)):
		currState = iterate_system(1, currState, time)
		time+=0.00001
		xx = []
		for j in range(4):
			xx.append(int((abs(currState[j])-math.floor(abs(currState[j])))*10**14)%256)
		xbar = xx[0]%4

		indexes = [3*i, 3*i+1, 3*i+2]
		rows = [y//256 for y in indexes]
		cols = [y%256 for y in indexes]

		cipheredImage[rows[0]][cols[0]] = phl[rows[0]][cols[0]]^xx[xbar//2+1]
		if i<math.ceil(width*height/3)-1:
			cipheredImage[rows[1]][cols[1]] = phl[rows[1]][cols[1]]^xx[(xbar+8)//3]
			cipheredImage[rows[2]][cols[2]] = phl[rows[2]][cols[2]]^xx[xbar//3]
		else:
			if ((i+1)*3)-(width*height)<2:
				cipheredImage[rows[1]][cols[1]] = phl[rows[1]][cols[1]]^xx[(xbar+8)//3]
			if ((i+1)*3)-(width*height)<1:
				cipheredImage[rows[2]][cols[2]] = phl[rows[2]][cols[2]]^xx[xbar//3]

	save_bmp_image(cipheredImage, header, ofname)

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

def logistic_map(xn):
	'''
	Retorna o resultado do mapa logístico para o valor xn.
	'''
	return round(R*xn*(1-xn), 14)

def shuffle_rows(matrix, hl):
	'''
	Retorna as linhas de matrix embaralhadas na ordem estabelecida pela lista hl
	'''
	ret = []
	for i in range(len(matrix)):
		ret.append(matrix[hl[i]])
	return ret

def shuffle_cols(row, ll):
	'''
	Retorna as colunas da linha row embaralhadas na ordem estabelecida pela lista ll
	'''
	ret = []
	for i in range(len(row)):
		ret.append(row[ll[i]])
	return ret

def f(state, t):
	'''
	Implementa o sistema hipercaótico.
	'''
	x1, x2, x3, x4 = state
	return A*(x1-x2), -x1*x3+D*x1+C*x2-x4, x1*x2-B*x3, x1+K

def iterate_system(niter, curr_state, curr_time):
	'''
	Itera o sistema hipercaótico niter vezes a partir do estado curr_state e do tempo curr_time
	e retorna o estado alcançado após a pultima iteração.
	'''
	t = [curr_time+i*0.00001 for i in range(niter+1)]
	t = np.array(t)
	states = odeint(f, curr_state, t)
	return states[-1]

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
