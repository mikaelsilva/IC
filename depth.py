from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import cv2 as cv
import math
import os


def area(contornos):
    a = cv.contourArea(contornos)
    if a == None:
        a = 0.0
    return a

#	A relação entre as duas areas de fato ocorre de maneira a 
#ser definada como Area_Sub_Menor / Area_Original_Ou_SubAnterior
def area_interesse(area_Imagem,area_SubImagem):

	try:
		area = area_SubImagem / area_Imagem 
		area = area_SubImagem*100
		return area
	except:
		return -1
		
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

def relacionando_tamanho(largura,comprimento):
	retorno = 0 
		
	try:
		if(largura > comprimento):
			retorno =  comprimento/largura 
			return retorno
		else:
			retorno =  largura/comprimento
			return retorno
	except:
		return retorno
	


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

#VERIFICADA, RESPONSAVEL POR RECEBER A SUB-IMAGEM CINZA E GERAR UMA 
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
	imagem2, contornos, hierarquia = cv.findContours(imagem, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
	return (imagem2,contornos,hierarquia)

def desenhando(imagem,contornos):
	cv.drawContours(imagem,[contornos],0,(0,0,255),3)
	return imagem

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
		x2 = width
	
	if(x1 < 0):
		x1 = 0
	
	if (y2 > height):
		y2 = height
	
	if(y1 < 0):
		y1 = 0 
	
	#print ("Limites na função:", x1,x2,y1,y2)
	return x1,y1,x2,y2

#RESPONSAVEL PELA IDENTIFICAÇÃO DASOS VALORES QUE EXCEDEM A 
# SUB_SUB_IMAGEM  FORMANDO AS 6 REGIÕES AO REDOR DA REGIÃO 
# #IDENTIFICADA COMO UMA POSSIVEL ANOMALIA NA ESTRADA
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

	#print ('Limites:','[',x,'-',x1,']','|','[',y,'-',y1,']')
	#print ("Valores: ",[width,height])
	
	if(x == x1 or y == y1):
		return (lista)
	else:
		for i in range(y,y1): #height
			for j in range(x,x1): #width
				if (imagem[i][j] == -1):
					indice = imagem[i][j]
					lista[indice] += 2
				else:
					indice = imagem[i][j]
					lista[indice] += 1
		#plt.plot(lista)
		#plt.ylabel('Gauss')
		#plt.show()

		return (lista)


def take(elem):
	return elem[1]

def estimando_regiao(lista,flag):
	r1 = -1
	m1 = 0
	r2 = -1
	m2 = 0
	r3 = -1
	m3 = 0

	#print ("-------------------------------------------------------------------------------------------")
	#print ("Flag ", flag)

	'''OBS: Aqui é realizado uma média ponderada, talvez ela não seja interessante para utilização porque fica mais dificil fazer
		a comparação entre as regiões, enquanto que para uma media normal, apenas pela quantidade daquele intervalo divido pela 
		quantidade analisada fique melhor de identificar qual região obteve um maior numero de elementos
		print ("Listando: ",lista)

		for i in range(0,len(lista)-1):
			if (i <= 85):
				if(lista[i] != -1):
				r1 += i*lista[i]
					m1 += i
			
			elif (i > 85 and i <= 170):
			if(lista[i] != -1):
				r2 += i*lista[i]
				m2 += i
		else:
			if(lista[i] != -1):
				r3 += i*lista[i]
				m3 += i
	'''
	for i in range(0,len(lista)-1):
		if (i <= 85):
			if(lista[i] != -1):
				r1 += lista[i]
				m1 += 1
			
		elif (i > 85 and i <= 170):
			if(lista[i] != -1):
				r2 += lista[i]
				m2 += 1
		else:
			if(lista[i] != -1):
				r3 += lista[i]
				m3 += 1

	if (m1 == 0):
		m1 = 1
	if (m2 == 0):
		m2 = 1
	if (m3 == 0):
		m3 = 1
	
	r1 = (r1/m1)
	r2 = (r2/m2)
	r3 = (r3/m3)
		
	print ("R1: ",r1, "and","M1: ",m1)
	print ("R2: ",r2, "and","M2: ",m2)
	print ("R3: ",r3, "and","M3: ",m3)

	#print ("-------------------------------------------------------------------------------")

	listando = []
	listando.append(("Escuro",r1))
	listando.append(("Cinza",r2))
	listando.append(("Claro",r3))
	listando = sorted(listando,reverse=True,key=take)
	print (":: ",listando)

	if (r1 == r2 == r3 == -1):
		return ("Indefinido",-1)
	else:
		print('A',listando[0])
		return listando[0]
	
def porcentagem(lista,indice):
	valor = 1

	for i in range(0,len(lista)-1):
		if (i != indice):
			try:
				porcent = lista[i][2] / lista[indice][2] #(Valor_menor / Valor_maior)
			except Exception as e:
				porcent = lista[i][2] / (-1)
				
				'''if(int(lista[i][2]) != 0):
					porcent = (lista[i][2]/(lista[i][2])*3)
				else:
					porcent = lista[i][2]/3
				pass'''

			if (porcent*100 >= 60):
				valor += 1
	return valor

#VERIFICAR PARA PASSAR A LISTA QUE ESTÁ O ELEMENTO PRINCIPAL, PARA QUE OUTRAS ANALISES POSSAM ACONTECER
def relacionando_regiao(lista):
	listaEs = []
	listaCi = []
	listaCl = []
	valor = 0
	flag = ""
	indice = 0
	
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

	if(flag == "Es"):
		for i in range(0,len(listaEs)-1):
			if(listaEs[i][0] == 'P'):
				indice = i
		valor = porcentagem(listaEs,indice)
		
			
	if(flag == "Ci"):
		for i in range(0,len(listaCi)-1):
			if(listaCi[i][0] == 'P'):
				indice = i
		valor = porcentagem(listaCi,indice)

	if(flag == "Cl"):
		for i in range(0,len(listaCl)-1):
			if(listaCl[i][0] == 'P'):
				indice = i
		valor = porcentagem(listaCl,indice)
		
	'''
	for i in range(0,len(listaCl)-1):
		if(listaCl[i][0] == 'P'):
			valor = porcentagem(listaCl,i)
			if(valor > 1):
				return valor
			else:
				return 0


			if(valor > 1):	
				return valor
			else:
				return 0
	'''
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
	origem = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Origem/'
	origem2 = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Origem_Fake/'
	subimagem ='/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/3_SubImagens/'

	destino = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Imagens_F/'
	especial = '/media/study/Arquivos HD 2/Aprender/Areas de Atuação/Processamento de Imagens/Imagens/Origem/'

	tabela = [{'NUM_I':0,"NUM_J":0,'AREA_IMAGEM':0.0,"AREA_SUB_IMAGEM":0.0,"AREA_SUB_CONTORNO":0.0,"COMPRIMENTO":0.0,"LARGURA":0.0,"ALTURA":0.0,"CIRCULARIDADE":0.0,"REGIAO":"null"}
             ]

	df = pd.DataFrame(tabela)
	df = df[['NUM_I',"NUM_J",'AREA_IMAGEM','AREA_SUB_IMAGEM','AREA_SUB_CONTORNO','COMPRIMENTO','LARGURA','ALTURA','CIRCULARIDADE','REGIAO']]	 
	df.to_csv('ic.csv',header=True,index=False)
	

	for _, _, quantidade in os.walk(origem2):
		pass

	for _, _, arquivo in os.walk(subimagem):
		pass


	count = 0
	for cast in quantidade:
		cast = cast.split('.')
		num = int(cast[0])
		listandoContornos = []
		
		count = contando_subimagens(cast[0],arquivo)
		print ("AQUI [%d] ate [%d]" %(1,count))

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

			imagema,imagem_contorno,imagemc = contornos(imagem)
			
			#INICIANDO CORREÇÃO DO CÓDIGO ABAIXO
			#-----------------------------------------------------------------------------------

			#RESPONSAVEL POR PERCORRER CADA SubSubImagem que foi encontrada na SubImagem que pode ser um possivel buraco/mancha/rachadura
			for j in range(0,len(imagem_contorno)-1):
				subImagem = cor.copy()

				teste = imagem_contorno[j]
				
				quadrado = cv.minAreaRect(teste)
				novos_contornos = cv.boxPoints(quadrado)
				novos_contornos = np.int0(novos_contornos)

				a = area(novos_contornos)
				#print(a)
				
				print ("Definindo regiões e seus valores")

				#RESPONSAVEL POR DEFINIR OS LIMITES EM (x,y) DA SubSubImagem
				lxi0, lyi0, lxi1, lyi1 = limites(height,width,novos_contornos)
				print(lxi0, lyi0, lxi1, lyi1)
				#Aqui são definidos alguns parametros da SubSubImagem (area,comprimento,circularidade,lagura,comprimento)       
				area_SubSubImagem = (lxi1-lxi0) * (lyi1-lyi0)    #width * height
				comp_SubSubImagem = comprimento(teste)
				circ_SubSubImagem = circularidade(teste)
				width_SubSubImagem = (lxi1-lxi0)
				height_SubSubImagem = (lyi1-lyi0)

				#RESPONSAVEL POR DEFIIR A REGIÃO DE ANALISE AO REDOR DA SubSubImagem, DE ACORDO COM O TAMANHO ORIGINAL DA IMAGEM
				lxe0, lye0, lxe1, lye1 = limites_externos(height_SubImagem,width_SubImagem,height_SubSubImagem,width_SubSubImagem,lxi0,lyi0,lxi1,lyi1)

				#print (height,width)
				#print ('lxi0:',lxi0,'lyi0:',lyi0,'lxi1:',lxi1,'lyi1:',lyi1)
				#print ('lxe0:',lxe0,'lye0:',lye0,'lxe1:',lxe1,'lye1:',lye1)

				#RESPONSAVEL POR PERCORRER AS REGIÕES AO REDOR DA REGIÃO PRINCIPAL PARA FUTURAMENTE TENTAR ESTIMAR
				#ALGUMAS INFORMAÇÕES A MAIS A PARTIR DA RELAÇÃO ENTRE ELAS E A PARTE PRINCIPAL
				#AO TOD ESTÃO DEFINIDOS A REGIÃO PRINCIPAL (P), E MAIS 8 REGIÕES (Norte,Sul,Leste,Oeste,Nordeste,Noroeste,Sudeste,Sudoeste)
				
				listaP = []
				listaP = definindo_regiao(lxi0,lxi1,lyi0,lyi1,imagem_cinza)
				subImagem[lyi0:lyi1, lxi0:lxi1] = (0, 0, 0)
				#mostrar_imagem(subImagem)
			

				listaN = []
				listaN = definindo_regiao(lxi0,lxi1,lye0,lyi0,imagem_cinza)
				subImagem[lye0:lyi0, lxi0:lxi1] = (255, 0, 0)
				#mostrar_imagem(subImagem)

				listaS = []
				listaS = definindo_regiao(lxi0,lxi1,lyi1,lye1,imagem_cinza)
				subImagem[lyi1:lye1, lxi0:lxi1] = (0, 255, 0)
				#mostrar_imagem(subImagem)

				listaL = []
				listaL = definindo_regiao(lxi1,lxe1,lyi0,lyi1,imagem_cinza)
				subImagem[lyi0:lyi1, lxi1:lxe1] = (0, 0, 255)
				#mostrar_imagem(subImagem)

				listaO = []
				listaO = definindo_regiao(lxe0,lxi0,lyi0,lyi1,imagem_cinza)
				subImagem[lyi0:lyi1, lxe0:lxi0] = (255, 255, 0)
				#mostrar_imagem(subImagem)

				listaNO = []
				listaNO = definindo_regiao(lxe0,lxi0,lye0,lyi0,imagem_cinza)
				subImagem[lye0:lyi0, lxe0:lxi0] = (255, 0, 255)
				#mostrar_imagem(subImagem)

				listaNL = []
				listaNL = definindo_regiao(lxi1,lxe1,lye0,lyi0,imagem_cinza)
				subImagem[lye0:lyi0, lxi1:lxe1] = (0, 255, 255)
				#mostrar_imagem(subImagem)

				listaSL = []
				listaSL = definindo_regiao(lxi1,lxe1,lyi1,lye1,imagem_cinza)
				subImagem[lyi1:lye1, lxi1:lxe1] = (255, 255, 255)
				#mostrar_imagem(subImagem)

				listaSO = []
				listaSO = definindo_regiao(lxe0,lxi0,lyi1,lye1,imagem_cinza)
				subImagem[lyi1:lye1, lxe0:lxi0] = (200, 200, 200)
				#mostrar_imagem(subImagem)

				#listaTotal = [listaP,listaNO,listaN,listaNL,listaL,listaSL,listaS,listaSO,listaO]
				#print (listaTotal)
				
				#PAREI DE VERIFICAR AQUI 19/11/2019
				print ('Definindo media das regiões')
				listaRegiao = []
				media = []

				regiao_P, media_P = estimando_regiao(listaP,"P")
				listaRegiao.append(('P',regiao_P,media_P))
				#print ('Principal:',regiao,'\n','Media de:',media)

				regiao, media = estimando_regiao(listaN,"N")
				listaRegiao.append(('N',regiao,media))
				#print ('Norte:',regiao,'\n','Media de:',media)

				regiao, media = estimando_regiao(listaS,"S")
				listaRegiao.append(('S',regiao,media))
				#print ('Sul:',regiao,'\n','Media de:',media)

				regiao, media = estimando_regiao(listaL,"L")
				listaRegiao.append(('L',regiao,media))
				#print ('Leste:',regiao,'\n','Media de:',media)

				regiao, media = estimando_regiao(listaO,"O")
				listaRegiao.append(('O',regiao,media))
				#print ('Oeste:',regiao,'\n','Media de:',media)

				regiao, media = estimando_regiao(listaNO,"NO")
				listaRegiao.append(('NO',regiao,media))

				regiao, media = estimando_regiao(listaNL,"NL")
				listaRegiao.append(('NL',regiao,media))

				regiao, media = estimando_regiao(listaSL,"SL")
				listaRegiao.append(('SL',regiao,media))

				regiao, media = estimando_regiao(listaSO,"SO")
				listaRegiao.append(('SO',regiao,media))

				#print ('Listando:' , listaRegiao)

				
				#print('-----------------------------------------------------------------------------------------------------------------------')
				#print ('Relacionando valores de regiões')

				valor = relacionando_regiao(listaRegiao)
				#print ("Valor: ",valor)
				#if (valor > 1):
				#	print ('Existem regiões com valores aproximados')
				#else:
			#		print ('Possivel buraco')

				print('-----------------------------------------------------------------------------------------------------------------------')

				#print (listaRegiao)

				area_Final = area_interesse(area_SubImagem,area_SubSubImagem)
				tamanho = relacionando_tamanho(largura(novos_contornos),comprimento(novos_contornos)) #height,width
				#print ("TAMANHO: ",tamanho)
				#---------------------------------------------------------------------------------------------------------------------
				#area_final = (area(novos_contornos)/area_SubImagem)
				#print(area_valor)
				#cv.drawContours(subImagem,[novos_contornos],0,(0,0,255),3)
				#mostrar_imagem(subImagem)
#Num_i_j | Area_imagem | Area_SubImagem | Area_SubContorno | Comprimento | Largura | Altura | Circularidade | Região | Estimativa_Regioes_Arredores (TODAS)| 

				area_Imagem = 512*256
				#area_SubImagem =  Já tem
				#area_SubSubImagem = Já tem

				comp_Imagem = 512
				#width_SubImagem = já tem
				#comp_SubSubImagem = já tem 

				#larg_Imagem = 512	
				#larg_SubImagem = 
				#larg_SubSubImagem =  

				#VERIFICAR
				height_Imagem = 256
				#height_SubImagem = já tem 
				#height_SubSubImagem = height

				#circ_SubSubImagem = já tem 

				#area_SubOriginal = (area_Subimagem/area_Imagem)
				#area_SubSub = (area_SubSub/area_Imagem)
				#area_SubSubOriginal = (area_SubSubImagem/area_Imagem )
				
				#regiao_P,media_P
				'''
				train_list = []
				train_list.append((num,i,j))
				train_list.append(area_Imagem)
				train_list.append(area_SubImagem)
				train_list.append(area_SubSubImagem)

				train_list.append(comp_Imagem)
				train_list.append(comp_SubImagem)
				train_list.append(comp_SubSubImagem)

				train_list.append(alt_Imagem)
				train_list.append(alt_SubImagem)
				train_list.append(alt_SubSubImagem)

				train_list.append(circ_SubSubImagem)

				train_list.append((regiao_P,media_P))
				'''
				#train_list.append(LISTA COM OS OUTROS VALORES DA LISTA A QUAL A REGIÃO PRINCIPAL PERTENCE)

				if(area_Final >= 0.003 and valor <= 1 and tamanho >= 0.2):
					#print ('Imagem atual:')
					
					friends = [{"NUM_I":i,"NUM_J":j,"AREA_IMAGEM":area_Imagem,"AREA_SUB_IMAGEM":area_SubImagem,"AREA_SUB_CONTORNO":i,"COMPRIMENTO":i,"LARGURA":i+0.0,"ALTURA":i+0.0,"CIRCULARIDADE":i+0.0,"REGIAO":"R"}]

					df = pd.DataFrame(friends)
					df = df[["NUM_I","NUM_J","AREA_IMAGEM","AREA_SUB_IMAGEM","AREA_SUB_CONTORNO","COMPRIMENTO","LARGURA","ALTURA","CIRCULARIDADE","REGIAO"]]
					df.to_csv('ic.csv',header=False, mode='a',index=False)
					
					#print ('Comprimento:',comprimento(teste))
					#print ('Altura:',altura(teste))
					#print ('Area:',area_final)
					#print ('largura:',largura(teste))
					#print ('Circularidade:',circularidade(teste))

					imagem_aux = desenhando(subImagem,novos_contornos)
					#mostrar_imagem(imagem_aux)
					tag = str(i) + "." + str(j)	
					salvar(imagem_aux,num,tag,'4_Contornos/')
					listandoContornos.append((novos_contornos,i))
				
		

		leitura = 0
		listXY = []
		listaFinal = []
		
		limite = len(listandoContornos)
		#print ("LIMITE: ", limite)
		arq = open(destino + '0_Listas_Posicoes/' + 'lista' + '3' + '.txt', 'r')

		texto = arq.read()

		if(texto != 'NaN'):
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
			salvar(imagem_aux,lista[0][1],0,'5_Finalizadas/')
			print ('Finalizado nº: ',num)
		#else:
			#salvar(imagem_aux,i,len(listandoContornos),'5_Finalizadas/')

		leitura = ""
		arq.close()
