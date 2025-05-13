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

st.markdown("""
<h1 style='text-align: center;'>🛒 Comparador de Preços</h1>
<p style='text-align: center; font-size: 18px;'>Compare os preços do mesmo produto em diferentes supermercados</p>
""", unsafe_allow_html=True)

st.markdown("""
<style>
body {
    background-color: #eafaf1;
    font-family: 'Inter', sans-serif;
    color: #333;
}

section.main > div {
    background-color: #eafaf1;
    padding: 20px;
    border-radius: 12px;
}

.produto-section {
    margin-bottom: 40px;
    padding: 20px;
    border-radius: 16px;
    background-color: #ffffff;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.produto-card {
    background: #fdfdfd;
    border: 1px solid #dfe6e2;
    border-radius: 16px;
    padding: 20px;
    margin: 10px;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 550px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.produto-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.1);
}

.produto-imagem {
    width: 150px;
    height: 150px;
    margin: 0 auto 15px auto;
}

.produto-imagem img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 16px;
}

.produto-info p {
    margin: 5px 0;
    font-size: 1.5rem;
    color: #444;
    line-height: 1.6;
}

.produto-preco {
    font-size: 1.4rem;
    font-weight: 600;
    color: #27ae60;
    margin-bottom: 10px;
}

.produto-link a {
    display: inline-block;
    margin-top: 5px;
    padding: 10px 18px;
    background-color: #3498db;
    color: #fff;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 500;
    transition: background-color 0.3s ease;
}

.produto-link a:hover {
    background-color: #1d78c1;
}

.melhor-preco-badge {
    background-color:#27ae60;
    color:white;
    display:inline-block;
    padding:4px 10px;
    border-radius:20px;
    font-weight:bold;
    margin-bottom: 10px;
}

@media (max-width: 768px) {
    .produto-card {
        height: auto;
        padding: 10px;
    }
    .produto-imagem {
        width: 100px;
        height: 100px;
    }
    .produto-preco {
        font-size: 1.2rem;
    }
    .produto-info p {
        font-size: 1.1rem;
    }
}
</style>
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
            except Exception as e:
                st.warning(f"❌ Nenhum resultado encontrado para {nome_mercado}.")

    for r in resultados:
        with st.container():
            st.markdown('<div class="produto-card">', unsafe_allow_html=True)
            st.markdown(f"<div class='mercado-nome'><strong>🏪 {r.get('mercado', 'Mercado')}</strong></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='produto-imagem'><img src='{r.get('imagem')}'></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='produto-info'><p><strong>Nome:</strong> {r.get('nome')}</p><p><strong>Marca:</strong> {r.get('marca')}</p></div>", unsafe_allow_html=True)
            preco = r.get("preco")
            if isinstance(preco, (int, float)):
                st.markdown(f"<div class='produto-preco'>R$ {preco:.2f}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='produto-preco'>Preço não disponível</div>", unsafe_allow_html=True)
            if r.get("link"):
                st.markdown(f"<div class='produto-link'><a href='{r['link']}' target='_blank'>🔗 Comprar agora</a></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
