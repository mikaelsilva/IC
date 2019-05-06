from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv
import math
import os


def reducao_ruido(num,imagem,pasta):
	kernel = np.ones((10,10),np.uint8)
	##dst = cv.fastNlMeansDenoising(imagem,None,10,7,21)

	clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(15,15))
	cl1 = clahe.apply(imagem)

	erosao = cv.erode(cl1,kernel,iterations = 1)

	clahe2 = cv.createCLAHE(clipLimit=2.0, tileGridSize=(5,5))
	cl2 = clahe2.apply(erosao)

	nome = '1_Especial'
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
		imagem_fatia = imagem[limites[0]:limites[3],limites2[0]:limites2[3]] #Aqui é feito um recorte em relação a area do contorno analisado
		#mostrar_imagem(imagem_fatia)

		#Esse calculo é feito para que a imagemFatia contenha uma area significativa em relação a imagem original
		height, width = imagem_fatia.shape[:2]
		area_total = 256*512
		area_subImagem = height * width 
		area_final = (area_subImagem / area_total) 

		#print (area_final)
		#mostrar_imagem(imagem_fatia)
		res = cv.resize(imagem_fatia,(10*width, 10*height), interpolation = cv.INTER_CUBIC)

		if (area_final >= 0.01):
			nome = '3_SubImagens'
			salvar(nome,imagem_fatia,num)
			return 1
			
	imagem_fatia = 0

	return 0

def definindo_caracteristicas(imagem, imagem_canny,num_imagem,lista):
	num = 1
	
	imagem2, contornos, hierarquia = cv.findContours(imagem_canny, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
	imagem3 = imagem.copy()

	for i in range(len(contornos)):
		teste = contornos[i]
		imagem_contorno = imagem.copy()
		imagem_quadrado = imagem.copy()

		quadrado = cv.minAreaRect(teste)
		novos_contornos = cv.boxPoints(quadrado)
		novos_contornos = np.int0(novos_contornos)

		if (area(novos_contornos) >  100 and largura(novos_contornos) > 15 and altura(novos_contornos) > 15):
			#print ("A1: %f | P1: %f | W1: %f | H1: %f" %(area(teste),comprimento(teste),largura(teste),altura(teste)))
			#print ("A2: %f | P2: %f | W2: %f | H2: %f" %(area(novos_contornos),comprimento(novos_contornos),largura(novos_contornos),altura(novos_contornos)))

			cv.drawContours(imagem_contorno,[teste],0,(255,0,0),3)
			cv.drawContours(imagem_quadrado,[novos_contornos],0,(0,255,0),3)

			#mostrar_imagem(imagem_contorno)
			#mostrar_imagem(imagem_quadrado)

			if (reanalizando_contornos(imagem,novos_contornos,num) == 1):

				cv.drawContours(imagem3,[novos_contornos],0,(0,0,255),3)
				nome = '2_Tratadas'
				salvar(nome,cv.drawContours(imagem_quadrado,[novos_contornos],0,(0,255,0),3),num)
				nome = 0
				lista.append([novos_contornos,num_imagem,num])
				num +=1
		#print ("--------------------------------------------------------------------------------------------")


	imagem4 = imagem.copy()
	cv.drawContours(imagem4,contornos,-1,(0,255,255),3)

	nome = '1_Especial'
	salvar(nome,imagem_canny,num_imagem+1)

	nome = '1_Especial'
	salvar(nome,imagem3,num_imagem+2)

	nome = '1_Especial'
	salvar(nome,imagem4,num_imagem+3)

	return imagem,num

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

def salvar(nome,imagem,pasta):
	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	final = destino + nome + '/' + str(pasta) + '.png'

	cv.imwrite(final,imagem)

	return 0


if __name__ == "__main__":

	origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_B/'
	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'

	
	lista = [[]]
	for i in range(3,4):
		leitura = origem + str(i) + '.jfif'
		img = cv.imread(leitura)

		#Recortando imagem
		imagem = img[256:512,0:512]
		#mostrar_imagem(imagem)i9

		mostrar_imagem(img)
		mostrar_imagem(imagem)

		imagem_cinza = cv.cvtColor(imagem,cv.COLOR_RGB2GRAY)
		#mostrar_imagem(imagem_cinza)
		imagem_tratada = reducao_ruido(i,imagem_cinza,i)
		#mostrar_imagem(imagem_tratada)
		imagem_canny = encontrando_contornos(imagem_tratada)
		#mostrar_imagem(imagem_canny)
		imagem_finalizada,quant_img_salvas = definindo_caracteristicas(imagem,imagem_canny,i,lista)
		mostrar_imagem(imagem_finalizada)

		print (lista)
		#print (lista, ' ---- ---- ' ,str(lista[1][0][0][0]))
		arq = open(destino + '4_Contornos/' + 'lista.txt', 'w')
		
		arq.write('[[')
		for i in range(1,quant_img_salvas):
			arq.write('[')
			for x in range(0,4):
				arq.write('[')
				arq.write(str(lista[i][0][x][0]))
				arq.write(',')
				arq.write(str((lista[i][0][x][1])))
				arq.write(']')
				
				if (x < 3):
					arq.write(',')

			arq.write('],')
			arq.write(str((lista[i][1])))
			arq.write(',')
			arq.write(str((lista[i][2])))
			if (i < quant_img_salvas-1):
				arq.write('],[')
			else:
				arq.write(']')

		arq.write(']')
		arq.close()
		leitura = 0