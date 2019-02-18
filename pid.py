import numpy as np
import cv2 as cv
import math
from matplotlib import pyplot as plt 


def reducao_ruido(num,imagem,pasta):
	kernel = np.ones((10,10),np.uint8)

	clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(15,15))
	cl1 = clahe.apply(imagem)

	erosao = cv.erode(cl1,kernel,iterations = 1)

	clahe2 = cv.createCLAHE(clipLimit=2.0, tileGridSize=(5,5))
	cl2 = clahe2.apply(erosao)

	nome = 'Imagem_' + str(pasta)
	salvar(nome,cl2,pasta)

	return cl2

def encontrando_contornos(imagem):
	imagem2 = cv.Canny(imagem,100,200)

	return imagem2          

def area(contornos):
    a = cv.contourArea(contornos)
    if a == None:
        a = 0.0
    return a

def comprimento(contornos):
    c = cv.arcLength(contornos,True)
    if c == None:
        c = 0.0
    return c

def largura(contornos):
    x,y,w,h = cv.boundingRect(contornos)
    if w == None:
        w = 0.0
    return w

def altura(contornos):
    x,y,w,h = cv.boundingRect(contornos)
    if h == None:
       h = 0.0
    return h

def circularidade(contornos):
    c =(4*math.pi*cv.contourArea(contornos))/((cv.arcLength(contornos,True)**2))
    if c == None:
        c = 0.0
    return c

'''
#Ambas as funções estão sendo alteradas para buscar um melhor resultado na identificação de buracos, manchas, rachaduras e outros....
def buraco(imagem_fatia,imagem):
	cinza = cv.cvtColor(imagem,cv.COLOR_RGB2GRAY)
	kernel = np.ones((10,10),np.uint8)

	clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(15,15))
	cl1 = clahe.apply(cinza)

	erosao = cv.erode(cl1,kernel,iterations = 1)

	ret, th = cv.threshold(erosao,50,255,cv.THRESH_BINARY + cv.THRESH_OTSU)


	mostrar_imagens(imagem,cinza,erosao,th)

	return 0

OBS:Será que é possivel pegar um bloco da imagem e verificar se ela possui alguma similaridade em outras regiões
		dela?
	Talvez seja possivel identificar que uma região é uma sombra se ela puder ser "identificada" em outras partes
		da imagem, pelo menos com uma porcentagem de "igualdade" 


def reanalizando_contornos(imagem,novos_contornos,num):
	listaX=[]
	listaY=[]
	print ("VALORES: ")
	for i in range(0,4):
		x,y = novos_contornos[i]
		print (x,y)
		listaX.append(y)
		listaY.append(x)
		
	limites = sorted(listaX)
	limites2 = sorted(listaY)

	x1,x2 = limites[0],limites[3]
	y1,y2 = limites2[0],limites2[3]

	if (x1 != x2 and y1 != y2 and x1 >= 0 and x2 >= 0 and y1 >= 0 and y2 >= 0):
		imagem_fatia = imagem[limites[0]:limites[3],limites2[0]:limites2[3]] #Aqui é feito um recorte quadratico em relação a area do contorno analisado
		#mostrar_imagem(imagem_fatia)

		#Aqui é feita uma pequena modificação na imagem recortada para que ela fique um pouco maior
		height, width = imagem_fatia.shape[:2]
		res = cv.resize(imagem_fatia,(10*width, 10*height), interpolation = cv.INTER_CUBIC)
		#mostrar_imagem(res)
		#num=str(num)
		#salvar(num,res)
		buraco(imagem_fatia,res)



	imagem_fatia = 0

	return 0
'''


def definindo_caracteristicas(imagem, imagem_canny,pasta):
	imagem2, contornos, hierarquia = cv.findContours(imagem_canny, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
 	
	imagem3 = imagem.copy()

	for i in range(len(contornos)):
		teste = contornos[i]
		imagem_contorno = imagem.copy()
		imagem_quadrado = imagem.copy()

		quadrado = cv.minAreaRect(teste)
		novos_contornos = cv.boxPoints(quadrado)
		novos_contornos = np.int0(novos_contornos)
		
		if (area(novos_contornos) >  200 and comprimento(novos_contornos) > 15 and largura(novos_contornos) > 15 and altura(novos_contornos) > 15):
			#print ("A1: %f | P1: %f | W1: %f | H1: %f" %(area(teste),comprimento(teste),largura(teste),altura(teste)))
			#print ("A2: %f | P2: %f | W2: %f | H2: %f" %(area(novos_contornos),comprimento(novos_contornos),largura(novos_contornos),altura(novos_contornos)))

			cv.drawContours(imagem_contorno,[teste],0,(255,0,0),3)
			cv.drawContours(imagem_quadrado,[novos_contornos],0,(0,255,0),3)

			#mostrar_imagem(imagem_contorno)
			#mostrar_imagem(imagem_quadrado)
			
			#reanalizando_contornos(imagem,novos_contornos,i)

			cv.drawContours(imagem3,[novos_contornos],0,(0,0,255),3)

			nome = str(i)
			salvar(nome,cv.drawContours(imagem_quadrado,[novos_contornos],0,(0,255,0),3),pasta)
			nome = 0
	
		#print ("--------------------------------------------------------------------------------------------")


	imagem4 = imagem.copy()
	cv.drawContours(imagem4,contornos,-1,(0,255,255),3)

	nome = 'Imagem_' + str(pasta+1)
	salvar(nome,imagem_canny,pasta)

	nome = 'Imagem_' + str(pasta+2)
	salvar(nome,imagem3,pasta)

	nome = 'Imagem_' + str(pasta+3)
	salvar(nome,imagem4,pasta)
		          
	return imagem

def mostrar_imagem(imagem):
	
	cv.imshow('Imagem',imagem) 
	cv.waitKey(0)
	cv.destroyAllWindows()
	
	return 0

def mostrar_imagens(imagem1,imagem2,imagem3,imagem4):
	plt.subplot(221), plt.imshow(imagem1, 'gray')
	plt.subplot(222), plt.imshow(imagem2,'gray')
	plt.subplot(223), plt.imshow(imagem3, 'gray')
	plt.subplot(224), plt.imshow(imagem4,'gray')
	plt.show()

	return 0

def salvar(num,imagem,pasta):
	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_P/'
	final = destino + str(pasta) + '/' + num + '.png'

	cv.imwrite(final,imagem)

	return 0


if __name__ == "__main__":
 
	origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_B/'
	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_P/'

	for i in range(1,2):
		leitura = origem + str(i) + '.JPG'
		imagem = cv.imread(leitura)

		imagem_cinza = cv.cvtColor(imagem,cv.COLOR_RGB2GRAY)

		imagem_tratada = reducao_ruido(i,imagem_cinza,i)
		imagem_canny = encontrando_contornos(imagem_tratada)

		imagem_finalizada = definindo_caracteristicas(imagem,imagem_canny,i)

		leitura = 0