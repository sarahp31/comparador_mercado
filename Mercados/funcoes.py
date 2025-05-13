import requests
import json
import re
import urllib.parse
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import streamlit as st

def extrair_imagem(suggestion_view):
    """Extrai a URL da imagem do campo suggestion_view."""
    if not suggestion_view:
        return None

    # Expressão regular para capturar links de imagem que terminam em .jpg ou .png
    match = re.search(r'https:\/\/mfresh\.s3\.amazonaws\.com\/[^\s"]+\.(?:jpg|png)', suggestion_view)

    return match.group(0) if match else None

# ============================================================== #
# Função para encontrar o produto mais semelhante
# ============================================================== #

def encontrar_melhor_match(produto_pesquisado, produtos, chave_nome):
    if not produtos:
        return None  # Retorna None se não houver produtos

    # Definir palavras irrelevantes (não devem influenciar a correspondência)
    palavras_irrelevantes = {"de", "com", "c", "e", "o", "a", "do", "da", "zero", "light"}

    # Criar lista de palavras importantes na busca (removendo palavras irrelevantes)
    palavras_busca = set(produto_pesquisado.lower().split()) - palavras_irrelevantes

    melhor_produto = None
    maior_score = 0

    def similaridade(a, b):
        return SequenceMatcher(None, a, b).ratio()

    for produto in produtos:
        nome_produto = produto[chave_nome].lower()
        palavras_produto = set(nome_produto.split()) - palavras_irrelevantes

        # Similaridade entre strings (peso 40%)
        score_similaridade = similaridade(produto_pesquisado.lower(), nome_produto)

        # Cobertura de palavras (peso 40%) - Favorece produtos que contêm mais palavras da busca
        cobertura_palavras = len(palavras_busca.intersection(palavras_produto)) / len(palavras_busca)

        # Priorização de marca e sabor (peso 20%) - Favorece marcas e sabores específicos
        bonus_marca_sabor = 0
        for palavra in palavras_busca:
            if palavra in palavras_produto:
                bonus_marca_sabor += 0.1  # Aumenta a pontuação se a palavra for relevante

        # Score final = 40% similaridade + 40% cobertura + 20% bônus de marca/sabor
        score_final = (0.4 * score_similaridade) + (0.4 * cobertura_palavras) + (0.2 * bonus_marca_sabor)

        if score_final > maior_score:
            maior_score = score_final
            melhor_produto = produto

    return melhor_produto

# ============================================================== #
# Funções para buscar os produtos em cada mercado
# ============================================================== #

def buscar_pao_de_acucar(produto):
    url = 'https://api.vendas.gpa.digital/pa/search/search'
    payload = {
        "terms": produto,
        "page": 1,
        "sortBy": "relevance",
        "resultsPerPage": 21,
        "allowRedirect": True,
        "storeId": 461,
        "department": "ecom",
        "customerPlus": True,
        "partner": "linx"
    }
    response = requests.post(url, json=payload)
    response.encoding = 'utf-8'

    if response.status_code == 200:
        data = response.json()
        if "products" in data and data["products"]:
            produtos = data["products"]
            item = encontrar_melhor_match(produto, produtos, "name")

            if item:
                # Definir os campos que queremos manter
                campos_desejados = ["name", "brand", "price", "productImages", "urlDetails"]

                # Criar o dicionário do melhor match
                melhor_match = {
                    "mercado": "Pão de Açúcar",
                    "nome": item["name"],
                    "marca": item.get("brand", "Não disponível"),
                    "preco": item["price"],
                    "imagem": f"https://www.paodeacucar.com{item['productImages'][0]}" if item.get("productImages") else "N/A",
                    "link": item["urlDetails"]
                }

                # Criar a lista de outros produtos sem o melhor match e com os mesmos campos
                outros_produtos = [
                    {
                        "nome": p["name"],
                        "marca": p.get("brand", "Não disponível"),
                        "preco": p["price"],
                        "imagem": f"https://www.paodeacucar.com{p['productImages'][0]}" if p.get("productImages") else "N/A",
                        "link": p["urlDetails"]
                    }
                    for p in produtos if p != item
                ]

                return melhor_match, outros_produtos
    return None

def buscar_extra(produto):
    url = "https://api.vendas.gpa.digital/ex/search/search"
    payload = {
        "terms": produto,
        "page": 1,
        "sortBy": "relevance",
        "resultsPerPage": 21,
        "allowRedirect": True,
        "storeId": 483,
        "department": "ecom",
        "customerPlus": True,
        "partner": "linx"
    }
    response = requests.post(url, json=payload)
    response.encoding = 'utf-8'

    if response.status_code == 200:
        data = response.json()
        if "products" in data and data["products"]:
            produtos = data["products"]
            item = encontrar_melhor_match(produto, produtos, "name")

            if item:
                # Criar o dicionário do melhor match
                melhor_match = {
                    "mercado": "Extra",
                    "nome": item["name"],
                    "marca": item.get("brand", "Não disponível"),
                    "preco": item["price"],
                    "imagem": f"https://www.clubeextra.com.br{item['productImages'][0]}" if item.get("productImages") else "N/A",
                    "link": item["urlDetails"]
                }

                # Criar a lista de outros produtos sem o melhor match e com os mesmos campos
                outros_produtos = [
                    {
                        "nome": p["name"],
                        "marca": p.get("brand", "Não disponível"),
                        "preco": p["price"],
                        "imagem": f"https://www.clubeextra.com.br{p['productImages'][0]}" if p.get("productImages") else "N/A",
                        "link": p["urlDetails"]
                    }
                    for p in produtos if p != item
                ]

                return melhor_match, outros_produtos
    return None

def buscar_sonda(produto):
    produto_formatado = urllib.parse.quote(produto)
    url = f"https://www.sondadelivery.com.br/delivery/busca/{produto_formatado}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    produtos = []
    for product in soup.find_all("div", class_="product"):
        try:
            nome = product.find("h3", class_="product--title").text.strip()
            preco_element = product.find("span", id=lambda x: x and "lblValorPor" in x)
            preco = float(preco_element.text.strip().replace(",", ".").strip()) if preco_element else float("nan")
            imagem = product.find("img", class_="lazy")["data-srcset"]
            link = "https://www.sondadelivery.com.br" + product.find("a", class_="js-link-produto")["href"]
            produtos.append({
                "nome": nome,
                "preco": preco,
                "imagem": imagem,
                "link": link
            })
        except AttributeError:
            continue  # Ignora produtos com informações incompletas

    item = encontrar_melhor_match(produto, produtos, "nome")
    outros_produtos = [p for p in produtos if p != item]
    if item:
        return {
            "mercado": "Sonda",
            "nome": item["nome"],
            "marca": None,
            "preco": item["preco"],
            "imagem": item["imagem"],
            "link": item["link"]
        }, outros_produtos
    return None

def buscar_carrefour(produto):
    url = "https://mercado.carrefour.com.br/api/graphql"

    variables = {
        "isPharmacy": False,
        "first": 20,
        "after": "0",
        "sort": "score_desc",
        "term": produto,
        "selectedFacets": [
            {"key": "channel", "value": json.dumps({"salesChannel": 2, "regionId": "v2.7BA3167303A7C6998E4A6BF241DCB3C1"})},
            {"key": "locale", "value": "pt-BR"},
            {"key": "region-id", "value": "v2.7BA3167303A7C6998E4A6BF241DCB3C1"}
        ]
    }

    params = {
        "operationName": "ProductsQuery",
        "variables": json.dumps(variables)
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": f"https://mercado.carrefour.com.br/s?q={urllib.parse.quote(produto)}&sort=score_desc&page=0",
        "Accept-Encoding": "gzip, deflate, br"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        try:
            items = data['data']['search']['products']['edges']
            produtos = [
                {
                    "mercado": "Carrefour",
                    "nome": item['node'].get("name", "Nome não encontrado"),
                    "marca": item['node'].get("brand", {}).get("name", "Marca desconhecida"),
                    "preco": item['node'].get("offers", {}).get("lowPrice", "Preço indisponível"),
                    "imagem": item['node'].get("image", [{}])[0].get("url", None),
                    "link": f"https://mercado.carrefour.com.br/{item['node'].get('slug', '')}/p"
                }
                for item in items
            ]
            item = encontrar_melhor_match(produto, produtos, "nome")
            outros_produtos = [p for p in produtos if p != item]
            if item:
                return {
                    "mercado": "Carrefour",
                    "nome": item["nome"],
                    "marca": item["marca"],
                    "preco": item["preco"],
                    "imagem": item["imagem"],
                    "link": item["link"]
                }, outros_produtos
        except KeyError:
            return None
    return None

def buscar_st_marche(produto):
    produto_formatado = urllib.parse.quote(produto)
    url = f"https://www.marche.com.br/produtos/autocomplete?query={produto_formatado}"
    response = requests.get(url)
    response.encoding = 'utf-8'

    if response.status_code == 200:
        data = json.loads(response.text)
        produtos = [
            {
                "mercado": "St Marche",
                "nome": p["slug"].replace("-", " ").title(),
                "preco": float(p.get("price", "Preço não encontrado")),
                "imagem": extrair_imagem(p.get("suggestion_view", None)),  # Extraindo imagem corretamente
                "link": f"https://www.marche.com.br/produtos/{p.get('slug', '')}"
            }
            for p in data
        ]
        item = encontrar_melhor_match(produto, produtos, "nome")
        outros_produtos = [p for p in produtos if p != item]
        if item:
            return {
                "mercado": "St Marche",
                "nome": item["nome"],
                "marca": None,
                "preco": item["preco"],
                "imagem": item["imagem"],
                "link": item["link"]
            }, outros_produtos
    return None
