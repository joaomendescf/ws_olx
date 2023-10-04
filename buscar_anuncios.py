import requests
from random import randint
from bs4 import BeautifulSoup
from lxml import etree
import json
from time import sleep
import os
import pandas as pd
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys

SCRAPEOPS_API_KEY = '7a1f21b1-37ee-408d-8faf-e32dba21af3c'
    
def get_headers_list():
  response = requests.get('http://headers.scrapeops.io/v1/browser-headers?api_key=' + SCRAPEOPS_API_KEY)
  json_response = response.json()
  return json_response.get('result', [])

def get_random_header(header_list):
  random_index = randint(0, len(header_list) - 1)
  return header_list[random_index]

def abrirNavegador():
    options = Options()
    header_list = get_headers_list()
    headers=get_random_header(header_list)
    options.add_argument('--headless=new')
    options.add_argument('disable-infobars')
    options.add_argument('--disable-notifications')
    options.add_argument("--disable-extensions")
    options.add_argument(f"--header={headers}")
    
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches",["enable-automation"])
    
    dir_path = os.getcwd()
    options.add_argument(f'user-data-dir={dir_path}\\automacaoFlet_profile\\automacoes')
   
    navegador = webdriver.Chrome(options=options)
    
    # posicao_x = 1000
    # posicao_y = 1000
    # navegador.set_window_position(posicao_x, posicao_y)
    
    # navegador.minimize_window()    
    # navegador.maximize_window()    
    return navegador

print('#. abrindo navegador')
navegador = abrirNavegador()

local = 'ce'
consulta = 'celular usado'
consulta = consulta.replace(' ', '%20')  
pagina = 100
# pagina_final = 10
lst_final = []
sequencia_geral = 1

# while pagina <= pagina_final:
while len(navegador.find_elements(By.CSS_SELECTOR, 'a[class="olx-button olx-button--link-button olx-button--small olx-button--a olx-button--disabled"]')) < 1:  
      
        url = f'https://www.olx.com.br/estado-{local}?q={consulta}&o={pagina}' 

        # print(f'1. carregando pagina {pagina} de {pagina_final}')
        print(f'1. carregando a pagina {pagina}')
        navegador.get(url)
        sleep(5)

        print('2. Coletando os dados da pagina')
        page_source = navegador.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        dom = etree.HTML(str(soup)) 

        print(f'3. Percorrendo a pagina')
        valores = dom.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
        dict_dados = json.loads(valores)

        print('4. Convertendo em dicionario')
        dados = dict_dados['props']['pageProps']['ads']

        print(f'5. Quantidade de dados coletados: {len(dados)} ')
        
        sequencia_pag = 1

        for dict_dados in dados:
            try:        
                titulo = dict_dados['title']
                preco = dict_dados['price']
                
                data = dict_dados['date']                
                data = datetime.utcfromtimestamp(data)
                data_formatada = data.strftime("%d-%m-%Y_%H-%M")
                
                url = dict_dados['url']        
                dados_local = dict_dados['locationDetails']
                cidade = dados_local['municipality']
                bairro = dados_local['neighbourhood']
                estado = dados_local['uf']
                ddd = dados_local['ddd']
                lst_final.append({'pag':pagina, 'item_pag': sequencia_pag, 'item_geral': sequencia_geral, 'titulo': titulo, 'preco': preco, 'data':data_formatada, 'cidade': cidade, 'bairro':bairro , 'estado':estado , 'ddd':ddd , 'url':url }) 
                
                sequencia_pag += 1
                sequencia_geral += 1
            except:
                pass

        print('6. salvando dados em .xlsx')
        arquivo_excel = f'dados_anuncios.xlsx' 
        
        #excluir itens duplicados da lista   
        tuplas_de_itens = [tuple(d.items()) for d in lst_final]        
        conjunto_de_tuplas = set(tuplas_de_itens)    
        lista_itens_unicos = [dict(t) for t in conjunto_de_tuplas]
        
        df = pd.DataFrame(lista_itens_unicos)    
        df.to_excel(arquivo_excel, index=False)

        print(f'7. Dados acumulados: {len(lst_final)}')
        print(f'8. Página {pagina} finalizada com sucesso!\n')
        pagina += 1
        
        if len(navegador.find_elements(By.CSS_SELECTOR, 'a[class="olx-button olx-button--link-button olx-button--small olx-button--a olx-button--disabled"]')) > 0:
            break

navegador.quit()

local_atual = os.getcwd()
data_hora_atual = datetime.now()
agora = data_hora_atual.strftime("%d-%m-%Y_%H-%M")
nome_arquivo = f'{local_atual}\\dados_gerais_{agora}.xlsx'

tuplas_de_itens = [tuple(d.items()) for d in lst_final]        
conjunto_de_tuplas = set(tuplas_de_itens)    
lista_itens_unicos = [dict(t) for t in conjunto_de_tuplas]

df = pd.DataFrame(lista_itens_unicos)    
df.to_excel(nome_arquivo, index=False)
print(f'Solicitação realizada com sucesso\nLocal do Arquivo: {nome_arquivo}')
  