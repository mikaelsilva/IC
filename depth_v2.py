from matplotlib import pyplot as plt
from random import randint
import pandas as pd
import numpy as np
import cv2 as cv
import math
import os



def limpar(imagem):
	dst = cv.fastNlMeansDenoising(imagem,None,10,7,21)
	return dst

#VERIFICADA, RESPONSAVEL POR RECEBER A SUB_IMAGEM CINZA E GERAR UMA 
#EROSAO E UMA DILATAÇÃO EM SEGUIDA PARA REDUZIR O RUIDO
def erosao(imagem):
	kernel = np.ones((8,8),np.uint8)

	#BLOCO EM ANALISE -----------------------------------------
	opening = cv.morphologyEx(imagem, cv.MORPH_OPEN,kernel) 
	#erosao = cv.erode(opening,kernel,iterations = 1) #VERIFICAR ESSA ALTERALÇÃO DO CL1 POR DST

	return opening

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


#RESPONSAVEL POR ENCONTRAR OS LIMITES DA SUBIMAGEM
def limites(height, width, lista):
	listaX = []
	listaY = []

	#Verificar o porque em alguns casos os novo_contorno termina por acusar um valor fora da faixa do tamanho da sua sub_imagem
	for i in range(0,4):
		x , y = lista[i]
		listaX.append(x)
		listaY.append(y)

	x_min,x_max = min(listaX),max(listaX)
	y_min,y_max = min(listaY),max(listaY)

	if (x_max > width):
		x_max = width-1
	
	if(x_min < 0):
		x_min = 0
	
	if (y_max > height):
		y_max = height-1
	
	if(y_min < 0):
		y_min = 0 

	return x_min,y_min,x_max,y_max

#RESPONSAVEL PELA IDENTIFICAÇÃO DOS VALORES QUE EXCEDEM A 
# SUB_SUB_IMAGEM  FORMANDO AS 8 REGIÕES AO REDOR DA REGIÃO 
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


#FUNÇÃO RESPONSAVEL POR PERCORRER OS LIMITES INTERNOS ate os EXTERNOS da SubSubImagem
#PARA IDENTIFICAR A DISTRIBUIÇÃO DOS VALORES [0-255] NA ESCALA EM CINZA DA SUBIMAGEM
def definindo_regiao(x,x1,y,y1,imagem): 
	dicio = {} 
	lista = []
	
	#height,width = imagem.shape[:2]
	for i in range(0,256):
		dicio[str(i)] = 0

	#print ('Limites:','[',x,'-',x1,']','|','[',y,'-',y1,']')
	#print ("Valores: ",[width,height])
	
	if(x == x1 or y == y1):
		for val in dicio.values():
			lista.append(val)
		return (lista)
	
	else:
		for height in range(y,y1): #height
			for width in range(x,x1): #width
				indice = imagem[height][width]
				dicio[str(indice)] = dicio[str(indice)] + 1

		#print(lista)			
		#plt.ylabel('Gauss')
		#plt.show()
		for val in dicio.values():
			lista.append(val)
		
		#plt.bar(range(255),lista)
		#plt.show()
		return (lista)

#AQUI É REALIZADO UMA MÉDIA SIMPLES, COMO UMA MEDIDA DE UMA TENDENDCIA CENTRAL DE SEUS VALORES
#TALVEZ SEJA A MELHOR ABORDAGEM, JÁ QUE É DIFICIL ESTIMAR QUAL INTERVALO (0-255)  SERIA ESTIMADO COM UM DETERMINADO
# #VALOR PARA PESOS DIFERENTES
def estimando_regiao(lista):
	r1,r2,r3 = 1,1,1

	for i in range(0,len(lista)-1):
		if (i <= 85):
			if(lista[i] != 0):
				r1 += lista[i]

		elif (i > 85 and i <= 170):
			if(lista[i] != 0):
				r2 += lista[i] 

		else:
			if(lista[i] != 0):
				r3 += lista[i] 

	media_1 = r1/85
	media_2 = r2/85
	media_3 = r3/85
		
	listando = []
	listando.append(("Escuro",media_1))
	listando.append(("Cinza",media_2))
	listando.append(("Claro",media_3))
	listando = sorted(listando,reverse=True,key=take)
	#print (":: ",listando)

	if (media_1 == media_2 == media_3 == -1.0):
		return ("Indefinido",-1.0)
	else:
		if(listando[0][1] == listando[1][1] == listando[2][1]):
			return ("Iguais",listando[0][1])
		else:	
			return listando[0]


def take(elem):
	return elem[1]

#Função responsavel por receber a Sub_Lista onde a região principal se encontra
#Ela verifica se os outros valores que existem na mesma lista possuem uma porcentagem 
#significativa em relação a região principal, caso exista, e seja maior que 60%
#o retorno é a quantidade de vezes que a região principal possui regiões ao seu redor
def porcentagem(lista):
	valor = 0

	for i in range(1,len(lista)):
		#(Valor_de_outra_regiao / Valor_Principal)
		porcent = lista[i][2] / lista[0][2] 

		#print("Para [%s][%s][%f]" % (lista[i][0],lista[i][1],lista[i][2]))
		if (porcent*100 >= 50):
			#print(porcent*100)
			valor += 1

	return valor


#Esta funcao recebe como parametro a lista contendo as tuplas de três elementos das caracteristicas de cada região principal e 
#seus arredores
#Essa tupla é compostas por ('SIGLA_REGIAO','TIPO_DE_COR_REGIAO','VALOR_MEDIA_DA_COR_DA_REGIAO')
#Percorrendo essa lista, é separado então de acordo com os 'TIPOS_DE_COR_REGIAO' todas as tuplas
#Depois verifica se em qual das listas está o elemento principal 'lista[0]' e se o seu valor de MÉDIA é maior que zero
#Caso a condição seja verdadeira, a função 'PORCENTAGEM' é chamada e o seu valor de retorno é um valor indicando se 
#a lista que contém a região principal, possui regiões ao seu redor que estão proximas de deu valor, isso pode indicar
#que aquela região não necessariamente é um buraco, pode ser apenas uma mancha, ou alguma outra coisa qualquer que 
def relacionando_regiao(lista):	
	listaEs,listaCi,listaCl,listaIn,listaIg = [], [], [], [], []
	valor = 0
	flag = ""

	for lis in lista:
		if (lis[1] == 'Escuro'):
			listaEs.append(lis)
			flag = "Escuro"
		
		if(lis[1] == 'Cinza'):
			listaCi.append(lis)
			flag = "Cinza"
		
		if(lis[1] == 'Claro'):
			listaCl.append(lis)
			flag = "Claro"
		
		if(lis[1] == 'Indefinido'):
			listaIn.append(lis)
			flag = "Indefinido"

		if(lis[1] == 'Iguais'):
			listaIg.append(lis)
			flag = "Iguais"

	for i in [listaEs,listaCi,listaCl,listaIn,listaIg]:
		try:
			if(i[0][0] == 'P'):
				return len(i)
		except:
			pass

	return valor


#A relação entre as duas areas ocorre de forma a identificar qual a área da subimagem em relação a imagem maior/anterior
#(Sub_Imagem / Imagem_Original) , (SubSub_Imagem / Sub_Imagem) ,(SubSub_Imagem / Imagem_Original)
def area_interesse(area_Imagem,area_SubImagem):
	try:
		area = area_Imagem - area_SubImagem
		variacao_porcent = (area*100)/area_Imagem
		return variacao_porcent
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
	#destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	destino = "c:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\"
	final = destino + flag + 'Contorno_' + str(i) + '.' + str(j) + '.png'

	#print(final)
	cv.imwrite(final,imagem)


def desenhando(imagem,contornos):
	cv.drawContours(imagem,[contornos],0,(0,0,255),3)
	return imagem


def equalizar(imagem):
	clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(5,5))
	cl1 = clahe.apply(imagem)
	return cl1
#----------------------------------------------------------------

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

	listasPosicoes = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\0_Listas_Posicoes\\"

	destino = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\"
	#destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	
	especial = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Origem\\"
	#especial = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Origem/'

	tabela = [{"NUM_ORIGIN":1,
			   "NUM_SUB":1,
			   
			   "AREA_ORIGIN":0,
			   "AREA_SUB":0,

			   "COMPRIMENTO_ORIGIN":0,
			   "COMPRIMENTO_SUB":0,

			   "LARGURA_ORIGIN":0,
			   "LARGURA_SUB":0,

			   "ALTURA_ORIGIN":0,
			   "ALTURA_SUB":0,

			   "CIRCULARIDADE_SUB":0,

			   "AREA_SUB_ORIGINAL":0,

			   "REGIAO_P":"null",
			   "MEDIA_REGIAO_P":0,

			   "REGIAO_N":"null",
			   "MEDIA_REGIAO_N":0,

			   "REGIAO_S":"null",
			   "MEDIA_REGIAO_S":0,

			   "REGIAO_L":"null",
			   "MEDIA_REGIAO_L":0,

			   "REGIAO_O":"null",
			   "MEDIA_REGIAO_O":0,

			   "REGIAO_NO":"null",
			   "MEDIA_REGIAO_NO":0,

			   "REGIAO_NL":"null",
			   "MEDIA_REGIAO_NL":0,

			   "REGIAO_SO":"null",
			   "MEDIA_REGIAO_SO":0,

			   "REGIAO_SL":"null",
			   "MEDIA_REGIAO_SL":0,

			   "QTD_REGIOES":0
			}]

	df = pd.DataFrame(tabela)
	df = df[["NUM_ORIGIN","NUM_SUB","AREA_ORIGIN","AREA_SUB","COMPRIMENTO_ORIGIN","COMPRIMENTO_SUB","LARGURA_ORIGIN","LARGURA_SUB","ALTURA_ORIGIN","ALTURA_SUB",
			 "CIRCULARIDADE_SUB","AREA_SUB_ORIGINAL","REGIAO_P","MEDIA_REGIAO_P","REGIAO_N","MEDIA_REGIAO_N","REGIAO_S","MEDIA_REGIAO_S","REGIAO_L","MEDIA_REGIAO_L",
			 "REGIAO_O","MEDIA_REGIAO_O","REGIAO_NO","MEDIA_REGIAO_NO","REGIAO_NL","MEDIA_REGIAO_NL","REGIAO_SO","MEDIA_REGIAO_SO","REGIAO_SL","MEDIA_REGIAO_SL","QTD_REGIOES"]]				
	df.to_csv('ic_death_v2.csv',header=True,index=False)
	
	for _, _, quantidade in os.walk(origem):
		pass

	for _, _, arquivo in os.walk(subimagem):
		pass

	for _, _, listas in os.walk(listasPosicoes):
		pass
	
	for im in quantidade:
		print("*******************************************************",im,"*******************************************************")
		arq = open(listasPosicoes + "lista" + im.split('.')[0] + ".txt", 'r')
		texto = arq.read()
		aux = list(eval(texto))
		num = im.split('.')[0]
		listandoContornos = []

		#print(aux,"\n")

		leitura = origem + im
		cor = cv.imread(leitura)
		imagem_cinza = cv.cvtColor(cor,cv.COLOR_RGB2GRAY)
		#mostrar_imagem(cor)

		height, width = cor.shape[:2]

		for j in aux:
			lxi0, lyi0, lxi1, lyi1 = limites(height, width , j[0])

			print('1: ' ,j[0])
			print('2: ' ,'[',lxi0, lyi0,']', '[',lxi1, lyi1,']','\n')

			#Aqui são definidos alguns parametros da SubSubImagem (area,comprimento,circularidade,lagura,comprimento)       
			#area_SubSubImagem = (lxi1-lxi0) * (lyi1-lyi0)    #width * height
			#comp_SubSubImagem = comprimento(lxi1-lxi0)
			#circ_SubSubImagem = circularidade(teste)
			width_SubImagem = (lxi1-lxi0)
			height_SubImagem = (lyi1-lyi0)
			
			#RESPONSAVEL POR DEFINIR A REGIÃO DE ANALISE AO REDOR DA SubSubImagem, DE ACORDO COM O TAMANHO ORIGINAL DA IMAGEM
			lxe0, lye0, lxe1, lye1 = limites_externos(height,width,height_SubImagem,width_SubImagem,lxi0,lyi0,lxi1,lyi1)

			#RESPONSAVEL POR PERCORRER AS REGIÕES AO REDOR DA REGIÃO PRINCIPAL PARA FUTURAMENTE TENTAR ESTIMAR
			#ALGUMAS INFORMAÇÕES A MAIS A PARTIR DA RELAÇÃO ENTRE ELAS E A PARTE PRINCIPAL
			#AO TOD ESTÃO DEFINIDOS A REGIÃO PRINCIPAL (P), E MAIS 8 REGIÕES (Norte,Sul,Leste,Oeste,Nordeste,Noroeste,Sudeste,Sudoeste)
				
			listaPosicoes = [['P',[lxi0,lxi1,lyi0,lyi1]],['N',[lxi0,lxi1,lye0,lyi0]],['S',[lxi0,lxi1,lyi1,lye1]],
							['L',[lxi1,lxe1,lyi0,lyi1]],['O',[lxe0,lxi0,lyi0,lyi1]],['NO',[lxe0,lxi0,lye0,lyi0]],
							['NL',[lxi1,lxe1,lye0,lyi0]],['SL',[lxi1,lxe1,lyi1,lye1]],['SO',[lxe0,lxi0,lyi1,lye1]]]

			listaTotal = []
			for d_r in listaPosicoes:
				pos = d_r[1]
				aux_ = definindo_regiao(pos[0],pos[1],pos[2],pos[3],imagem_cinza)
				#cor[pos[2]:pos[3],pos[0]:pos[1]] = (randint(0,254),randint(0,254),randint(0,254))
				#mostrar_imagem(cor)
				listaTotal.append([d_r[0],aux_])

				#listaTotal = [['P',listaP],['N',listaN],['S',listaS],['L',listaL],['O',listaO],['NO',listaNO],['NL',listaNL],['SL',listaSL],['SO',listaSO]]
				#--------------------------------------------------------------------------------------------------------------#

				#print ('Definindo media das regiões\n')
				#--------------------------------------------------------------------------------------------------------------#
				listaRegiao = []
				media = []

				#Percorre a lista de tuplas que indicam a posição da regiao e sua lista definida por "definindo_regiao"
				for estimando in listaTotal:
					regiao, media = estimando_regiao(estimando[1])
					listaRegiao.append((estimando[0],regiao,media))
					#print ("Relacionando as regiões: [%s] | [%f] | [%f]" ,estimando[0],regiao,media)
				
				#--------------------------------------------------------------------------------------------------------------#
				#print ('\nRelacionando valores de regiões\n')
				valor = relacionando_regiao(listaRegiao)
				#subImagem[lyi0:lyi1, lxi0:lxi1] = (0, 0, 0)
				#mostrar_imagem(subImagem)
			
				#--------------------------------------------------------------------------------------------------------------#
				if(valor is None):
					print("Valor None Retornado")
					valor = "None"
				elif(valor > 1):
					print ("Existem regiões com valores aproximados")
				else:
					print ("Não existem regiões com valores aproximados -> ",valor)

				print('-----------------------------------------------------------------------------------------------------------------------')

				#print (listaRegiao)

				#area_Final = area_interesse(area_SubImagem,area_SubSubImagem)
				#print("area_Final",area_Final)
				#---------------------------------------------------------------------------------------------------------------------
				#area_final = (area(novos_contornos)/area_SubImagem)
				#print(area_final)
				#cv.drawContours(subImagem,[novos_contornos],0,(0,0,255),3)
				#mostrar_imagem(subImagem)

				area_Imagem = height*height
				area_SubImagem =  height_SubImagem * width_SubImagem

				comp_Imagem = 4*height
				comp_SubImagem = 2*width_SubImagem + 2*height_SubImagem

				larg_Imagem = height	
				larg_SubImagem = width_SubImagem

				alt_Imagem = height
				alt_SubImagem = height_SubImagem
				
				#circ_SubImagem = informação contida no pid.py 
				
				area_SubOriginal = area_interesse(area_Imagem, area_SubImagem)

				#regiao_P,media_P
				#if(area_Final >= 0.003 and valor < 1):
				#print ('Imagem atual:')
				print(listaTotal)
				print(listaRegiao)
				
				tabela = [{"NUM_ORIGIN":num,
						   "NUM_SUB":j[2],
						   
						   "AREA_ORIGIN":area_Imagem,
						   "AREA_SUB":area_SubImagem,
						   
						   "COMPRIMENTO_ORIGIN":comp_Imagem,
						   "COMPRIMENTO_SUB":width_SubImagem,
						   
						   "LARGURA_ORIGIN":larg_Imagem,
						   "LARGURA_SUB":width_SubImagem,
						   
						   "ALTURA_ORIGIN":height,
						   "ALTURA_SUB":height_SubImagem,
						   
						   "CIRCULARIDADE_SUB":0,
						   
						   "AREA_SUB_ORIGINAL":area_SubOriginal,
						   
						   "REGIAO_P":listaRegiao[0][1],
						   "MEDIA_REGIAO_P":listaRegiao[0][2],
						   
						   "REGIAO_N":listaRegiao[1][1],
						   "MEDIA_REGIAO_N":listaRegiao[1][2],
						   
						   "REGIAO_S":listaRegiao[2][1],
						   "MEDIA_REGIAO_S":listaRegiao[2][2],
						   
						   "REGIAO_L":listaRegiao[3][1],
						   "MEDIA_REGIAO_L":listaRegiao[3][2],
						   
						   "REGIAO_O":listaRegiao[4][1],
						   "MEDIA_REGIAO_O":listaRegiao[4][2],
						   
						   "REGIAO_NO":listaRegiao[5][1],
						   "MEDIA_REGIAO_NO":listaRegiao[5][2],
						   
						   "REGIAO_NL":listaRegiao[6][1],
						   "MEDIA_REGIAO_NL":listaRegiao[6][2],

						   "REGIAO_SL":listaRegiao[7][1],
						   "MEDIA_REGIAO_SL":listaRegiao[7][2],
   
						   "REGIAO_SO":listaRegiao[8][1],
						   "MEDIA_REGIAO_SO":listaRegiao[8][2],
   
						   "QTD_REGIOES":valor
						}]

				df = pd.DataFrame(tabela)
				df = df[["NUM_ORIGIN","NUM_SUB","AREA_ORIGIN","AREA_SUB","COMPRIMENTO_ORIGIN","COMPRIMENTO_SUB","LARGURA_ORIGIN","LARGURA_SUB","ALTURA_ORIGIN","ALTURA_SUB",
						 "CIRCULARIDADE_SUB","AREA_SUB_ORIGINAL","REGIAO_P","MEDIA_REGIAO_P","REGIAO_N","MEDIA_REGIAO_N","REGIAO_S","MEDIA_REGIAO_S","REGIAO_L","MEDIA_REGIAO_L",
						 "REGIAO_O","MEDIA_REGIAO_O","REGIAO_NO","MEDIA_REGIAO_NO","REGIAO_NL","MEDIA_REGIAO_NL","REGIAO_SO","MEDIA_REGIAO_SO","REGIAO_SL","MEDIA_REGIAO_SL",
						 "QTD_REGIOES"]]				
				#print("+++++++++++++++++++++++++++++++++++++++++++ SALVO NO CSV ++++++++++++++++++++++++++++++++++++++++++++")
				df.to_csv('ic_death_v2.csv',header=False, mode='a',index=False)
				
				#print ('Comprimento:',comprimento(teste))
				#print ('Altura:',altura(teste))
				#print ('Area:',area_final)
				#print ('largura:',largura(teste))
				#print ('Circularidade:',circularidade(teste))
				imagem_aux = desenhando(cor,j[0])
				#mostrar_imagem(imagem_aux)
				tag = str(num) + "." + str(j[2])	
				salvar(imagem_aux,num,tag,'4_Contornos\\')
				listandoContornos.append((j[0],i))	





