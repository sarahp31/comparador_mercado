import streamlit as st
import pandas as pd
import requests
import json
import io
import base64
import openpyxl
import re
from bs4 import BeautifulSoup
from Mercados.funcoes import buscar_pao_de_acucar, buscar_extra, buscar_sonda, buscar_carrefour, buscar_st_marche

st.set_page_config(layout="wide")

# CSS aprimorado com fundo mais suave
st.markdown("""
<style>
body {
    background-color: #f9fcfb;
    font-family: 'Segoe UI', sans-serif;
    color: #333;
}

.stApp {
    background-color: #f9fcfb;
}

.produto-card {
    background: #ffffff;
    border: 1px solid #e1e8e3;
    border-radius: 16px;
    padding: 20px;
    margin: 10px auto;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.06);
    max-width: 600px;
}

.produto-card img {
    max-width: 150px;
    max-height: 150px;
    object-fit: contain;
    border-radius: 12px;
    margin-bottom: 15px;
}

.produto-preco {
    color: #27ae60;
    font-weight: bold;
    font-size: 1.4rem;
    margin: 8px 0;
}

.produto-link a {
    color: #ffffff;
    background-color: #3498db;
    padding: 10px 16px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
    transition: background-color 0.3s ease;
    display: inline-block;
}

.produto-link a:hover {
    background-color: #2c80b4;
}
</style>
""", unsafe_allow_html=True)

# TABS
aba1, aba2 = st.tabs(["Produto Único", "Upload de Arquivo"])

with aba1:
    st.markdown("""
    <h1 style='text-align: center;'>🛒 Comparador de Preços de Supermercados</h1>
    <p style='text-align: center;'>Digite um produto e veja os preços nos mercados.</p>
    """, unsafe_allow_html=True)

    produto = st.text_input("Digite o nome do produto:", "").strip()
    if st.button("Buscar") and produto:
        with st.spinner("Buscando..."):
            mercados = {
                "Pão de Açúcar": buscar_pao_de_acucar,
                "Extra": buscar_extra,
                "Sonda": buscar_sonda,
                "Carrefour": buscar_carrefour,
                "St Marche": buscar_st_marche
            }

            resultados = []
            for nome_mercado, funcao in mercados.items():
                try:
                    resultado = funcao(produto)
                    if resultado:
                        produto_principal, _ = resultado
                        resultados.append(produto_principal)
                    else:
                        st.warning(f"❌ Nenhum resultado encontrado para {nome_mercado}.")
                except Exception as e:
                    st.error(f"⚠️ Erro ao buscar no {nome_mercado}: {str(e)}")

        for r in resultados:
            with st.container():
                st.markdown('<div class="produto-card">', unsafe_allow_html=True)
                if r.get("imagem") and r.get("imagem") != "N/A":
                    st.markdown(f"<img src='{r.get('imagem')}' alt='Imagem do produto'>", unsafe_allow_html=True)
                st.markdown(f"<h3>{r.get('mercado', 'Mercado')}</h3>", unsafe_allow_html=True)
                st.markdown(f"<p><strong>Nome:</strong> {r.get('nome')}</p>", unsafe_allow_html=True)
                st.markdown(f"<p><strong>Marca:</strong> {r.get('marca')}</p>", unsafe_allow_html=True)
                preco = r.get("preco")
                if isinstance(preco, (int, float)):
                    st.markdown(f"<div class='produto-preco'>R$ {preco:.2f}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='produto-preco'>Preço não disponível</div>", unsafe_allow_html=True)
                if r.get("link"):
                    st.markdown(f"<div class='produto-link'><a href='{r['link']}' target='_blank'>🔗 Comprar agora</a></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

with aba2:
    st.subheader("📂 Upload de Arquivo ainda não implementado nesta versão.")
