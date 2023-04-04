##imports de bibliotecas
import os
import gspread
import requests
import pandas as pd
import numpy as np
import datetime 
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials
from tchan import ChannelScraper
from bs4 import BeautifulSoup
from pandas import DataFrame
from datetime import date


## preparando a integração com o telegram
TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
TELEGRAM_ADMIN_ID = os.environ["TELEGRAM_ADMIN_ID"]

##preparando a integração com o google sheets
GOOGLE_SHEETS_CREDENTIALS = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
with open("credenciais.json", mode = "w") as fobj:
  fobj.write(GOOGLE_SHEETS_CREDENTIALS)
conta = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")
api = gspread.authorize(conta)
planilha = api.open_by_key("1ZDyxhXlCtCjMbyKvYmMt_8jAKN5JSoZ7x3MqlnoyzAM")
sheet = planilha.worksheet("Sheet1")

##configurando o flask e preparando o site
app = Flask(__name__)

menu = """
<center><a href="/">Página inicial</a> |  <a href="/concursos">Concursos Abertos</a> | <a href="/sobre">Sobre</a> | <a href="/contato">Contato</a></center>
"""

@app.route("/")
def index():
  return menu

@app.route("/sobre")
def sobre():
  return menu + "Site desenvolvido para a disciplina de Algoritmos de Automação do Master de Jornalismo de Dados, Automação e Data storytelling do Insper. "

@app.route("/contato")
def contato():
  return menu + "Para me contatar, pode acessar meu github: https://github.com/thamatos ou chamar no e-mail: thais.matos.pinheiro@alumni.usp.br"

## importar as funções de raspar os concursos e automatizar texto
from funcoes_concursos import raspa_concursos
from funcoes_concursos import automatiza_texto
texto = automatiza_texto()
mensagem_bot = f'Obrigada por acessar o bot dos concursos. {texto}'

##Cria página com o resultado da raspagem dos concursos

@app.route("/concuros")
def concursos():
  raspagem = raspa_concursos()
  texto = automatiza_texto()
  return(texto)

## Cria a resposta do Telegram

@app.route("/telegram-bot", methods=["POST"])
def telegram_bot():
  update = request.json
  chat_id = update["message"]["chat"]["id"]
  message = update["message"]["text"]
  lista_entrada = ["/start", "oi", "ola", "olá", "bom dia", "boa tarde", "boa noite"]
  lista_saida = ["obrigado", "obrigada", "valeu", "muito obrigado", "muito obrigada"]
  nova_mensagem = ' '
  if message.lower().strip() in lista_entrada:
    nova_mensagem = {"chat_id" : chat_id, "text" : "Oi, seja muito bem-vindo(a) ao Bot do Concurso Público do site PCI Concursos! \n Se você quiser saber quantos concursos e quantas vagas estão abertos hoje, digite 1"}
  elif message == "1":
     nova_mensagem = {"chat_id" : chat_id, "text" : f'{mensagem_bot}'}
  elif message.lower().strip() in lista_saida:
     nova_mensagem = {"chat_id" : chat_id, "text" : "Que isso! Até a próxima :)"}
  else:
    nova_mensagem = {"chat_id" : chat_id, "text" : "Não entendi. Escreva 'oi' ou 'olá' para ver as instruções."}
  resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
  print(resposta.text)
  return "ok"
 
