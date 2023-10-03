from time import sleep
from random import randint
import pandas as pd
import os
import datetime
from lxml import etree

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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
    # options.add_argument('--headless=new')
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
    navegador.maximize_window()    
    return navegador

  
def coletar_links(navegadorChrome, rolagem_total, pagina=0):
        
    rolagem = 0  
    lst_dados = []
      
    while rolagem <= rolagem_total:
        try:   
            navegadorChrome.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            sleep(2)
                                     
            if rolagem%2==0:
                page_source = navegadorChrome.page_source
                soup = BeautifulSoup(page_source, "html.parser")
               
                elementos = soup.find_all('section', class_='olx-ad-card olx-ad-card--horizontal sc-3888b54f-1 cRGtPk')

                for e in elementos:           
                    link = e.find('a', class_='olx-ad-card__link-wrapper', href=True)['href']       
                    descricao = e.find('h2', class_='olx-text olx-text--title-small olx-text--block olx-ad-card__title olx-ad-card__title--horizontal').text   
                    preco = e.find('h3', class_='olx-text olx-text--body-large olx-text--block olx-text--semibold olx-ad-card__price').text   
                    local = e.find('p', class_='olx-text olx-text--caption olx-text--block olx-text--regular').text   
                    data = e.find('p', class_='olx-text olx-text--caption olx-text--block olx-text--regular olx-ad-card__date--horizontal').text 
                    
                    lst_dados.append({'pag':pagina, 'descricao':descricao, 'preco':preco, 'local':local, 'data':data, 'link':link})
                        
                    sleep(1)    
                        
        except:
            pass        
        rolagem += 1
        
    return lst_dados
       
def excluir_elementos_duplicados_lista(lst_dados):
    # if tipo == 'dados_gerais':
    #     tuplas_de_itens = [tuple(d.items()) for d in lst_dados]
    # if tipo == 'dados_vendedor':
    tuplas_de_itens = [tuple(d.items()) for d in lst_dados]
        
    conjunto_de_tuplas = set(tuplas_de_itens)
    lista_de_dicionarios_sem_duplicatas = [dict(t) for t in conjunto_de_tuplas]
      
    return lista_de_dicionarios_sem_duplicatas
 
def coletar_dados_vendedor(navegadorChrome, lst_dados):
    lst_dados_vendedor = []
    
    for dict_dados in lst_dados:
        print('\nlink: '+dict_dados['link'])
        navegadorChrome.get(dict_dados['link'])
        
        cont = 1
        while len(navegadorChrome.find_elements(By.CSS_SELECTOR, 'button[class="sc-gqjmRU bfPGKd"]')) < 1:           
            print(f'wait {cont}', end=' - ')
            
            if cont == 10:
                break
            
            sleep(1)
            cont += 1
        
        try:
            
            bt_ver_numero = navegadorChrome.find_element(By.XPATH, '//*[@id="miniprofile"]/div/div/div/div[5]/div/button')
            bt_ver_numero.click()
            print('clicou no botao')
        except:
            # bt_ver_numero = navegadorChrome.find_element(By.CSS_SELECTOR, 'button[class="sc-gqjmRU bfPGKd"]')
            # bt_ver_numero.click()
            print('sem numero')
                    
        sleep(3)
        
        #adrianodasilvagomes387@gmail.com
        #@JF159730ana
        #abrir profile direto pelo windows
        #"D:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir=D:\Users\joaom\Desktop\CURSOS\sistemaweb\automacaoFletprofile\automacoes
        
        page_source = navegadorChrome.page_source
        soup = BeautifulSoup(page_source, "html.parser")
                
        # anuncio =  soup.find('h1', class_='ad__sc-45jt43-0 htAiPK sc-jTzLTM iXcEhO').text
        # preco =  soup.find('span', class_='ad__sc-1wimjbb-1 hoHpcC sc-jTzLTM kNahTW').text
        # data = 'NI'
        
        # try:
        #     dt =  soup.find_all('span', class_='ad__sc-1oq8jzc-0 dWayMW sc-jTzLTM iGzcjb')
        #     data = dt[1].text
        # except:
        #     pass
        
        # dados_localizacao = 'NI'
        cep =  'NI'
        # municipio =  'NI'
        bairro = 'NI'
        # logradouro = 'NI'
        
        try:
            dados_localizacao = soup.find_all('span', class_='ad__sc-1f2ug0x-1 cpGpXB sc-jTzLTM ieZUgc')
        except:
            pass
        
        try:  
            cep =  dados_localizacao[0].text
        except:
            cep =  'NI'
        # try:
        #     municipio =  dados_localizacao[1].text
        # except:
        #     municipio = 'NI'
        try:
            bairro =  dados_localizacao[2].text
        except:
            bairro =  'NI'            
        # try:
        #     logradouro =  dados_localizacao[3].text
        # except:
        #     logradouro =  'NI' 
        
        # try:
        #     try:
        #         # nome_vendedor = soup.find('span', class_='sc-hizQCF sc-ewMkZo bnupHe sc-kFLxrv kMPwxI sc-fjhmcy jbKYVi').text
        #         root = html.fromstring(str(soup))
        #         nome_vendedor = root.xpath('//*[@id="miniprofile"]/div/div/div/div[2]/div/span').text
        #     except:
        #         nome_vendedor = soup.find('span', class_='sc-hizQCF sc-dAWfgX bnNYNJ sc-kFLxrv dKpwOL sc-fjhmcy fuoLiy').text
        #         nome_vendedor = soup.find('span', class_='sc-hizQCF sc-dAWfgX bnNYNJ sc-kFLxrv dKpwOL sc-fjhmcy fuoLiy').text
        # except:
        #     nome_vendedor = 'NI'
        dom = etree.HTML(str(soup))                   
        
        
        try:    
            # telefone_vendedor = soup.find('span', class_='sc-kUQWMX jkdHlS sc-jTzLTM cLtOVy').text
           
            telefone_vendedor = dom.xpath('//*[@id="miniprofile"]/div/div/div/div[5]/div/button/div/span[1]')[0].text
        except:
            telefone_vendedor = 'NI'
            
        try: 
            nome_vendedor = dom.xpath('//*[@id="miniprofile"]/div/div/div/div[2]/div/span')[0].text
        except:
            nome_vendedor = 'NI'
        
        lst_dados_vendedor.append({
                'pag':dict_dados['pag'], 
                'vendedor':nome_vendedor, 
                'telefone':telefone_vendedor, 
                'anuncio':dict_dados['descricao'], 
                'preco':dict_dados['preco'], 
                'data_pub':dict_dados['data'], 
                'municipio':dict_dados['local'], 
                'bairro':bairro, 
                'cep':cep, 
                # 'logradouro':logradouro, 
                'link':dict_dados['link'] 
            })
        
        print(f'Vendedodor: {nome_vendedor} | {telefone_vendedor}')
        # dict= {
        #         'vendedor':nome_vendedor, 
        #         'telefone':telefone_vendedor, 
        #         'anuncio':dict_dados['descricao'], 
        #         'preco':dict_dados['preco'], 
        #         'data_pub':dict_dados['data'], 
        #         'municipio':dict_dados['local'], 
        #         'bairro':bairro, 
        #         'cep':cep, 
        #         # 'logradouro':logradouro, 
        #         'link':dict_dados['link'] 
        #     }
        
        # print(dict)
        
    return lst_dados_vendedor   
 

def salvar_dados_txt():
    arquivo = 'dados_olx_novo.txt'
    
    arquivo_existe = False
    try:
        with open(arquivo, 'r'):
            arquivo_existe = True
    except FileNotFoundError:
        arquivo_existe = False
    
    modo_abertura = 'a' if arquivo_existe else 'w'
        
    cont = 1
    
    with open(arquivo, modo_abertura) as arquivo:  
        for dict_dado in lst_dados:
            arquivo.write(f'[Item {cont}]============================' + "\n")
            
            for c,v in dict_dado.items():               
                arquivo.write(f'{c} : {v}' + "\n")
                
            arquivo.write("\n")
        
            cont+=1

def salvar_dados_xls(tipo, dict_dados):
    
    data_hora_atual = datetime.datetime.now()
    agora = data_hora_atual.strftime("%d-%m-%Y_%H-%M")
    
    if tipo == 'dados_gerais':
        # lista_sem_duplicacao = excluir_elementos_duplicados_lista('dados_gerais')
        arquivo_excel = f'dados_gerais_{agora}.xlsx'
    elif tipo == 'dados_vendedor':        
        # lista_sem_duplicacao = excluir_elementos_duplicados_lista('dados_vendedor')
        arquivo_excel = f'dados_vendedor_{agora}.xlsx'
    
    df = pd.DataFrame(dict_dados)    
    df.to_excel(arquivo_excel, index=False)
   
       

def main():
    
    consulta = 'celular usado'
    consulta = consulta.replace(' ', '%20')      
    
    local = 'ce'
    
    # tipo = 'todos_os_links'
    # tipo = 'quantidade_especifica_registros'
    tipo = 'quantidade_paginas'
    rolagem = 20 #numero par
   
    navegador = abrirNavegador()  
    
    if tipo == 'quantidade_paginas':
        pagina = 1
        pagina_final = 1
        
        while pagina <= pagina_final:   
            
            if len(local) == 6:            
                url = f'https://www.olx.com.br/{local}?q={consulta}&o={pagina}'
            elif len(local) == 2:
                url = f'https://www.olx.com.br/estado-{local}?q={consulta}&o={pagina}' 
              
            navegador.get(url)
            
            dict_dados = coletar_links(navegador, rolagem, pagina) 
            dict_dados_unicos = excluir_elementos_duplicados_lista(dict_dados)
            dict_dados_vendedores = coletar_dados_vendedor(navegador, dict_dados_unicos)
            # print(dict_dados_vendedores)
            
            salvar_dados_xls('dados_vendedor',dict_dados_vendedores)
            
            pagina += 1  
    
    
    elif tipo == 'todos_os_links':
        while len(navegador.find_elements(By.CSS_SELECTOR, 'span[class="olx-text olx-text--title-large olx-text--block"]')) < 1:
            if len(local) == 6:            
                url = f'https://www.olx.com.br/{local}?q={consulta}&o={pagina}'
            elif len(local) == 2:
                url = f'https://www.olx.com.br/estado-{local}?q={consulta}&o={pagina}' 
              
            navegador.get(url)
          
            dict_dados = coletar_links(navegador, rolagem) 
            dict_dados_unicos = excluir_elementos_duplicados_lista(dict_dados)
               
    
    navegador.quit()    
   

def main_xls():
    df = pd.read_excel('dados_gerais.xlsx')
    # qtd_linhas = df.shape[0]
    # nome = df.loc[0, 'link']
    dict_dados_unicos = df.to_dict(orient='records')
    navegador = abrirNavegador()
    # print(dict_dados_unicos)
    
    dict_dados_vendedores = coletar_dados_vendedor(navegador, dict_dados_unicos)
       
    navegador.quit()
    salvar_dados_xls('dados_vendedor', dict_dados_vendedores)
    
    
main_xls()
