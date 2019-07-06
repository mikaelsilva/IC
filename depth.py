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

	#BLOCO EM ANALISE -----------------------------------------
	opening = cv.morphologyEx(imagem, cv.MORPH_OPEN,(5,5))	 
	#----------------------------------------------------------

	erosao = cv.erode(opening,kernel,iterations = 1) #VERIFICAR ESSA ALTERALÇÃO DO CL1 POR DST

	return erosao

def thresholding(imagem):
	ret,th = cv.threshold(imagem,0,255,cv.THRESH_BINARY + cv.THRESH_OTSU)
	#th2 = cv.adaptiveThreshold(imagem,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,11,2)
	#th3 = cv.adaptiveThreshold(imagem,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)

	return th

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

	x1,x2 = limites[0],limites[len(limites)-1]
	y1,y2 = limites2[0],limites2[len(limites2)-1]
	
	return x1,y1,x2,y2

def limites_externos(height,width,x,y,x1,y1):

	if ( x > 20 ):
		x -= 20
	else:
		if (x - int(x/2) >= 0):
			x -= int(x/2)
		else:
			x = x

	if ( (width-1) - x1 > 20 ):
		x1 += 20
	else:
		x1 += int(((width-1) - x1)/2)

	if ( y > 20 ):
		y -= 20
	else:
		if (y - int(y/2) >= 0):
			y -= int(y/2)
		else:
			y = y
		
	if ( int((height-1) - y1) > 20 ):
		y1 += 20
	else:
		y1 += int(((height-1) - y1)/2)

	return x,y,x1,y1

def definindo_regiao(y,y1,x,x1,imagem):
	lista = []
	for i in range(0,255):
		lista.append(0)

	#print ('Limites:','[',x,'-',x1,']','|','[',y,'-',y1,']')
	if(x == x1 | y == y1):
		return (lista)
	else:
		for i in range(x,x1-1):
			for j in range(y, y1-1):
				indice = imagem[i][j]
				lista[indice] += 1
		#print ('lista: ',lista) 
		return (lista)

#VERIFICAR COMO ESTIMAR DE FORMA CORRETA A MEDIA DOS VALORES PARA CADA REGIÃO
def estimando_regiao(lista):
	r1 = 0
	re1 = 1
	r2 = 0
	re2 = 1
	r3 = 0
	re3 = 1

	for i in range(0,len(lista)-1):
		if (i <= 85):
			if(lista[i] != 0):
				r1 += 3*lista[i]
				re1 += 3
			
		elif (i > 85 and i <= 170):
			if(lista[i] != 0):
				r2 += lista[i]
				re2 += 3
		else:
			if(lista[i] != 0):
				r3 += 1*lista[i]
				re3 += 3

	r1 = (r1/re1)
	r2 = (r2/re2)
	r3 = (r3/re3)

	if(r1 == r2 == r3 == 0):
		return ('Indefinida',0.0)
	elif (r1 >= r2 and r1 >= r3):
		return ('Escuro',[r1,r2,r3])
	elif (r2 >= r1 and r2 >= r3):
		return ('Cinza',[r1,r2,r3])
	else:
		return ('Claro',[r1,r2,r3])

def relacionando_regiao(lista):
	listaEs = []
	listaCi = []
	listaCl = []

	for i in range(0,len(lista)):
		if (lista[i][1] == 'Escuro'):
			listaEs.append(lista[i])
		
		if(lista[i][1] == 'Cinza'):
			listaCi.append(lista[i])
		
		if(lista[i][1] == 'Claro'):
			listaCl.append(lista[i])


	for i in range(0,len(listaEs)):
		if(listaEs[i][0] == 'P'):
			if(len(listaEs) > 1):
				return len(listaEs)
			else:
				return 0
		
	for i in range(0,len(listaCi)):
		if(listaCi[i][0] == 'P'):
			if(len(listaCi) > 1):
				return len(listaCi)
			else:
				return 0

	for i in range(0,len(listaCl)):
		if(listaCl[i][0] == 'P'):
			if(len(listaCl) > 1):
				return len(listaCl)
			else:
				return 0

	return 0


if __name__ == "__main__":
	origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/3_SubImagens/'
	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	especial = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_B/'


	listandoContornos = []
	imagem_finalizada = np.ones((256, 512, 3)) * 255 #imagem 400x300, com fundo branco e 3 canais para as cores

	for i in range(8,10):
		leitura = origem + str(i) + '.png'
		cor = cv.imread(leitura)
		
		imagem = cv.cvtColor(cor,cv.COLOR_RGB2GRAY)

		height, width = cor.shape[:2]

		area_imagem = height * width
		print ("---", i)
		#Os passos a seguir são somente para um pequeno tratamento (novamente) na sub-imagem
		imagem = limpar(imagem)
		#mostrar_imagem(imagem)

		#imagem = equalizar(imagem)
		#mostrar_imagem(imagem)

		imagem = erosao(imagem)
		imagem_cinza = imagem
		mostrar_imagem(imagem)

		imagema = thresholding(imagem)
		#mostrar_imagem(imagem)
		#mostrar_imagem(imagema)

		imagem = canny(imagema)
		#mostrar_imagem(imagem)

		imagema,imagemb,imagemc = contornos(imagem)
		#-----------------------------------------------------------------------------------


		#Definindo os contos e salvando em uma imagem e em uma lista
		#Verificar de que forma o algoritmo pode "reduzir" o número de imagens "inadequadas" que passam por ele 
		#for j in range(0,len(imagemb)): #VERIFICAR ESSE imagemb, há muito valores repetiso por algum motivo
		for j in range(0,1):
			subImagem = cor.copy()
			teste = imagemb[j]

			quadrado = cv.minAreaRect(teste)
			novos_contornos = cv.boxPoints(quadrado)
			novos_contornos = np.int0(novos_contornos)

			#Criando um script para tentar identificar buracos,manchas, rachaduras,
			#---------------------------------------------------------------------------------------------------------------------
			print('---------------------------------------------------------------------------------------------------------------------')	
			print ("Definindo regiões e seus valores")
			lxi0, lyi0, lxi1, lyi1 = limites(novos_contornos)
			#print ('lxi0:',lxi0,'lyi0:',lyi0,'lxi1:',lxi1,'lyi1:',lyi1)

			lxe0, lye0, lxe1, lye1 = limites_externos(height,width,lxi0,lyi0,lxi1,lyi1)

			print (height,width)
			#print ('lxi0:',lxi0,'lyi0:',lyi0,'lxi1:',lxi1,'lyi1:',lyi1)
			#print ('lxe0:',lxe0,'lye0:',lye0,'lxe1:',lxe1,'lye1:',lye1)

			listaP = []
			listaP = definindo_regiao(lxi0,lxi1,lyi0,lyi1,imagem_cinza)
			#subImagem[lyi0:lyi1, lxi0:lxi1] = (0, 0, 255)
			#mostrar_imagem(subImagem)
			#print (listaP)

			listaN = []
			listaN = definindo_regiao(lxi0,lxi1,lye0,lyi0,imagem_cinza)
			
			listaS = []
			listaS = definindo_regiao(lxi0,lxi1,lyi1,lye1,imagem_cinza)
			#subImagem[lyi1:lye1, lxi0:lxi1] = (100, 0, 255)
			#mostrar_imagem(subImagem)
			
			listaL = []
			listaL = definindo_regiao(lxi1,lxe1,lyi0,lyi1,imagem_cinza)

			listaO = []
			listaO = definindo_regiao(lxe0,lxi0,lyi0,lyi1,imagem_cinza)
			#subImagem[lyi0:lyi1, lxe0:lxi0] = (0, 100, 255)
			#mostrar_imagem(subImagem)

			listaNO = []
			listaNO = definindo_regiao(lxe0,lxi0,lye0,lyi0,imagem_cinza)

			listaNL = []
			listaNL = definindo_regiao(lxi1,lxe1,lye0,lyi0,imagem_cinza)

			listaSL = []
			listaSL = definindo_regiao(lxi1,lxe1,lyi1,lye1,imagem_cinza)

			listaSO = []
			listaSO = definindo_regiao(lxe0,lxi0,lyi1,lye1,imagem_cinza)
			#subImagem[lyi1:lye1, lxe0:lxi0] = (100, 100, 255)
			#mostrar_imagem(subImagem)
			#listaTotal = [listaP,listaNO,listaN,listaNL,listaL,listaSL,listaS,listaSO,listaO]

			#print('----------------------------------------------------------------------------------------------------------------------')
			
			print ('Definindo media das regiões')
			listaRegiao = []
			media = []

			regiao, media = estimando_regiao(listaP)
			listaRegiao.append(('P',regiao,media))
			#print ('Principal:',regiao,'\n','Media de:',media)

			regiao, media = estimando_regiao(listaN)
			listaRegiao.append(('N',regiao,media))
			#print ('Norte:',regiao,'\n','Media de:',media)

			regiao, media = estimando_regiao(listaS)
			listaRegiao.append(('S',regiao,media))
			#print ('Sul:',regiao,'\n','Media de:',media)

			regiao, media = estimando_regiao(listaL)
			listaRegiao.append(('L',regiao,media))
			#print ('Leste:',regiao,'\n','Media de:',media)

			regiao, media = estimando_regiao(listaO)
			listaRegiao.append(('O',regiao,media))
			#print ('Oeste:',regiao,'\n','Media de:',media)

			regiao, media = estimando_regiao(listaNO)
			listaRegiao.append(('NO',regiao,media))

			regiao, media = estimando_regiao(listaNL)
			listaRegiao.append(('NL',regiao,media))

			regiao, media = estimando_regiao(listaSL)
			listaRegiao.append(('SL',regiao,media))

			regiao, media = estimando_regiao(listaSO)
			listaRegiao.append(('SO',regiao,media))

			#print ('Listando:' , listaRegiao)

			#print('-----------------------------------------------------------------------------------------------------------------------')
			print ('Relacionando valores de regiões')

			valor = relacionando_regiao(listaRegiao)
			if (valor > 1):
				print ('Existe regiões com valores aproximados')
			else:
				print ('Possivel buraco')

			#print('-----------------------------------------------------------------------------------------------------------------------')

			#print (listaRegiao)


			#---------------------------------------------------------------------------------------------------------------------
			area_final = (area(novos_contornos)/area_imagem)
			
			if(area_final >= 0.01 and valor <= 1):
				#print ('Imagem atual:')
				
				#print ('Comprimento:',comprimento(teste))
				#print ('Altura:',altura(teste))
				#print ('Area:',area_final)
				#print ('largura:',largura(teste))
				#print ('Circularidade:',circularidade(teste))
				
				imagem_aux = desenhando(subImagem,novos_contornos)
				mostrar_imagem(imagem_aux)
				salvar(imagem_aux,i,j,'4_Contornos/')
				listandoContornos.append((novos_contornos,i))
			
	leitura = 0
	listXY = []
	listaFinal = []
	
	limite = len(listandoContornos)
	arq = open(destino + '4_Contornos/' + 'lista' + str(12) + '.txt', 'r')

	texto = arq.read()
	lista = list(eval(texto.split()[0]))

	leitura = especial + str(lista[0][1]) + '.jfif'
	imagem_aux = cv.imread(leitura)




	#AQUI COMEÇA A COMPARAÇÃO COM OS VALORES DA LISTA ENCONTRADA AQUI E DA LISTA ORIGINAL
	inicioJ = 0
	for i in range(0,len(lista)):
		print ("IMAGEM_FINALIZADA 1") 	
		for j in range(inicioJ,limite):
			if (lista[i][2] == listandoContornos[j][1]):
				menorX,menorY,lix,lix2 = limites(lista[i][0])

				x = menorX + listandoContornos[j][0][0][0] 
				y = menorY + listandoContornos[j][0][0][1] + 256

				x1 = menorX + listandoContornos[j][0][1][0] 
				y1 = menorY + listandoContornos[j][0][1][1] + 256

				x2 = menorX + listandoContornos[j][0][2][0] 
				y2 = menorY + listandoContornos[j][0][2][1] + 256

				x3 = menorX + listandoContornos[j][0][3][0] 
				y3 = menorY + listandoContornos[j][0][3][1] + 256

				contorno = np.array([[x,y],[x1,y1],[x2,y2],[x3,y3]])
				imagem_finalizada = desenhando(imagem_aux,contorno)
				#mostrar_imagem(imagem_finalizada)
				print ("IMAGEM_FINALZIADA 2")
				
			else:
				print ("IMAGEM FINALIZADA 3")
				inicioJ = j
				j = limite

	print (lista[0][1])
	salvar(imagem_finalizada,lista[0][1],0,'5_Finalizadas/')
	print ('Finalizado')

	arq.close()	

#Estado
'''
	A verficiação ao redor do buraco está quase funcionando, falta verificar os casos em que os limites_da_area_externa ficam fora do 
		limite da imagem_original, mas para os que funciona e o ambiente é mais controlado (rua sem muitos ruídos), o resultado se
		apresenta de forma a ajudar o resultado final

	Verificar a anomalia de imagemb que termina por resultar em imagens duplicadas

	Verificar como é salvo os contornos finais

	Verificar como será o vetor utilizado para treinar a IA e que tipo de IA de classificção poderá ser utilizada
'''