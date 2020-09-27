from matplotlib import pyplot as plt
import json
import cv2


def mostrar_imagem(imagem):
    cv2.imshow('Imagem',imagem)
    cv2.waitKey()
    cv2.destroyAllWindows()
    return 0

def mostrar_imagens(imagem1,imagem2,imagem3,imagem4):
	plt.subplot(221), plt.imshow(imagem1, 'gray')
	plt.subplot(222), plt.imshow(imagem2,'gray')
	plt.subplot(223), plt.imshow(imagem3, 'gray')
	plt.subplot(224), plt.imshow(imagem4,'gray')
	plt.show()

	return 0


if __name__ == "__main__":

    
    path_origem = "C:\\Users\\mikae\\"
    path_imagem = "C:\\Nova pasta\\2_Areas de Atuacao\\Processamento de Imagens\\Imagens\\Imagens_F\\2_Tratadas\\"
    
    lista = []
#   with open(path_origem + 'CLASSE_m1.json') as f:
#        lista.append(json.load(f))
        
    for i in range(0,3):
        with open(path_origem + 'CLASSE_' + str(i) + '.json') as f:
            lista.append(json.load(f))


    for num in range(0,3):
       
        tam = len(lista[i]['NUM_ORIGIN'].values())
        num_origin = list(lista[i]['NUM_ORIGIN'].values())
        num_sub = list(lista[i]['NUM_SUB'].values())
        
        print('VALOR DA CLASSE | ',num - 1)
        for im in range(1,tam):
            leitura = path_imagem + str(num_origin[im]) + '_' + str(num_sub[im]) + '.png' 
            imagem = cv2.imread(leitura)
            mostrar_imagem(imagem)
            #mostrar_imagens(imagem,imagem,imagem,imagem)

    #mostrar_imagens(imagem,imagem,imagem,imagem)
    #print('Funcionou ______ NUM_ORIGIN |')
    #print(data['NUM_ORIGIN'])
    #print('Funcionou ______ NUM_SUB |')
    #print(data['NUM_SUB'])

'''
import urllib.request
import numpy as np
import cv2

urls = ['https://geo0.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=pt-BR&gl=br&output=thumbnail&thumb=2&w=512&h=512&pitch=13.196594786332426&ll=-8.419068946001369%2C-37.05888456603527&panoid=_v-_sFk7QgvNjDTPrYshHg&yaw=99.09436149014695',
        'https://geo0.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=pt-BR&gl=br&output=thumbnail&thumb=2&w=512&h=512&pitch=23.381998904268926&ll=-8.418919855931424%2C-37.0607654302107&panoid=yNHT2lMOOZJCjpbzBOV1yQ&yaw=266.32852382890627',
        'https://geo0.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=pt-BR&gl=br&output=thumbnail&thumb=2&w=512&h=512&pitch=24.75339642961535&ll=-8.418618599459512%2C-37.06232059087411&panoid=ccBhbnU8Kki3tTwnAUgJFg&yaw=288.48365384797177']

def url_to_image(url):
	resp = urllib.request.urlopen(url)
	image = np.asarray(bytearray(resp.read()), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)
	return image

for url in urls:
    print("downloading %s" % (url))
    image = url_to_image(url)
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
'''

