from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv
import math
import os

#Verificada e deixando apenas em função da erosao
def reducao_ruido(num,imagem):
	kernel = np.ones((10,10),np.uint8)
	#dst = cv.fastNlMeansDenoising(imagem,None,10,7,21)

	erosao = cv.erode(imagem,kernel,iterations = 1)

	pasta = '1_Especial'
	nome = str(num) + '.1'
	salvar(pasta,erosao,nome)

	return erosao

#Verificada
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

def reanalizando_contornos(imagem,novos_contornos,num_imagem,num):
	listaX=[]
	listaY=[]

	#print ("VALORES: ")
	for i in range(0,4):
		x,y = novos_contornos[i]
		#print (x,y)
		listaX.append(y)
		listaY.append(x)
	
	x1,x2 = min(listaX),max(listaX)
	y1,y2 = min(listaY),max(listaY)

	if (x1 != x2 and y1 != y2 and x1 >= 0 and x2 >= 0 and y1 >= 0 and y2 >= 0):
		imagem_fatia = imagem[x1:x2,y1:y2] #Aqui é feito um recorte em relação a area do contorno analisado
		mostrar_imagem(imagem_fatia)

		#Esse calculo é feito para que a imagemFatia contenha uma area significativa em relação a imagem original
		height, width = imagem_fatia.shape[:2]
		area_total = 256*512
		area_subImagem = height * width 
		area_final = (area_subImagem / area_total) 

		#print (area_final)
		mostrar_imagem(imagem_fatia)

		#VERIFICAR A POSSIBILIDADE DO RESIZE NA IMAGEM "28/10/2019 00:00"
		#res = cv.resize(imagem_fatia,(10*width, 10*height), interpolation = cv.INTER_CUBIC)
		#mostrar_imagem(res)

		if (area_final >= 0.01):
			pasta = '3_SubImagens'
			nome = str(num_imagem) + '.' + str(num)
			salvar(pasta,imagem_fatia,nome)
			return 1
			
	imagem_fatia = 0

	return 0

#MELHOR ESSE TRECHO DE CÓDIGO , ASSIM COMO RENOMEAR imagem1,2,3 .. . . . . . . . . .... . .  ..  . . .
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

		#VERIFICAR A RETIRADA DA CONDIÇÃO DE "largura e altura" 28/10/2019 23:50
		if (area(novos_contornos) >  100 and largura(novos_contornos) > 15 and altura(novos_contornos) > 15):
			print ("A1: %f | P1: %f | W1: %f | H1: %f" %(area(teste),comprimento(teste),largura(teste),altura(teste)))
			print ("A2: %f | P2: %f | W2: %f | H2: %f" %(area(novos_contornos),comprimento(novos_contornos),largura(novos_contornos),altura(novos_contornos)))

			#cv.drawContours(imagem_contorno,[teste],0,(255,0,0),3)
			#cv.drawContours(imagem_quadrado,[novos_contornos],0,(0,255,0),3)

			#mostrar_imagem(imagem_contorno)
			#mostrar_imagem(imagem_quadrado)

			if (reanalizando_contornos(imagem,novos_contornos,num_imagem,num) == 1):

				cv.drawContours(imagem3,[novos_contornos],0,(0,0,255),3)
				pasta = '2_Tratadas'
				nome = str(num_imagem) + '.' + str(num)
				salvar(pasta,cv.drawContours(imagem_quadrado,[novos_contornos],0,(0,255,0),3),nome)
				#nome = 0
				lista.append([novos_contornos,num_imagem,num])
				num +=1
		#print ("--------------------------------------------------------------------------------------------")


	imagem4 = imagem.copy()
	cv.drawContours(imagem4,contornos,-1,(0,255,255),3)

	pasta = '1_Especial'
	nome = str(num_imagem) + '.2'
	salvar(pasta,imagem_canny,nome)

	pasta = '1_Especial'
	nome = str(num_imagem) + '.3'
	salvar(pasta,imagem3,nome)

	pasta = '1_Especial'
	nome = str(num_imagem) + '.4'
	salvar(pasta,imagem4,nome)

	return imagem,num,lista

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

#ALTERAR O nome PARA PASTA
#ALTERAR pasta PARA NUMERO já em STRING
def salvar(pasta,imagem,nome):
	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	final = destino + pasta + '/' + nome + '.png'

	cv.imwrite(final,imagem)

	return 0


if __name__ == "__main__":

	origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Origem/'
	origem2 = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Origem_Fake/'

	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	openn = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'

	for _, _, arquivo in os.walk(origem):
		pass

	#print (arquivo)
	#print (origem + arquivo[0])

	for img in arquivo:
		lista = [[]]

		i = int(img[0:-5])
		imagem = cv.imread(origem+img)

		#Recortando imagem
		imagem = imagem[256:512,0:512]
		mostrar_imagem(imagem)

		imagem_cinza = cv.cvtColor(imagem,cv.COLOR_RGB2GRAY)
		mostrar_imagem(imagem_cinza)

		imagem_tratada = reducao_ruido(i,imagem_cinza)
		mostrar_imagem(imagem_tratada)
		
		imagem_canny = encontrando_contornos(imagem_tratada)
		mostrar_imagem(imagem_canny)

		#VERIFICAR A FUNÇÃO definindo_caracteristicas()
		imagem_finalizada,quant_img_salvas,lista = definindo_caracteristicas(imagem,imagem_canny,i,lista)
		#mostrar_imagem(imagem_finalizada)

		print("TERMINOU")
	
		#arq2 = open('lista' +str(i) +'.txt',"r")
		#a = arq2.read()
		#print(a)
		#arq2.close()

		try:
			arq = open('lista' +str(i) +'.txt', 'w')
			del lista[0]
			saida = str(lista).replace('array','').replace('(','').replace(')','').replace('\n','').replace(' ','')
			arq.write(saida)
			
			arq.close()


		except Exception as e:
			print ("ERRO:",img)
			pass