from matplotlib import pyplot as plt
from datetime import datetime
from random import randint
import pandas as pd
import numpy as np
import cv2 as cv
import json
import math
import csv
import os

##VERIFICAR -> SE EU LIMPAR UMA SUB_IMAGEM E TIRAR A DIFERENÇA DELA COM A ORIGINAL, EU CONSIGO IDENTIFICAR SUB_IMAGENS QUE POSSUA MUITOS PONTOS
## DE FALHA DENTRO DELA, PODENDO INFERIR QUE É UMA REGIÃO QUE POSSIVELMENTE APRESENTE A IRREGULARIDADE DE UM BURACO? OU ENTÃO VERIFICAR PELA TAXA DE CONTORNOS DENTRO DELA
#	https://docs.opencv.org/3.4/d5/d69/tutorial_py_non_local_means.html
def limpar(imagem):
	dst = cv.fastNlMeansDenoising(imagem,None,10,7,21)
	return dst

#Toda imagem possui um histograma com a distribuição das suas cores (PRINCIPALMENTE QUANDO SE ESTÁ NA GRAY SCALE)
#	Essa função ajuda a expandir um pouco mais esse histograma, para deixar a imagem com alguns pontos mais destacados
#	https://docs.opencv.org/master/d5/daf/tutorial_py_histogram_equalization.html
def equalizar(imagem):
	clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(5,5))
	cl1 = clahe.apply(imagem)
	return cl1

#Está função define um RANGE no qual irá utilizar para binarizar a imagem
#	https://docs.opencv.org/master/d7/d4d/tutorial_py_thresholding.html
def thresholding(imagem):
	ret,th = cv.threshold(imagem,0,255,cv.THRESH_BINARY + cv.THRESH_OTSU)
	#th2 = cv.adaptiveThreshold(imagem,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,11,2)
	#th3 = cv.adaptiveThreshold(imagem,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)

	return th

#Está função pega a IMAGEM e identifica seus contornos
#	https://docs.opencv.org/master/da/d22/tutorial_py_canny.html
def canny(imagem):
	teste = cv.Canny(imagem,100,200)
	return teste

#Está função tem como objetivo pegar uma IMAGEM CANNY e gerar seus CONTORNOS e HIERARQUIAS
def contornos(imagem):
	contornos, hierarquia = cv.findContours(imagem, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
	return (contornos,hierarquia)

#Não utilizada atualmente, já que não é necessario ter uma informação da SUB SUB_IMAGEM, então o que está sendo analisado
#	já está salvo em algum outro lugar
def salvar(imagem, i,j,flag):
	#destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	destino = "c:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\"
	final = destino + flag + 'Contorno_' + str(i) + '.' + str(j) + '.png'

	#print(final)
	cv.imwrite(final,imagem)

def desenhando(imagem,contornos):
	cv.drawContours(imagem,[contornos],0,(0,0,255),3)
	return imagem

#AS FUNÇÕES ACIMA FORAM UTILIZADAS PARA TESTES, COM A ORGANIZAÇÃO DOS CÓDIGOS, É IMPORTANTE MODULARIZAR ELE A PONTO DE PODER REALIZAR
#	NOVOS TESTES A FIM DE UM MELHOR ESTUDO DO QUE PODE AJUDAR NA DETECÇÃO DE BURACOS

#----------------------------------------------------------------------------------------------------------------------------------------------
#AS FUNÇÕES A BAIXO, ESTÃO EM UTILIZAÇÃO CONSTANTE

#RESPONSAVEL POR ENCONTRAR OS LIMITES DA SUBIMAGEM
def limites(height, width, lista_pontos):
	listaX = []
	listaY = []

	#Verificar o porque em alguns casos os novo_contorno termina por acusar um valor fora da faixa do tamanho da sua sub_imagem
	for i in range(0,4):
		x , y = lista_pontos[i]
		listaX.append(x)
		listaY.append(y)

	x_min,x_max = min(listaX),max(listaX)
	y_min,y_max = min(listaY),max(listaY)

	if (x_max >= width):
		x_max = width-1
	
	if(x_min < 0):
		x_min = 0
	
	if (y_max >= height):
		y_max = height-1
	
	if(y_min < 0):
		y_min = 0 

	return x_min,y_min,x_max,y_max

#RESPONSAVEL PELA IDENTIFICAÇÃO DOS VALORES QUE EXCEDEM A SUB_IMAGEM, FORMANDO AS 8 REGIÕES AO SEU REDOR, [N,S,L,O,NO,NE,SO,SE]
def limites_externos(height,width,height_Regiao,width_Regiao,x_min,y_min,x1_max,y1_max):

	if(x_min - int(width_Regiao/2) >= 0):
		x_min -= int(width_Regiao/2)
	else:
		x_min = 0

	if(x1_max + int(width_Regiao/2) < width):
		x1_max += int(width_Regiao/2)
	else:
		x1_max = width


	if(y_min - int(height_Regiao/2) >= 0):
		y_min -= int(height_Regiao/2)
	else:
		y_min = 0

	if(y1_max + int(height_Regiao/2) < height):
		y1_max += int(height_Regiao/2)
	else:
		y1_max = height

	#print ("|Iniciais: ",x,'|',y,"|Finais:",'|',x1,'|',y1)
	return x_min,y_min,x1_max,y1_max

#FUNÇÃO RESPONSAVEL POR PERCORRER OS LIMITES 'INTERNOS' ATE OS 'EXTERNOS' da SubImagem PARA IDENTIFICAR A DISTRIBUIÇÃO DOS VALORES [0-255]
def definindo_regiao(x,x1,y,y1 ,imagem): 
	
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
				if(width <= 256 and (206 <= (width + height)) or (width > 256 and ((width - height) <= 296))):
                    #imagem_copia[j][i] = (0,0,255)
					indice = imagem[height][width]
					dicio[str(indice)] = dicio[str(indice)] + 1
				else:
					pass

		#print(lista)			
		#plt.ylabel('Gauss')
		#plt.show()
		for val in dicio.values():
			lista.append(val)
		
		#plt.bar(range(255),lista)
		#plt.show()
		return (lista)

def take(elem):
	return elem[1]

#AQUI É REALIZADO UMA PORCENTAGEM SIMPLES, TALVEZ SEJA A MELHOR ABORDAGEM, JÁ QUE É DIFICIL ESTIMAR UM PESO PARA OS INTERVALO DE (0-255) 
def estimando_regiao(width_subImagem,height_subImagem,lista):
	r1,r2,r3 = 0,0,0

	for i in range(0,len(lista)-1):
		if (i <= 85):
			if(lista[i] != 0):  
				r1 += lista[i]

		elif (i > 85 and i <= 170):
			if(lista[i] != 0):
				r2 += lista[i] 
		elif(i > 170):
			if(lista[i] != 0):
				r3 += lista[i]
		else:
			pass 

	'''OBS: VERIFICAR A POSSIBILIDADE DE UMA ANALISE POR R1/(WIDTH_SUBIMAGEM * HEIGHT_SUBIMAGEM), TALVEZ RELACIONANDO A QUANTIDADE DE PIXELS NOS SEUS RESPECTIVOS VALORES DE [0,255]
			PELO TOTAL DE PIXELS DA REGIÃO DA SUBIMAGEM,  TRAGA UMA TAXA MELHOR DE QUAL REGIÃO ESTÁ MAIS REPRESENTADA DE ACORDO COM OS CORTES E AS QUANTIDADES TOTAIS'''
	'''media_1 = r1 / (width_subImagem * height_subImagem) , sendo r1 a quantidade dos pixels nas faixas de 0-85, 85-170, 170-255 '''
	
	if(width_subImagem == 0 or height_subImagem == 0):
		media_1,media_2,media_3 = 0,0,0
	else:
		area = width_subImagem * height_subImagem
		
		porcent_1 = ( area - r1 ) / area
		porcent_2 = ( area - r2 ) / area
		porcent_3 = ( area - r3 ) / area
		
		media_1 = ( 1 - porcent_1 ) * 100
		media_2 = ( 1 - porcent_2 ) * 100
		media_3 = ( 1 - porcent_3 ) * 100
			
	listando = []
	listando.append(("Escuro",media_1))
	listando.append(("Cinza",media_2))
	listando.append(("Claro",media_3))
	listando = sorted(listando,reverse=True,key=take)
	#print (":: ",listando)

	if (media_1 == media_2 == media_3 == 0):
		return ("Indefinido",0.0)
	else:
		if(listando[0][1] == listando[1][1] == listando[2][1]):
			return ("Iguais",listando[0][1])
		else:	
			return listando[0]

#O objetivo desta função é verificar quantas regiões iguais a REGIÃO PRINCIPAL existem, e quantas vezes ela se REPETE, talvez isso possa ajudar a diferenciar uma
#	região de buraco e uma que só possui alguma mancha ou algo do tipo.
def consecutivo(lista):
	l = {'N':0,'NL':0,'L':0,'SL':0,'S':0,'SO':0,'O':0,'NO':0}
	atual,value,qtd_consecutivo,qtd_repete_consecutivo = 0,0,0,0

	for i in lista:
		if(i[0] != 'P'):
			l[i[0]] = 1
		else:
			pass

	r = {}
	for i in l.values():
		if(i == 1):
			atual += 1
		elif(i == 0):
			if(r.get(atual) ==  True):
				r[atual] += 1
				atual = 0
			else:
				r[atual] = 1
				atual = 0
		else:
  			pass
	
	r[atual] = 1

	#print("AAOUDHIUSBDAU SD: ",l)
	#print("ASDKANODIANDOIA ASDOIAIDONAID: ",r)
	value = dict(sorted(r.items()))
	#print("AS DAJBDAIUBD: ",value)
	qtd_consecutivo,qtd_repete_consecutivo = list(value.items())[-1]

	return qtd_consecutivo,qtd_repete_consecutivo

#Esta funcao recebe como parametro a lista contendo ('SIGLA_REGIAO','TIPO_DE_COR_REGIAO','VALOR_MEDIA_DA_COR_DA_REGIAO')
#Percorrendo essa lista, é separado as tuplas que possuem os mesmos 'TIPOS_DE_COR_REGIAO' Ex: Escuro, Claro, Cinza......
#Depois é verificado em qual das listas está a 'SIGLA_REGIAO' -> 'P', então ,é retornado o tamanho da lista que contém a região principal 'P'
#	uma lista das LISTAS DAS REGIÕES, e a quantidade de vezes que o TIPO DA REGIÃO PRINCIPAL , apareceu ao seu ARREDOR e quantas vezes essa quantidade se repetiu
def relacionando_regiao(lista):	
	listaEs,listaCi,listaCl,listaIn,listaIg = [], [], [], [], []
	valor = 0
	flag = ''
	qtd_consecutivo = 0 
	qtd_aparece = 0

	#print("MINHA LISTA ------------------------------ \n",lista)

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
	
	listaTotal = []
	for j in [listaEs,listaCi,listaCl,listaIn,listaIg]:
		if(len(j) != 0):
			listaTotal.append(j)
	
	#print("HAHAHAHAH\n")
	#print(listaTotal)
	#print(len(listaTotal))
	#print(listaTotal[0][0][0])

	if(len(listaTotal) == 1 and listaTotal[0][0][0] == 'P'):
		#print('O VALOR VEIO PARA CA \n')
		qtd_consecutivo,qtd_aparece = consecutivo(listaTotal[0])
		return len(listaTotal[0]),[len(listaEs),len(listaCi),len(listaCl),len(listaIg),len(listaIn)],qtd_consecutivo,qtd_aparece

	for i in listaTotal:
		#print('TESTE:\n',i)
		try:
			#print('EITAAAAAA :' , i[0][0])
			if(i[0][0] == 'P'):
				#print('PORQUE NAO DEU CERTO')
				qtd_consecutivo,qtd_aparece = consecutivo(i)
				valor = len(i)
				return len(i),[len(listaEs),len(listaCi),len(listaCl),len(listaIg),len(listaIn)],qtd_consecutivo,qtd_aparece
		except:
			pass
	#print("NENHUMA LISTA FUNCIONOU -------------------------------------------------")
	return valor,[len(listaEs),len(listaCi),len(listaCl),len(listaIg),len(listaIn)],qtd_consecutivo,qtd_aparece

#A relação entre as duas areas ocorre de forma a identificar qual a área da subimagem em relação a sua imagem mae #(Imagem_Original / Sub_Imagem)
def area_interesse(area_Imagem,area_SubImagem):
	try:
		area = ((area_Imagem - area_SubImagem) / area_Imagem)
		variacao_porcent = ((1 - area) * 100)
		return variacao_porcent
	except:
		return 0

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

#FUNÇÕES AUXILIARES
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


#----------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

	#origem = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\FEATURES\\"
	#origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Origem/'
	#origem_2 = 'C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\1_Especial\\'
	#subimagem ='/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/3_SubImagens/'
	#destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	#subimagem = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\3_SubImagens\\"
	#listasPosicoes = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\0_Listas_Posicoes\\"
	#origem = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_Google_Maps\\"
	#destino = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\"

	origem = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_IC\\Origem_Imagens\\Imagens_Google_Maps\\"
	jsonPosicoes = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_IC\\Destino_Imagens\\Arquivo_Posicoes\\"
	destino = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_IC\\Destino_Imagens\\"

	tabela = [{"NUM_ORIGIN":0, "NUM_SUB":0, "X_POS":0, "Y_POS":0, "AREA_ORIGIN":0, "AREA_SUB":0, "AREA_SUB_ORIGINAL":0, "COMPRIMENTO_ORIGIN":0, "COMPRIMENTO_SUB":0,
        	  "LARGURA_ORIGIN":0, "LARGURA_SUB":0, "ALTURA_ORIGIN":0, "ALTURA_SUB":0, "CIRCULARIDADE_SUB":0, "DESVIO_PADRAO_SUB":0,
        	  "QTD_REGIOES_ESCURO": 0, "QTD_REGIOES_CINZA": 0, "QTD_REGIOES_CLARO": 0, "QTD_REGIOES_IGUAIS": 0, "QTD_REGIOES_INDEFINIDO": 0,	
			  "REGIAO_P":0, "MEDIA_REGIAO_P":0, "REGIAO_N":0, "MEDIA_REGIAO_N":0, "REGIAO_S":0, "MEDIA_REGIAO_S":0, "REGIAO_L":0, "MEDIA_REGIAO_L":0,
			  "REGIAO_O":0, "MEDIA_REGIAO_O":0, "REGIAO_NO":0, "MEDIA_REGIAO_NO":0, "REGIAO_NL":0, "MEDIA_REGIAO_NL":0, "REGIAO_SL":0,
			  "MEDIA_REGIAO_SL":0, "REGIAO_SO":0, "MEDIA_REGIAO_SO":0, "QTD_REGIOES":0, "QTD_REGIOES_VALIDAS":0,"QTD_REGIOES_CONSECUTIVO":0,
			  "QTD_APARECIMENTO":0, "CLASSE":0
			}]

	dataFrame = pd.DataFrame(tabela)
	dataFrame = dataFrame[["NUM_ORIGIN","NUM_SUB","X_POS","Y_POS","AREA_ORIGIN","AREA_SUB","AREA_SUB_ORIGINAL","COMPRIMENTO_ORIGIN","COMPRIMENTO_SUB","LARGURA_ORIGIN",
			"LARGURA_SUB","ALTURA_ORIGIN","ALTURA_SUB","CIRCULARIDADE_SUB","DESVIO_PADRAO_SUB","QTD_REGIOES_ESCURO","QTD_REGIOES_CINZA","QTD_REGIOES_CLARO",
			"QTD_REGIOES_IGUAIS","QTD_REGIOES_INDEFINIDO","REGIAO_P","MEDIA_REGIAO_P","REGIAO_N","MEDIA_REGIAO_N","REGIAO_S","MEDIA_REGIAO_S",
			"REGIAO_L","MEDIA_REGIAO_L","REGIAO_O","MEDIA_REGIAO_O","REGIAO_NO","MEDIA_REGIAO_NO","REGIAO_NL","MEDIA_REGIAO_NL","REGIAO_SL",
			"MEDIA_REGIAO_SL","REGIAO_SO","MEDIA_REGIAO_SO","QTD_REGIOES","QTD_REGIOES_VALIDAS","QTD_REGIOES_CONSECUTIVO","QTD_APARECIMENTO","CLASSE"]]
	
	timestamp = datetime.now()
	date = str(timestamp.year) + str(timestamp.month) + str(timestamp.day) + "_" + str(timestamp.hour) + "_" + str(timestamp.minute) + "_" + str(timestamp.minute) 
	dataFrame.to_csv("C:\\Nova pasta\\Projetos Git\\IC\\" + "prov_all_" + date + ".csv",header=True,index=False)

	for _, _, quantidade in os.walk(origem):
		pass

	for _, _, listas in os.walk(jsonPosicoes):
		pass
	
	print(quantidade,'\n')
	print(listas,'\n')
	q0 = 0
	q1 = 0
	
	for im in quantidade:
		print("*******************************************************",im,"*******************************************************")
		#arq = open(jsonPosicoes + "STRUCT_BASE_" + im.split('.')[0] + ".", 'r')
		#texto = arq.read()
		#aux = list(eval(texto))
		num = im.split('.')[0]

		with open(jsonPosicoes + "STRUCT_BASE_" + im.split('.')[0] + ".json") as f:
			image_json = json.load(f)

		print(image_json['1']['limites'])
		print(image_json['1']['circularidade'])
		print(image_json['1']['desvio_padrao'])

		#MODIFICAR PARA CONSEGUIR CLASSIFICAR
		leitura = origem + im
		imagem = cv.imread(leitura)
		cor = imagem[256:512,0:512]                                                                    

		#im_resize = cv.resize(imagem,(512,512))
		#im_resize2 = im_resize[150:310,50:462]
		#im_resize3 = cv.resize(im_resize2,(512,512))
		#cor = im_resize3[256:512,0:512]
		#imagem_cinza = cv.cvtColor(cor,cv.COLOR_RGB2GRAY)
		#mostrar_imagens(im_resize,im_resize2,im_resize3,cor)
		#mostrar_imagens(im_resize,im_resize3,imagem_cinza,cor)
		
		#Aqui, é realizado a leitura da IMAGEM que foi feito a EROSAO para tentar identificar melhor os BURACOS
		#Embora a imagem seja cinza, ela ainda possui 3 canais de cores, por isso é feito a conversão RGB2GRAY
		cinza_aux = cv.imread("C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_IC\\Destino_Imagens\\Imagens_Selecionadas_Analise_Geral\\" + num + "_Erosao.png")
		imagem_cinza = cv.cvtColor(cinza_aux,cv.COLOR_RGB2GRAY)
		
		height_Original, width_Original = imagem_cinza.shape[:2]
		listandoContornos = []
		
		#Aqui, é realizado o percurso de CADA ARQUIVO de IMAGEM, ou seja, essa interação passa por cada SUBIMAGEM para ANALISE
		for index_json in image_json.keys():
			subImagem = cor.copy()
			lxi0, lyi0, lxi1, lyi1 = limites(height_Original, width_Original , image_json[str(index_json)]["limites"])

			#Aqui são definidos alguns parametros da Região da Imagem de Interesse (area,comprimento,circularidade,lagura,comprimento)       
			width_SubImagem = (lxi1-lxi0)
			height_SubImagem = (lyi1-lyi0)

			area_Imagem = height_Original*width_Original
			area_SubImagem =  height_SubImagem * width_SubImagem

			comp_Imagem = 4*height_Original
			comp_SubImagem = 2*width_SubImagem + 2*height_SubImagem

			larg_Imagem = width_Original	
			larg_SubImagem = width_SubImagem

			alt_Imagem = height_Original
			alt_SubImagem = height_SubImagem
							
			area_SubOriginal = area_interesse(area_Imagem, area_SubImagem)

			#x_med = round((lxi1+lxi0)/2)
			#y_med = round((lyi1+lyi0)/2)
			
			#RESPONSAVEL POR DEFINIR A REGIÃO DE ANALISE AO REDOR DA SubSubImagem, DE ACORDO COM O TAMANHO ORIGINAL DA IMAGEM
			lxe0, lye0, lxe1, lye1 = limites_externos(height_Original,width_Original,height_SubImagem,width_SubImagem,lxi0,lyi0,lxi1,lyi1)

			#RESPONSAVEL POR PERCORRER AS REGIÕES AO REDOR DA REGIÃO PRINCIPAL PARA FUTURAMENTE TENTAR ESTIMAR
			#	ALGUMAS INFORMAÇÕES A MAIS A PARTIR DA RELAÇÃO ENTRE ELAS E A PARTE PRINCIPAL
			#AO TODo ESTÃO DEFINIDOS A REGIÃO PRINCIPAL (P), E MAIS 8 REGIÕES (Norte,Sul,Leste,Oeste,Nordeste,Noroeste,Sudeste,Sudoeste)

			#jsonPosicaoSubImagens = {'P':[lxi0,lxi1,lyi0,lyi1],'N':[lxi0,lxi1,lye0,lyi0],'S':[lxi0,lxi1,lyi1,lye1],'L':[lxi1,lxe1,lyi0,lyi1],
			#						 'O':[lxe0,lxi0,lyi0,lyi1],'NO':[lxe0,lxi0,lye0,lyi0],'NL':[lxi1,lxe1,lye0,lyi0],'SL':[lxi1,lxe1,lyi1,lye1],
			#						 'SO':[lxe0,lxi0,lyi1,lye1]}
			#listaTotal = []
			#for regiao in jsonPosicaoSubImagens.keys():
			#	listaRegiaoRetorno = definindo_regiao(jsonPosicaoSubImagens[regiao],imagem_cinza)
			#	listaTotal.append([regiao , listaRegiaoRetorno ,[pos[1]-pos[0],pos[3]-pos[2]]])
			
			listaPosicoes = [['P',[lxi0,lxi1,lyi0,lyi1]],['N',[lxi0,lxi1,lye0,lyi0]],['S',[lxi0,lxi1,lyi1,lye1]],
							['L',[lxi1,lxe1,lyi0,lyi1]],['O',[lxe0,lxi0,lyi0,lyi1]],['NO',[lxe0,lxi0,lye0,lyi0]],
							['NL',[lxi1,lxe1,lye0,lyi0]],['SL',[lxi1,lxe1,lyi1,lye1]],['SO',[lxe0,lxi0,lyi1,lye1]]]

			listaTotal = []
			for d_r in listaPosicoes:
				pos = d_r[1]
				aux_ = definindo_regiao(pos[0],pos[1],pos[2],pos[3],imagem_cinza)
				listaTotal.append([d_r[0] , aux_ ,[pos[1]-pos[0],pos[3]-pos[2]]])
				#cor[pos[2]:pos[3],pos[0]:pos[1]] = (randint(0,254),randint(0,254),randint(0,254))
				#mostrar_imagem(cor)
				
			#listaTotal = [['P',listaP,[x,y]],['N',listaN,[x,y]],['S',listaS,[x,y]],['L',listaL,[x,y]],['O',listaO,[x,y]],
			#['NO',listaNO,[x,y]],['NL',listaNL,[x,y]],['SL',listaSL,[x,y]],['SO',listaSO,[x,y]]]
			#--------------------------------------------------------------------------------------------------------------#
			print ('Definindo media das regiões\n')
			
			listaRegiao = []
			media = []
			#Percorre a lista de tuplas que indicam a posição da regiao e sua lista/histograma definida por "definindo_regiao"
			for estimando in listaTotal:
				regiao, media = estimando_regiao(estimando[2][0],estimando[2][1],estimando[1])
				listaRegiao.append((estimando[0],regiao,media))
				#print ("Relacionando as regiões: [%s] | [%f] | [%f]" ,estimando[0],regiao,media)
				
			#--------------------------------------------------------------------------------------------------------------#
			print ('Relacionando valores de regiões\n')
			valor,qtd_regioes,qtd_regioes_consecutivos,qtd_aparecimento = relacionando_regiao(listaRegiao)		
		
			if(valor is None):
				print("Valor None Retornado")
				valor = 0
			elif(valor > 1):
				print ("Existem regiões com valores aproximados")
			else:
				print ("Não existem regiões com valores aproximados -> ",valor)
			#---------------------------------------------------------------------------------------------------------------------
			
			#cv.drawContours(subImagem,[novos_contornos],0,(0,0,255),3)
			#mostrar_imagem(subImagem)

			print("\nInformacoes para auxilio da classificacao\n")
			print("POSICOES [",lxi0,",",lxi1," | ",lyi0,", ",lyi1,"]")
			print('AREA_SUBIMAGEM -> | ',area_SubImagem)
			print("QTD_REGIOES_GERAIS -> | ", qtd_regioes)	
			print('QTD_REGIOES_PRINCIPAL -> | ' , valor)
			
			classe = 0
			if(area_SubImagem > 300):
				if((lxi0 <= 256 and (246 <= (lxi0 + lyi0))) or (lxi0 > 256 and ((lxi1 - lyi0) <= 266))): #Verificar essa etapa para aumentar a região de limite e analise
					if(valor <= 5):
						sub = subImagem
						sub2 = cor.copy()
						sub[lyi0:lyi1,lxi0:lxi1] = (255, 255, 255)
						cv.rectangle(sub2,(lxi0,lyi0),(lxi1,lyi1),(100,0,150),3)
						mostrar_imagens(imagem, imagem_cinza,sub,sub2)
						classe = input("POSSIVEL BURACO?: ")
						classe = 1
						q1 += 1

					else:
						sub = subImagem
						sub2 = cor.copy()
						sub[lyi0:lyi1,lxi0:lxi1] = (255, 255, 255)
						cv.rectangle(sub2,(lxi0,lyi0),(lxi1,lyi1),(100,0,150),3)
						mostrar_imagens(imagem, imagem_cinza,sub,sub2)
						classe = input("O QUE EH ISSO?: ")
						classe = 0
						q0 += 0 
					
					if(classe is None):
						classe = 0


					#if(q0 <= 500 or (q1 <= 200 and classe == 1)):
					tabela = [{"NUM_ORIGIN":num,"NUM_SUB":index_json,"X_POS":lxi0,"Y_POS":lyi0,"AREA_ORIGIN":area_Imagem,"AREA_SUB":area_SubImagem,
					"AREA_SUB_ORIGINAL":area_SubOriginal,"COMPRIMENTO_ORIGIN":comp_Imagem,"COMPRIMENTO_SUB":comp_SubImagem,"LARGURA_ORIGIN":larg_Imagem,
					"LARGURA_SUB":larg_SubImagem, "ALTURA_ORIGIN":alt_Imagem,"ALTURA_SUB":alt_SubImagem,"CIRCULARIDADE_SUB":image_json[str(index_json)]["circularidade"],
					"DESVIO_PADRAO_SUB":image_json[str(index_json)]["desvio_padrao"],"QTD_REGIOES_ESCURO": qtd_regioes[0], "QTD_REGIOES_CINZA": qtd_regioes[1],
					"QTD_REGIOES_CLARO": qtd_regioes[2],"QTD_REGIOES_IGUAIS": qtd_regioes[3],"QTD_REGIOES_INDEFINIDO": qtd_regioes[4],"REGIAO_P":listaRegiao[0][1],
					"MEDIA_REGIAO_P":listaRegiao[0][2],"REGIAO_N":listaRegiao[1][1],"MEDIA_REGIAO_N":listaRegiao[1][2],"REGIAO_S":listaRegiao[2][1],
					"MEDIA_REGIAO_S":listaRegiao[2][2],"REGIAO_L":listaRegiao[3][1],"MEDIA_REGIAO_L":listaRegiao[3][2],"REGIAO_O":listaRegiao[4][1],
					"MEDIA_REGIAO_O":listaRegiao[4][2],"REGIAO_NO":listaRegiao[5][1],"MEDIA_REGIAO_NO":listaRegiao[5][2],"REGIAO_NL":listaRegiao[6][1],
					"MEDIA_REGIAO_NL":listaRegiao[6][2],"REGIAO_SL":listaRegiao[7][1],"MEDIA_REGIAO_SL":listaRegiao[7][2], "REGIAO_SO":listaRegiao[8][1],
					"MEDIA_REGIAO_SO":listaRegiao[8][2],"QTD_REGIOES":valor,"QTD_REGIOES_VALIDAS": 9 - qtd_regioes[4],"QTD_REGIOES_CONSECUTIVO":qtd_regioes_consecutivos,
					"QTD_APARECIMENTO":qtd_aparecimento,"CLASSE":classe
							}]

					dataFrame = pd.DataFrame(tabela)
					dataFrame = dataFrame[["NUM_ORIGIN","NUM_SUB","X_POS","Y_POS","AREA_ORIGIN","AREA_SUB","AREA_SUB_ORIGINAL","COMPRIMENTO_ORIGIN","COMPRIMENTO_SUB",
					"LARGURA_ORIGIN","LARGURA_SUB","ALTURA_ORIGIN","ALTURA_SUB","CIRCULARIDADE_SUB","DESVIO_PADRAO_SUB","QTD_REGIOES_ESCURO","QTD_REGIOES_CINZA",
					"QTD_REGIOES_CLARO","QTD_REGIOES_IGUAIS","QTD_REGIOES_INDEFINIDO","REGIAO_P","MEDIA_REGIAO_P","REGIAO_N","MEDIA_REGIAO_N","REGIAO_S","MEDIA_REGIAO_S",
     				 "REGIAO_L","MEDIA_REGIAO_L","REGIAO_O","MEDIA_REGIAO_O","REGIAO_NO","MEDIA_REGIAO_NO","REGIAO_NL","MEDIA_REGIAO_NL","REGIAO_SL",
     				 "MEDIA_REGIAO_SL","REGIAO_SO","MEDIA_REGIAO_SO","QTD_REGIOES","QTD_REGIOES_VALIDAS","QTD_REGIOES_CONSECUTIVO","QTD_APARECIMENTO","CLASSE"]]				
						##print("+++++++++++++++++++++++++++++++++++++++++++ SALVO NO CSV ++++++++++++++++++++++++++++++++++++++++++++")
					dataFrame.to_csv("C:\\Nova pasta\\Projetos Git\\IC\\" + "prov_all_" + date + ".csv" ,header=False, mode='a',index=False)