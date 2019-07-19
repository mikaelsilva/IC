from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv
import math

origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/3_SubImagens/'

cor = cv.imread(origem+'16.png')
imagem = cv.cvtColor(cor,cv.COLOR_RGB2GRAY)


height , width = imagem.shape[:2]

print ("Altura: ",height, "Largura:", width)

#azul = (255, 0, 0)

#imagem[height-1][width-1] = azul

cv.imshow("Verificando",imagem)
cv.waitKey(0) 

for i in range(0,height-1): #height
	for j in range(0,width-1): #width
		indice = imagem[i][j]
		print (indice)
		print ("---")