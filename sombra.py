from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv
import math


def mostrar_imagem(imagem):
	cv.imshow('Imagem',imagem)
	cv.waitKey(0)
	cv.destroyAllWindows()

def erosao(imagem):
	kernel = np.ones((10,10),np.uint8)
	opening = cv.morphologyEx(imagem, cv.MORPH_OPEN,(5,5))	 
	erosao = cv.erode(opening,kernel,iterations = 1) #VERIFICAR ESSA ALTERALÇÃO DO CL1 POR DST
	return erosao

def thresholding(imagem):
	ret,th = cv.threshold(imagem,0,255,cv.THRESH_BINARY + cv.THRESH_OTSU)
	return th

def canny(imagem):
	teste = cv.Canny(imagem,100,200)
	return teste

def contornos(imagem):
	imagem2, contornos, hierarquia = cv.findContours(imagem, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
	return (imagem2,contornos,hierarquia)	

def desenhando(imagem,contornos):
	# se [contornos],0   | então é um contorno por vez pela posição
	# se contornos,-1  | então é todas os contornos passados na posição
	cv.drawContours(imagem,[contornos],0,(0,0,255),3) 
	return imagem

def salvar(imagem,nome):
	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/5_Finalizadas'
	final = destino + nome + '.png'

	cv.imwrite(final,imagem)

def limites_externos(x,x1,y,y1):
	if ((x-20) >= 0):
		x -= 20
	else:
		try:
			x -= 5
		except:
			x = x

	if ((x1 + 20) <= 512):
		x1 += 20
	else:
		x -= 5

	#----------------------------------------------------------------------------------------
	if ((y - 20) >= 256 ):
		y -= 20
	else:
		x -= 5

	if ((y1 + 20) <= 512 ):
		y1 -= 20
	else:
		y1 -= 5

	return x,x1,y,y1

def mascara (imagem):
	mask = np.zeros(imgray.shape,np.uint8)
	cv.drawContours(mask,[cnt],0,255,-1)
	pixelpoints = np.transpose(np.nonzero(mask))
	#pixelpoints = cv.findNonZero(mask)
	return mask

def estimando_regiao(lista):
	r1 = 0
	r2 = 0
	r3 = 0
	for i in range(0,len(lista)):
		if (i <= 85):
			r1 = r1 + lista[i] 
		elif (i > 85 and i <= 170):
			r2 = r2 + lista[i]
		else :
			r3 = r3 + lista[i]

	r1 = (r1/85)*10
	r2 = (r2/85)*10
	r3 = (r3/85)*10

	if (r1 >= r2 and r1 >= r3):
		return (1,r1)
	elif (r2 >= r3):
		return (2,r2)	
	else:
		return (3,r3)

def relacionador_regioes(lista):
	escuro = []
	medio = []
	claro = []

	for i in range(0,len(lista)):
		if (lista[i][0] == 1):
			escuro.append(lista[i])
		
		elif (lista[i][0] == 2):
			medio.append(lista[i])
		else:
			claro.append(lista[i])

	return (escuro,medio,claro)



if __name__ == "__main__":
	origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_B/'
	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'

	for i in range(1,2):
		leitura = origem + '1.jpg'
		imagem = cv.imread(leitura)
		imagem_cor = cv.imread(leitura)
		imagem = cv.cvtColor(imagem,cv.COLOR_RGB2GRAY)
		
		mostrar_imagem(imagem)
		imagem = erosao(imagem)
		imagem_cinza = imagem

		mostrar_imagem(imagem) 
		imagem = thresholding(imagem)

		imagem = canny(imagem)
		mostrar_imagem(imagem)

		imagem,contorno,c = contornos(imagem)

		
		#for i in range(25,len(contorno)):
		#	imagem_cor = desenhando(imagem_cor,contorno[i])
		#	print (i)
		#	mostrar_imagem(imagem_cor)

		



		imagem_cinza = desenhando(imagem_cinza,contorno[25])
		mostrar_imagem(imagem_cinza)

		salvar(imagem_cor, 'Sombra')

		
		#for j in range(0,len(contorno)):
		#imagem_cor = desenhando(imagem_c,contorno[24])
		#mostrar_imagem(imagem_cor)
		
		listx = []
		listy = []
		for j in range(0,len(contorno[25])):
			listx.append(contorno[25][j][0][0])
			listy.append(contorno[25][j][0][1])

		limitesx = sorted(listx)
		limitesy = sorted(listy)

		limiteX,limiteX1 = limitesx[0],limitesx[len(limitesx)-1]
		limiteY,limiteY1 = limitesy[0],limitesy[len(limitesy)-1]

	print ('finalizado:',(limiteX,limiteX1,limiteY,limiteY1))

	pCentral = int(((limiteX+limiteX1)/2))
	print (pCentral)

	print ('----')

	x , x1, y, y1 =limites_externos(limiteX,limiteX1,limiteY,limiteY1)
	print (x,x1,y,y1)


	#Criando uma função das regiões em torno das regiões criticas
	listN = []
	listS = []
	listL = []
	listO = []
	for i in range(0,255):
		listN.append(0)
		listS.append(0)
		listL.append(0)
		listO.append(0)
	
	#if (x != x1  | limiteX != limiteX1 | y != y1  | limiteY != limiteY1):
	for i in range(x,x1):
		for j in range(y,limiteY):
			indice = imagem_cinza[i][j]
			listN[indice] = listN[indice] + 1 

	for i in range(x,x1):
		for j in range(y1,limiteY1):
			indice = imagem_cinza[i][j]
			listS[indice] = listS[indice] + 1 
		
	for i in range(limiteY,limiteY1):
		for j in range(x,limiteX):
			
			indice = imagem_cinza[i][j]
			listO[indice] = listO[indice] + 1 
		
	for i in range(limiteY,limiteY1):
		for j in range(limiteX1,x1):

			indice = imagem_cinza[i][j]
			listL[indice] = listL[indice] + 1 

	print (listN,'\n')
	print (listS,'\n')
	print (listL,'\n')
	print (listO,'\n')

	lista = []

	#Estimador de região

	regiao,media = estimando_regiao(listN)
	lista.append((regiao,media,'N'))
	
	regiao,media = estimando_regiao(listL)
	lista.append((regiao,media,'L'))
	
	regiao,media = estimando_regiao(listS)
	lista.append((regiao,media,'S'))
	
	regiao,media = estimando_regiao(listO)
	lista.append((regiao,media,'O'))
	
	print(lista)

	#Relacionadr de regiões, para indicar quais regiões que os resultados podem estar mais proximos entre si
	escuro,medio,claro = relacionador_regioes(lista)

	print (escuro)
	print (medio)
	print (claro)