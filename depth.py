from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv
import math


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
    try:
    	c =(4*math.pi*cv.contourArea(contornos))/((cv.arcLength(contornos,True)**2))
    	if c == None:
        	c = 0.0
    	return c
    except:
    	return 0






def mostrar_imagem(imagem):
	cv.imshow('Imagem',imagem)
	cv.waitKey(0)
	cv.destroyAllWindows()

def mostrar_imagens(imagem1,imagem2,imagem3,imagem4):
	plt.subplot(221), plt.imshow(imagem1, 'gray')
	plt.subplot(222), plt.imshow(imagem2,'gray')
	plt.subplot(223), plt.imshow(imagem3, 'gray')
	plt.subplot(224), plt.imshow(imagem4,'gray')
	plt.show()

	return 0

def salvar(imagem, i,j,flag):
	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	final = destino + flag + 'Contorno_' + str(i) + '.' + str(j) + '.png'

	cv.imwrite(final,imagem)

def limpar(imagem):
	dst = cv.fastNlMeansDenoising(imagem,None,10,7,21)
	return dst

def equalizar(imagem):
	clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(5,5))
	cl1 = clahe.apply(imagem)
	return cl1

def erosao(imagem):
	kernel = np.ones((10,10),np.uint8)
	erosao = cv.erode(imagem,kernel,iterations = 1) #VERIFICAR ESSA ALTERALÇÃO DO CL1 POR DST
	return erosao

def thresholding(imagem):
	ret,th = cv.threshold(imagem,0,255,cv.THRESH_BINARY + cv.THRESH_OTSU)
	th2 = cv.adaptiveThreshold(imagem,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,11,2)
	th3 = cv.adaptiveThreshold(imagem,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)
	return (th,th2,th3)

def canny(imagem):
	teste = cv.Canny(imagem,100,200)
	return teste

def contornos(imagem):
	imagem2, contornos, hierarquia = cv.findContours(imagem, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
	return (imagem2,contornos,hierarquia)

def desenhando(imagem,contornos):
	cv.drawContours(imagem,[contornos],0,(0,0,255),3)
	return imagem

def limites (lista):
	listaX = []
	listaY = []

	for i in range(0,4):
		x , y = lista[i]
		listaX.append(x)
		listaY.append(y)

	limites = sorted(listaX)
	limites2 = sorted(listaY)

	x1,x2 = limites[0],limites[3]
	y1,y2 = limites2[0],limites2[3]
	
	return x1,y1



if __name__ == "__main__":
	origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/3_SubImagens/'
	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	especial = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_B/'


	listandoContornos = []
	for i in range(1,20):
		leitura = origem + str(i) + '.png'
		cor = cv.imread(leitura)
		
		imagem = cv.cvtColor(cor,cv.COLOR_RGB2GRAY)
		
		height, width = cor.shape[:2]
		#print (height, width)
		area_imagem = height * width

		#Os passos a seguir são somente para um pequeno tratamento (novamente) na sub-imagem
		imagem=limpar(imagem)
		#mostrar_imagem(imagem)

		imagem=equalizar(imagem)
		#mostrar_imagem(imagem)

		imagem=erosao(imagem)
		#mostrar_imagem(imagem)

		imagema,imagemb,imagemc=thresholding(imagem)
		#mostrar_imagem(imagem)
		#mostrar_imagem(imagema)

		imagem=canny(imagema)
		#mostrar_imagem(imagem)

		imagema,imagemb,imagemc = contornos(imagem)
		#-----------------------------------------------------------------------------------

		for j in range(0,len(imagemb)):
			subImagem = cor.copy()
			teste = imagemb[j]

			quadrado = cv.minAreaRect(teste)
			novos_contornos = cv.boxPoints(quadrado)
			novos_contornos = np.int0(novos_contornos)

			area_final = (area(novos_contornos)/area_imagem)
			
			if(area_final >= 0.01):
				#print ('Imagem atual:')
				
				#print ('Comprimento:',comprimento(teste))
				#print ('Altura:',altura(teste))
				#print ('Area:',area_final)
				#print ('largura:',largura(teste))
				#print ('Circularidade:',circularidade(teste))
				
				imagem_aux = desenhando(subImagem,novos_contornos)
				#mostrar_imagem(imagem_aux)
				salvar(imagem_aux,i,j,'4_Contornos/')
				
				listandoContornos.append((novos_contornos,i))
			
	leitura = 0
	listXY = []
	listaFinal = []
	
	limite = len(listandoContornos)
	#print ('TAMANHO', limite)
	
	arq = open(destino + '4_Contornos/' + 'lista.txt', 'r')

	texto = arq.read()
	lista = list(eval(texto.split()[0]))

	leitura = especial + '3' + '.jfif'

	cor = cv.imread(leitura)
	#mostrar_imagem(cor)

	cor1 = cor.copy()

	#AQUI COMEÇA A COMPARAÇÃO COM OS VALORES DA LISTA ENCONTRADA AQUI E DA LISTA ORIGINAL
	inicioJ = 0
	for i in range(0,len(lista)):	
		for j in range(inicioJ,limite):
			if (lista[i][2] == listandoContornos[j][1]):
				menorX,menorY = limites(lista[i][0])

				x = menorX + listandoContornos[j][0][0][0] 
				y = menorY + listandoContornos[j][0][0][1] + 256

				x1 = menorX + listandoContornos[j][0][1][0] 
				y1 = menorY + listandoContornos[j][0][1][1] + 256

				x2 = menorX + listandoContornos[j][0][2][0] 
				y2 = menorY + listandoContornos[j][0][2][1] + 256

				x3 = menorX + listandoContornos[j][0][3][0] 
				y3 = menorY + listandoContornos[j][0][3][1] + 256

				contorno = np.array([[x,y],[x1,y1],[x2,y2],[x3,y3]])
				imagem_finalizada = desenhando(cor1,contorno)
				#mostrar_imagem(imagem_finalizada)
				
			else:
				inicioJ = j
				#print ('finalziaJ')
				break

	salvar(imagem_finalizada,lista[0][1],0,'5_Finalizadas/')
	print ('aqui')

		
	arq.close()