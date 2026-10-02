import requests 
from pprint import pprint
menu_moedas = """

=== Opções de Moedas para Consulta ===

Tradicionais:

USD-BRL (Dólar Americano)
EUR-BRL (Euro)
GBP-BRL (Libra Esterlina)
ARS-BRL (Peso Argentino)

Criptomoedas:

BTC-BRL (Bitcoin)
ETH-BRL (Ethereum)

=====================================

"""
print(menu_moedas)

def consultar_moeda(moeda):
    url = f"https://economia.awesomeapi.com.br/json/last/{moeda}"

    resposta = requests.get(url)
    dados = resposta.json()
    if resposta.status_code == 200:
        print("Deu certo!")
        pprint(resposta.json())
        return resposta.json()
    
    elif resposta.status_code == 404:
        erro = dados["status"]
        mensagem = dados["message"]
        print(f"O erro foi {erro}, {mensagem}")
        return resposta.json()
    

    else:
        print("ERRO")

moeda_desejada = input("Digite a moeda que deseja consultar(ex: USD-BRL): ")

dados_api = consultar_moeda(moeda_desejada)

#----------------------Tratamento json------------------------------------------

if dados_api:
    chave = moeda_desejada.replace("-", "")
    valor = dados_api[chave]["bid"]
    print("\nRequisição bem-sucedida!")

    print(f"O valor atual de {moeda_desejada} é: ")
    print(f"R$ {float(valor):.2f}")

else:
    print(f"\nErro ao consultar a moeda: {moeda_desejada}. \nVerifique se o formato está correto.")







