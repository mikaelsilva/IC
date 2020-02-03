from matplotlib import pyplot as plt
from random import randint
import pandas as pd
import numpy as np
import cv2 as cv
import math
import os



#A relação entre as duas areas ocorre de forma a identificar qual a área da subimagem em relação a imagem maior/anterior
#(Sub_Imagem / Imagem_Original) , (SubSub_Imagem / Sub_Imagem) ,(SubSub_Imagem / Imagem_Original)
def area_interesse(area_Imagem,area_SubImagem):

	try:
		area = area_SubImagem / area_Imagem 
		area = area_SubImagem*100
		return area
	except:
		return -1

#Nome das funções auto-explicativas
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

def thresholding(imagem):
	ret,th = cv.threshold(imagem,0,255,cv.THRESH_BINARY + cv.THRESH_OTSU)
	#th2 = cv.adaptiveThreshold(imagem,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,11,2)
	#th3 = cv.adaptiveThreshold(imagem,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)

	return th

def canny(imagem):
	teste = cv.Canny(imagem,100,200)
	return teste

def contornos(imagem):
	contornos, hierarquia = cv.findContours(imagem, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
	return (contornos,hierarquia)

def desenhando(imagem,contornos):
	cv.drawContours(imagem,[contornos],0,(0,0,255),3)
	return imagem

def limpar(imagem):
	dst = cv.fastNlMeansDenoising(imagem,None,10,7,21)
	return dst

def equalizar(imagem):
	clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(5,5))
	cl1 = clahe.apply(imagem)
	return cl1
#----------------------------------------------------------------

#VERIFICADA, RESPONSAVEL POR RECEBER A SUB_IMAGEM CINZA E GERAR UMA 
#EROSAO E UMA DILATAÇÃO EM SEGUIDA PARA REDUZIR O RUIDO
def erosao(imagem):
	kernel = np.ones((8,8),np.uint8)

	#BLOCO EM ANALISE -----------------------------------------
	opening = cv.morphologyEx(imagem, cv.MORPH_OPEN,kernel) 
	#erosao = cv.erode(opening,kernel,iterations = 1) #VERIFICAR ESSA ALTERALÇÃO DO CL1 POR DST

	return opening


#RESPONSAVEL POR ENCONTRAR OS LIMITES DA SUBIMAGEM
def limites(height,width,lista):
	listaX = []
	listaY = []

	#Verificar o porque em alguns casos os novo_contorno termina por acusar um valor fora da faixa do tamanho da uma imagem
	for i in range(0,4):
		x , y = lista[i]
		listaX.append(x)
		listaY.append(y)

	x1,x2 = min(listaX),max(listaX)
	y1,y2 = min(listaY),max(listaY)

	if (x2 > width):
		x2 = width-1
	
	if(x1 < 0):
		x1 = 0
	
	if (y2 > height):
		y2 = height-1
	
	if(y1 < 0):
		y1 = 0 
	
	#print ("Limites na função:", x1,x2,y1,y2)
	return x1,y1,x2,y2

#RESPONSAVEL PELA IDENTIFICAÇÃO DOS VALORES QUE EXCEDEM A 
# SUB_SUB_IMAGEM  FORMANDO AS 6 REGIÕES AO REDOR DA REGIÃO 
# IDENTIFICADA COMO UMA POSSIVEL ANOMALIA NA ESTRADA
def limites_externos(height,width,height_Regiao,width_Regiao,x,y,x1,y1):

	if(x - int(width_Regiao/2) >= 0):
		x -= int(width_Regiao/2)
	else:
		x = 0

	if(x1 + int(width_Regiao/2) < width):
		x1 += int(width_Regiao/2)
	else:
		x1 = width


	if(y - int(height_Regiao/2) >= 0):
		y -= int(height_Regiao/2)
	else:
		y = 0

	if(y1 + int(height_Regiao/2) < height):
		y1 += int(height_Regiao/2)
	else:
		y1 = height

	#print ("|Iniciais: ",x,'|',y,"|Finais:",'|',x1,'|',y1)
	return x,y,x1,y1

#FUNÇÃO RESPONSAVEL POR PERCORRER OS LIMITES INTERNOS -> EXTERNOS da SubSubImagem
#PARA TENTAR TIRAR UMA GAUSSIANA DE SEUS VALORES
def definindo_regiao(x,x1,y,y1,imagem):
	lista = []
	
	height,width = imagem.shape[:2]
	for i in range(0,255):
		lista.append(-1)
	i=0

	print ('Limites:','[',x,'-',x1,']','|','[',y,'-',y1,']')
	print ("Valores: ",[width,height])
	
	if(x == x1 or y == y1):
		return (lista)
	else:
		for i in range(y,y1): #height
			for j in range(x,x1): #width
				
				if (imagem[i][j] == -1):
					imagem[i][j]
					indice = imagem[i][j]
					indice = indice + 2
					lista.append(indice)
				else:
					print(imagem[i][j])
					indice = imagem[i][j]
					indice = indice + 2
					lista.append(indice)

		print(lista)			
		#plt.plot(lista)
		#plt.ylabel('Gauss')
		#plt.show()


		return (lista)


def take(elem):
	return elem[1]

def estimando_regiao(lista):
	r1,r2,r3 = -1,-1,-1
	m1,m2,m3 = 1,1,1

	#AQUI É REALIZADO UMA MÉDIA SIMPLES, COMO UMA MEDIDA DE UMA TENDENDCIA CENTRAL DE SEUS VALORES
	#TALVEZ SEJA A MELHOR ABORDAGEM, JÁ QUE É DIFICIL ESTIMAR QUAL INTERVALO (0-255)  SERIA ESTIMADO COM UM DETERMINADO
	#VALOR PARA PESOS DIFERENTES

	for i in range(0,len(lista)-1):
		if (i <= 85):
			if(lista[i] != -1):
				print(lista[i])
				r1 += lista[i]
				m1 += 1
			
		elif (i > 85 and i <= 170):
			if(lista[i] != -1):
				print(lista[i])
				r2 += lista[i]
				m2 += 1
		else:
			if(lista[i] != -1):
				print(lista[i])
				r3 += lista[i]
				m3 += 1

	r1 = (r1/m1)
	r2 = (r2/m2)
	r3 = (r3/m3)
		
	#print ("R1: ",r1, "and","M1: ",m1)
	#print ("R2: ",r2, "and","M2: ",m2)
	#print ("R3: ",r3, "and","M3: ",m3)

	listando = []
	listando.append(("Escuro",r1))
	listando.append(("Cinza",r2))
	listando.append(("Claro",r3))
	listando = sorted(listando,reverse=True,key=take)
	#print (":: ",listando)

	if (r1 == r2 == r3 == -1):
		return ("Indefinido",-1)
	else:
		#print('A',listando[0])
		return listando[0]

#Função responsavel por receber a Sub_Lista onde a região principal se encontra
#Ela verifica se os outros valores que existem na mesma lista possuem uma porcentagem 
#significativa em relação a região principal, caso exista, e seja maior que 60%
#o retorno é a quantidade de vezes que a região principal possui regiões ao seu redor
def porcentagem(lista,indice):
	valor = 0

	for i in range(0,len(lista)):
		if (i != indice):
			#(Valor_de_outra_regiao / Valor_Principal)
			porcent = lista[i][2] / lista[indice][2] 
			
			#print("Para [%s][%s][%f]" % (lista[i][0],lista[i][1],lista[i][2]))

			if (porcent*100 >= 60):
				print(porcent*100)
				valor += 1
	return valor

#Esta funcao recebe como parametro a lista contendo as tuplas de três elementos das caracteristicas de cada região principal e 
#seus arredores
#Essa tupla é compostas por ('SIGLA_REGIAO','TIPO_DE_COR_REGIAO','VALOR_MEDIA_DA_COR_DA_REGIAO')
#Percorrendo essa lista, é separado então de acordo com os 'TIPOS_DE_COR_REGIAO' todas as tuplas
#Depois verifica se em qual das listas está o elemento principal 'lista[0]' e se o seu valor de MÉDIA é maior que zero
#Caso a condição seja verdadeira, a função 'PORCENTAGEM' é chamada e o seu valor de retorno é um valor indicando se 
#a lista que contém a região principal, possui regiões ao seu redor que estão proximas se deu valor, isso pode indicar
#que aquela região não necessariamente é um buraco, pode ser apenas uma mancha, ou alguma outra coisa qualquer que 
def relacionando_regiao(lista):	
	listaEs = []
	listaCi = []
	listaCl = []
	valor = 0
	flag = ""

	for i in range(0,len(lista)-1):
		if (lista[i][1] == 'Escuro'):
			listaEs.append(lista[i])
			flag = "Es"
		
		if(lista[i][1] == 'Cinza'):
			listaCi.append(lista[i])
			flag = "Ci"
		
		if(lista[i][1] == 'Claro'):
			listaCl.append(lista[i])
			flag = "Cl"
	
	#print("Es",listaEs)
	#print("Ci",listaCi)
	#print("Cl",listaCl)
	
	if(flag == "Es"):
		if(listaEs[0][0] == 'P' and listaEs[0][2] > 0):			
			valor = porcentagem(listaEs,0)
		
			
	if(flag == "Ci"):
		if(listaCi[0][0] == 'P' and listaCi[0][2] > 0 ):
			valor = porcentagem(listaCi,0)

	if(flag == "Cl"):
		if(listaCl[0][0] == 'P' and listaCl[0][2] > 0):
			valor = porcentagem(listaCl,0)
			

			
	print("VALOR: ",valor)
	return valor

#Função atualizada, verificar apenas a possibilidade de retornar uma lista ao inves da quantidade
def contando_subimagens(num,arquivo):
	count = 0
	lista = []
	
	for i in range(0,len(arquivo)):
		var = arquivo[i].split('_')
		if(var[0] == num ):
			count +=1
			#lista.append(arquivo[i])

	return count 

if __name__ == "__main__":

	origem = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Origem\\"
	#origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Origem/'
	
	origem2 = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Origem_Fake\\"
	#origem2 = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Origem_Fake/'

	subimagem = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\3_SubImagens\\"
	#subimagem ='/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/3_SubImagens/'

	destino = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\"
	#destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	
	especial = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Origem\\"
	#especial = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Origem/'

	tabela = [{"NUM_ORIGIN":1,
           	   "NUM_SUB":1,
               "NUM_SUB_SUB":1,

               "AREA_ORIGIN":0,
               "AREA_SUB":0,
               "AREA_SUB_SUB":0,

               "COMPRIMENTO_ORIGIN":0,
               "COMPRIMENTO_SUB":0,
               "COMPRIMENTO_SUB_SUB":0,

               "LARGURA_ORIGIN":0,
               "LARGURA_SUB":0,
               "LARGURA_SUB_SUB":0,

               "ALTURA_ORIGIN":0,
               "ALTURA_SUB":0,
               "ALTURA_SUB_SUB":0,

               "CIRCULARIDADE_SUB":0,
               "CIRCULARIDADE_SUB_SUB":0,

			   "AREA_SUB_ORIGINAL":0,
			   "AREA_SUBSUB_ORIGINAL":0,
			   "AREA_SUBSUB_SUB_IMAGEM":0,

               "REGIAO_P":"null",
               "REGIAO_N":"null",
               "REGIAO_S":"null",
               "REGIAO_L":"null",
               "REGIAO_O":"null",
               "REGIAO_NO":"null",
               "REGIAO_NL":"null",
               "REGIAO_SO":"null",
               "REGIAO_SL":"null",

               "MEDIA_REGIAO_P":0,
               "MEDIA_REGIAO_N":0,
               "MEDIA_REGIAO_S":0,
               "MEDIA_REGIAO_L":0,
               "MEDIA_REGIAO_O":0,
               "MEDIA_REGIAO_NO":0,
               "MEDIA_REGIAO_NL":0,
               "MEDIA_REGIAO_SO":0,
               "MEDIA_REGIAO_SL":0,
            }]

	df = pd.DataFrame(tabela)
	df = df[["NUM_ORIGIN","NUM_SUB","NUM_SUB_SUB","AREA_ORIGIN","AREA_SUB","AREA_SUB_SUB","COMPRIMENTO_ORIGIN","COMPRIMENTO_SUB","COMPRIMENTO_SUB_SUB","LARGURA_ORIGIN","LARGURA_SUB","LARGURA_SUB_SUB","ALTURA_ORIGIN","ALTURA_SUB","ALTURA_SUB_SUB","CIRCULARIDADE_SUB","CIRCULARIDADE_SUB_SUB","AREA_SUB_ORIGINAL","AREA_SUBSUB_ORIGINAL","AREA_SUBSUB_SUB_IMAGEM","REGIAO_P","REGIAO_N","REGIAO_S","REGIAO_L","REGIAO_O","REGIAO_NO","REGIAO_NL","REGIAO_SO","REGIAO_SL","MEDIA_REGIAO_P","MEDIA_REGIAO_N","MEDIA_REGIAO_S","MEDIA_REGIAO_L","MEDIA_REGIAO_O","MEDIA_REGIAO_NO","MEDIA_REGIAO_NL","MEDIA_REGIAO_SO","MEDIA_REGIAO_SL"]]				
	df.to_csv('ic.csv',header=True,index=False)
	
	for _, _, quantidade in os.walk(origem):
		pass

	for _, _, arquivo in os.walk(subimagem):
		pass


	count = 0
	for cast in quantidade:
		cast = cast.split('.')
		num = int(cast[0])
		listandoContornos = []
		
		count = contando_subimagens(cast[0],arquivo)
		print ("Imagem [%d] possui [%d] subImagens" %(num,count))

		#REDEFINIR O FOR PARA A ENTRADA DOS VALORES
		for i in range(1,count+1):

			leitura = subimagem + str(num)+ '_' +str(i) + '.png'
			cor = cv.imread(leitura)
			#mostrar_imagem(cor)

			#width = int(cor.shape[1] *2)
			#height = int(cor.shape[0] * 2)
			#cor = cv.resize(cor, (width,height), interpolation = cv.INTER_LINEAR)
			
			imagem = cv.cvtColor(cor,cv.COLOR_RGB2GRAY)
			#mostrar_imagem(imagem)

			height, width = cor.shape[:2]

			area_SubImagem = height * width
			width_SubImagem = width
			height_SubImagem = height

			#Os passos a seguir são somente para um pequeno tratamento (novamente) na sub-imagem
			imagem = limpar(imagem) #IMPORTANTE MANTER
			#mostrar_imagem(imagem)

			#imagem = equalizar(imagem)
			#mostrar_imagem(imagem)

			imagem = erosao(imagem)
			imagem_cinza = imagem
			#mostrar_imagem(imagem_cinza)

			imagem_thresh = thresholding(imagem)
			#mostrar_imagem(imagem_thresh)

			imagem = canny(imagem_thresh)
			#mostrar_imagem(imagem)

			imagem_contorno,imagemc = contornos(imagem)
			
			#-----------------------------------------------------------------------------------

			#RESPONSAVEL POR PERCORRER CADA SubSubImagem que foi encontrada na SubImagem que pode ser um possivel buraco/mancha/rachadura
			for j in range(0,len(imagem_contorno)-1):

				#-------------------------------------------------------
				subImagem = cor.copy()

				teste = imagem_contorno[j]
				
				quadrado = cv.minAreaRect(teste)
				novos_contornos = cv.boxPoints(quadrado)
				novos_contornos = np.int0(novos_contornos)

				a = area(novos_contornos)
				#--------------------------------------------------------
				

				print ("\nDefinindo regiões e seus valores\n")
				#--------------------------------------------------------------------------------------------------------------#
				#RESPONSAVEL POR DEFINIR OS LIMITES EM (x,y) DA SubSubImagem
				lxi0, lyi0, lxi1, lyi1 = limites(height,width,novos_contornos)

				#Aqui são definidos alguns parametros da SubSubImagem (area,comprimento,circularidade,lagura,comprimento)       
				area_SubSubImagem = (lxi1-lxi0) * (lyi1-lyi0)    #width * height
				comp_SubSubImagem = comprimento(teste)
				circ_SubSubImagem = circularidade(teste)
				width_SubSubImagem = (lxi1-lxi0)
				height_SubSubImagem = (lyi1-lyi0)

				#RESPONSAVEL POR DEFINIR A REGIÃO DE ANALISE AO REDOR DA SubSubImagem, DE ACORDO COM O TAMANHO ORIGINAL DA IMAGEM
				lxe0, lye0, lxe1, lye1 = limites_externos(height_SubImagem,width_SubImagem,height_SubSubImagem,width_SubSubImagem,lxi0,lyi0,lxi1,lyi1)

				#RESPONSAVEL POR PERCORRER AS REGIÕES AO REDOR DA REGIÃO PRINCIPAL PARA FUTURAMENTE TENTAR ESTIMAR
				#ALGUMAS INFORMAÇÕES A MAIS A PARTIR DA RELAÇÃO ENTRE ELAS E A PARTE PRINCIPAL
				#AO TOD ESTÃO DEFINIDOS A REGIÃO PRINCIPAL (P), E MAIS 8 REGIÕES (Norte,Sul,Leste,Oeste,Nordeste,Noroeste,Sudeste,Sudoeste)
				
				listaPosicoes = [['P',[lxi0,lxi1,lyi0,lyi1]],['N',[lxi0,lxi1,lye0,lyi0]],['S',[lxi0,lxi1,lyi1,lye1]],
								['L',[lxi1,lxe1,lyi0,lyi1]],['O',[lxe0,lxi0,lyi0,lyi1]],['NO',[lxe0,lxi0,lye0,lyi0]],
								['NL',[lxi1,lxe1,lye0,lyi0]],['SL',[lxi1,lxe1,lyi1,lye1]],['SO',[lxe0,lxi0,lyi1,lye1]]]

				listaTotal = []
				for d_r in listaPosicoes:
					a = d_r[1]
					aux = definindo_regiao(a[0],a[1],a[2],a[3],imagem_cinza)
					#subImagem[a[2]:a[3],a[0]:a[1]] = (randint(0,254),randint(0,254),randint(0,254))
					#mostrar_imagem(subImagem)
					listaTotal.append([d_r[0],aux])

				#listaTotal = [['P',listaP],['N',listaN],['S',listaS],['L',listaL],['O',listaO],['NO',listaNO],['NL',listaNL],['SL',listaSL],['SO',listaSO]]
				#--------------------------------------------------------------------------------------------------------------#
				
				
				print ('Definindo media das regiões\n')
				#--------------------------------------------------------------------------------------------------------------#
				listaRegiao = []
				media = []

				#Percorre a lista de tuplas que indicam a posição da regiao e sua lista definida por "definindo_regiao"
				for estimando in listaTotal:
					regiao, media = estimando_regiao(estimando[1])
					listaRegiao.append((estimando[0],regiao,media))
					#print ("Relacionando as regiões: [%s] | [%f] | [%f]" ,estimando[0],regiao,media)
				
				#--------------------------------------------------------------------------------------------------------------#
				print ('\nRelacionando valores de regiões\n')
				valor = relacionando_regiao(listaRegiao)
				#subImagem[lyi0:lyi1, lxi0:lxi1] = (0, 0, 0)
				#mostrar_imagem(subImagem)
				#--------------------------------------------------------------------------------------------------------------#
				
				if (valor > 0):
					print ('Existem regiões com valores aproximados')
				else:
					print ('Não existem regiões com valores aproximados')

				print('-----------------------------------------------------------------------------------------------------------------------')

				#print (listaRegiao)

				area_Final = area_interesse(area_SubImagem,area_SubSubImagem)
				
				#---------------------------------------------------------------------------------------------------------------------
				area_final = (area(novos_contornos)/area_SubImagem)
				#print(area_final)
				#cv.drawContours(subImagem,[novos_contornos],0,(0,0,255),3)
				#mostrar_imagem(subImagem)

				area_Imagem = 512*256
				#area_SubImagem =  Já tem
				#area_SubSubImagem = Já tem

				comp_Imagem = 4*512
				#width_SubImagem = já tem
				#comp_SubSubImagem = já tem 

				larg_Imagem = 512	#informação correta em pid.py
				#larg_SubImagem = width_SubImagem
				#larg_SubSubImagem =  já tem

				#VERIFICAR
				height_Imagem = 256
				#height_SubImagem = já tem
				#height_SubSubImagem = height

				#circ_SubImagem = informação contida no pid.py 
				#circ_SubSubImagem = já tem 

				area_SubOriginal = (area_SubImagem/area_Imagem)
				area_SubSubOriginal = (area_SubSubImagem/area_Imagem)
				area_SubSub_SubImagem = (area_SubSubImagem/area_SubImagem )
				
				#regiao_P,media_P

				#if(area_Final >= 0.003 and valor < 1):
				#print ('Imagem atual:')
					
				friends = [{"NUM_ORIGIN":num,
							"NUM_SUB":i,
							"NUM_SUB_SUB":j,

							"AREA_ORIGIN":area_Imagem,
							"AREA_SUB":area_SubImagem,
							"AREA_SUB_SUB":area_SubSubImagem,

							"COMPRIMENTO_ORIGIN":comp_Imagem,
							"COMPRIMENTO_SUB":width_SubImagem,
							"COMPRIMENTO_SUB_SUB":comp_SubSubImagem,

							"LARGURA_ORIGIN":larg_Imagem,
							"LARGURA_SUB":width_SubImagem,
							"LARGURA_SUB_SUB":width_SubSubImagem,

							"ALTURA_ORIGIN":height_Imagem,
							"ALTURA_SUB":height_SubImagem,
							"ALTURA_SUB_SUB":height_SubSubImagem,

							"CIRCULARIDADE_SUB":0,
							"CIRCULARIDADE_SUB_SUB":circ_SubSubImagem,

							"AREA_SUB_ORIGINAL":area_SubOriginal,
							"AREA_SUBSUB_ORIGINAL":area_SubSubOriginal,
							"AREA_SUBSUB_SUB_IMAGEM":area_SubSub_SubImagem,

							"REGIAO_P":listaRegiao[0][1],
							"REGIAO_N":listaRegiao[1][1],
							"REGIAO_S":listaRegiao[2][1],
							"REGIAO_L":listaRegiao[3][1],
							"REGIAO_O":listaRegiao[4][1],
							"REGIAO_NO":listaRegiao[5][1],
							"REGIAO_NL":listaRegiao[6][1],
							"REGIAO_SL":listaRegiao[7][1],
							"REGIAO_SO":listaRegiao[8][1],

							"MEDIA_REGIAO_P":listaRegiao[0][2],
							"MEDIA_REGIAO_N":listaRegiao[1][2],
							"MEDIA_REGIAO_S":listaRegiao[2][2],
							"MEDIA_REGIAO_L":listaRegiao[3][2],
							"MEDIA_REGIAO_O":listaRegiao[4][2],
							"MEDIA_REGIAO_NO":listaRegiao[5][2],
							"MEDIA_REGIAO_NL":listaRegiao[6][2],
							"MEDIA_REGIAO_SL":listaRegiao[7][2],
							"MEDIA_REGIAO_SO":listaRegiao[8][2],
						}]

				df = pd.DataFrame(friends)
				df = df[["NUM_ORIGIN","NUM_SUB","NUM_SUB_SUB","AREA_ORIGIN","AREA_SUB","AREA_SUB_SUB","COMPRIMENTO_ORIGIN","COMPRIMENTO_SUB","COMPRIMENTO_SUB_SUB","LARGURA_ORIGIN","LARGURA_SUB","LARGURA_SUB_SUB","ALTURA_ORIGIN","ALTURA_SUB","ALTURA_SUB_SUB","CIRCULARIDADE_SUB","CIRCULARIDADE_SUB_SUB","AREA_SUB_ORIGINAL","AREA_SUBSUB_ORIGINAL","AREA_SUBSUB_SUB_IMAGEM","REGIAO_P","REGIAO_N","REGIAO_S","REGIAO_L","REGIAO_O","REGIAO_NO","REGIAO_NL","REGIAO_SO","REGIAO_SL","MEDIA_REGIAO_P","MEDIA_REGIAO_N","MEDIA_REGIAO_S","MEDIA_REGIAO_L","MEDIA_REGIAO_O","MEDIA_REGIAO_NO","MEDIA_REGIAO_NL","MEDIA_REGIAO_SO","MEDIA_REGIAO_SL"]]				
				print("+++++++++++++++++++++++++++++++++++++++++++ SALVO NO CSV ++++++++++++++++++++++++++++++++++++++++++++")
				df.to_csv('ic.csv',header=False, mode='a',index=False)
				
				#print ('Comprimento:',comprimento(teste))
				#print ('Altura:',altura(teste))
				#print ('Area:',area_final)
				#print ('largura:',largura(teste))
				#print ('Circularidade:',circularidade(teste))
				imagem_aux = desenhando(subImagem,novos_contornos)
				#mostrar_imagem(imagem_aux)
				tag = str(i) + "." + str(j)	
				salvar(imagem_aux,num,tag,'4_Contornos\\')
				listandoContornos.append((novos_contornos,i))
				

		leitura = 0
		listXY = []
		listaFinal = []
		
		limite = len(listandoContornos)
		#print ("LIMITE: ", limite)
		arq = open(destino + '0_Listas_Posicoes\\' + 'lista' + str(num) + '.txt', 'r')

		texto = arq.read()

		if(texto != 'NaN'):
			#CORRIGIR ESTA EXPRESSAO
			lista = list(eval(texto.split()[0]))

			#print ("NOVA LISTA:" ,lista)

			leitura = especial + str(lista[0][1]) + '.jfif'
			imagem_aux = cv.imread(leitura)

			#AQUI COMEÇA A COMPARAÇÃO COM OS VALORES DA LISTA ENCONTRADA AQUI E DA LISTA ORIGINAL
			inicioJ = 0

			for k in range(0,len(lista)):
				for j in range(inicioJ,limite):

					if (lista[k][2] == listandoContornos[j][1]): #A comparação é realizada de acordo com os indices das imagens e não dos contornos
						menorX,menorY,lix,lix2 = limites(height,width,lista[k][0])

						x = menorX + listandoContornos[j][0][0][0] 
						y = menorY + listandoContornos[j][0][0][1] + 256

						x1 = menorX + listandoContornos[j][0][1][0] 
						y1 = menorY + listandoContornos[j][0][1][1] + 256

						x2 = menorX + listandoContornos[j][0][2][0] 
						y2 = menorY + listandoContornos[j][0][2][1] + 256

						x3 = menorX + listandoContornos[j][0][3][0] 
						y3 = menorY + listandoContornos[j][0][3][1] + 256

						contorno = np.array([[x,y],[x1,y1],[x2,y2],[x3,y3]])
						cv.drawContours(imagem_aux,[contorno],0,(0,0,255),3)

			#print (lista[0][1], ' and ',num)
			salvar(imagem_aux,lista[0][1],0,'5_Finalizadas\\')
			print ('Processamento da imagem [%d] foi finalizado... \n '%(num))
		#else:
			#salvar(imagem_aux,i,len(listandoContornos),'5_Finalizadas/')

		leitura = ""
		arq.close()
