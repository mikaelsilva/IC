from matplotlib import pyplot as plt
from datetime import datetime
from random import randint
import pandas as pd
import numpy as np
import cv2 as cv
import json
import math
import csv
import os

def mostrar_imagem(imagem):
	cv.imshow('Imagem',imagem)
	cv.waitKey(0)
	cv.destroyAllWindows()

def mostrar_2_imagens(imagem1,imagem2):
	plt.subplot(221), plt.imshow(imagem1, 'gray')
	plt.subplot(222), plt.imshow(imagem2,'gray')
	plt.show()
	

def mostrar_imagens(imagem1,imagem2,imagem3,imagem4):
	plt.subplot(221), plt.imshow(imagem1, 'gray')
	plt.subplot(222), plt.imshow(imagem2,'gray')
	plt.subplot(223), plt.imshow(imagem3,'gray')
	plt.subplot(224), plt.imshow(imagem4,'gray')
	plt.show()
	
	return 0
if __name__ == "__main__":
    origem = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_IC\\Origem_Imagens\\Imagens_Google_Maps\\"
    lista = ["320.jpg","331.jpg","343.jpg","355.jpg","378.jpg","403.jpg","399.jpg","400.jpg"]

    for i in lista:
        imagem = cv.imread(origem + i)[256:512,0:512]
        imagem_cinza = cv.cvtColor(imagem,cv.COLOR_RGB2GRAY)
        print(imagem.shape)
        mostrar_imagem(imagem)
        #y,x = 256, 512
        imagem_copia = imagem

        #for i in range(0,256):
        #    y,x = 255 - i,i
        #    imagem_copia[y][x] = (0,255,0)
        #    imagem_copia[i][x+255] = (0,255,0)

        #    if(x <= 206):
        #        imagem_copia[y-50][x] = (0,0,255)
        #        imagem_copia[i][x+305] = (0,0,255)
        a = 0
        for i in range(0,512):
            for j in range(0,256):
                if(i <= 256 and (206 <= (i + j)) or (i > 256 and ((i - j) <= 296))):
                    imagem_copia[j][i] = (0,0,255)
                    a += 1

        imagem_cinza2 = cv.cvtColor(imagem_copia,cv.COLOR_RGB2GRAY)
        mostrar_2_imagens(imagem_cinza,imagem_cinza2)
        print(a)
        #mostrar_imagem(imagem_cinza2)
    