'''
from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv
import math
import os 

origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/2_Tratadas/'
	cor = cv.imread(origem+'16.png')
	imagem = cv.cvtColor(cor,cv.COLOR_RGB2GRAY)


	height , width = imagem.shape[:2]

	print ("Altura: ",height, "Largura:", width)

	azul = (255, 0, 0)
	for i in range(0,10):
		for j in range(0,height-1):
			cor[j][i] = azul

	cv.imshow("Verificando",cor)
	cv.waitKey(0) 



	for i in range(0,height-1): #height
		for j in range(0,width-1): #width
			indice = imagem[i][j]
			print (indice)
			print ("---")


for _, _, arquivo in os.walk(origem):
	pass

print ("TESTE")
print (origem+arquivo[0])
print (len(arquivo))

for img in arquivo:
	try:
		print (origem + img)
		if(len(img) == 5):
			print (img[0:1])
		else:
			print (img[0:2])
		
		imagem = cv.imread(origem+img)
		cv.imshow('Imagem',imagem)
		cv.waitKey(0)
		cv.destroyAllWindows()

	except Exception as e:
		pass

print ("FINALIZADO")
'''


from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv
import math
import os 

imagem = cv.imread("/home/study/Documentos/Env_RCNN/darknet/CARROS/" + "download.jpeg")
imagem = cv.cvtColor(imagem,cv.COLOR_RGB2GRAY)

cv.imwrite("/home/study/Documentos/Env_RCNN/darknet/CARROS/carro_cinza.png",imagem)

