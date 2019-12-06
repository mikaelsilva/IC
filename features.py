import pandas as pd 
'''
friends = [{'NUM_I_J':'null','AREA_IMAGEM':0.0,"AREA_SUB_IMAGEM":0.0,"AREA_SUB_CONTORNO":0.0,"COMPRIMENTO":0.0,"LARGURA":0.0,"ALTURA":0.0,"CIRCULARIDADE":0.0,"REGIAO":"null"}
         ]

df = pd.DataFrame(friends)
df = df[['NUM_I_J','AREA_IMAGEM','AREA_SUB_IMAGEM']]

df.to_csv('teste.csv',header=True,index=False)






for i in range(1,5):
    friends = [{'NUM_I_J':'1_'+str(i),'AREA_IMAGEM':i,"AREA_SUB_IMAGEM":i,"AREA_SUB_CONTORNO":i,"COMPRIMENTO":i,
                "LARGURA":i+0.0,"ALTURA":i+0.0,"CIRCULARIDADE":i+0.0,"REGIAO":"R"}
              ]
    df = pd.DataFrame(friends)
    df = df[['NUM_I_J','AREA_IMAGEM','AREA_SUB_IMAGEM']]
    df.to_csv('teste.csv',header=False, mode='a',index=False)




#Num_i_j "," Area_imagem "," Area_SubImagem "," Area_SubContorno "," Comprimento "," Largura "," Altura "," Circularidade "," Região "," Estimativa_Regioes_Arredores (TODAS)| 

'''
'''
EXISTENCIA DO ARQUIVO
try:
  pd.read_csv("ic.csv")
  print("EXISTE")
except:
  friends = [{'NUM_I_J':'null','AREA_IMAGEM':0.0,"AREA_SUB_IMAGEM":0.0,"AREA_SUB_CONTORNO":0.0,"COMPRIMENTO":0.0,"LARGURA":0.0,"ALTURA":0.0,"CIRCULARIDADE":0.0,"REGIAO":"null"}
            ]

  df = pd.DataFrame(friends)
  df = df[['NUM_I_J','AREA_IMAGEM','AREA_SUB_IMAGEM']]

  df.to_csv('ic.csv',header=True,index=False)
  
  print("AGORA VAI EXISIR")
  '''