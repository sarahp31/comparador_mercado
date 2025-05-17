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

# definir wide mode
st.set_page_config(layout="wide")

st.markdown("""
<style>
/* Fundo da página */
.stApp {
    background: linear-gradient(to bottom, #d4f5dc, #a8e6b1);
    font-family: 'Segoe UI', sans-serif;
    color: #2c3e50;
}

/* Título principal */
h1, h2 {
    color: #2c3e50;
}

/* Card de produto */
.produto-card {
    background: white;
    border-radius: 20px;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
    padding: 20px;
    margin-bottom: 30px;
    transition: transform 0.2s ease;
}

.produto-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12);
}

/* Imagem */
.produto-card img {
    max-width: 100%;
    max-height: 180px;
    margin-bottom: 15px;
    border-radius: 12px;
    object-fit: contain;
}

/* Texto do produto */
.produto-card p {
    font-size: 16px;
    margin: 5px 0;
}

/* Preço */
.produto-card .preco {
    font-size: 18px;
    font-weight: bold;
    color: #27ae60;
    margin-top: 10px;
}

/* Link */
.produto-card a {
    display: inline-block;
    margin-top: 12px;
    text-decoration: none;
    color: white;
    background-color: #2980b9;
    padding: 8px 16px;
    border-radius: 8px;
    transition: background 0.2s ease;
}

.produto-card a:hover {
    background-color: #1c5980;
}

/* Expander */
details summary {
    font-weight: bold;
    margin-top: 10px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)


button_style = """
<style>
/* Aplica o estilo aos botões, exceto os com a classe "logout-button" */
div.stButton:not(.logout-button) > button {
    background: linear-gradient(to right, #ffa500, #ff6a00);
    color: white !important;
    font-size: 50px;
    font-weight: bold;
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.1s ease-in-out;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

/* Efeito de hover */
div.stButton:not(.logout-button) > button:hover {
    background: linear-gradient(to right, #ff7a00, #e65c00);
    transform: scale(1.05);
    box-shadow: 0 6px 10px rgba(0,0,0,0.4);
}

/* Efeito de clique */
div.stButton:not(.logout-button) > button:active {
    transform: scale(0.98);
    box-shadow: 0 2px 5px rgba(0,0,0,0.5);
    color: white !important;
}

/* Evita que o Streamlit altere a cor durante o foco */
div.stButton:not(.logout-button) > button:focus {
    color: white !important;
}
</style>
"""

# Aplica o CSS personalizado para os botões
st.markdown(button_style, unsafe_allow_html=True)


# Criar abas
tab1, tab2 = st.tabs(["Produto Único", "Upload de Arquivo"])

with tab1:
    st.title("🛒 Comparador de Preços de Supermercados")
    st.write("Digite um produto e veja os preços nos mercados.")

    # Campo de entrada do usuário
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
            outros_produtos = {}
            
            for nome_mercado, funcao in mercados.items():
                try:
                    resultado = funcao(produto)
                    if resultado:
                        produto_principal, outros = resultado
                        if isinstance(produto_principal, dict) and "erro" not in produto_principal:
                            resultados.append(produto_principal)
                            outros_produtos[nome_mercado] = outros
                    else:
                        st.warning(f"❌ Nenhum resultado encontrado para {nome_mercado}.")
                except Exception as e:
                    st.error(f"⚠️ Erro ao buscar no {nome_mercado}: {str(e)}")

        if resultados:
            # Encontrar o menor preço
            precos_validos = [r.get("preco") for r in resultados if isinstance(r.get("preco"), (int, float))]
            menor_preco = min(precos_validos) if precos_validos else None

            for r in resultados:
                with st.container():
                    preco_atual = r.get("preco")
                    is_melhor_preco = isinstance(preco_atual, (int, float)) and preco_atual == menor_preco
                    
                    # Aplicar estilo baseado no preço
                    container_class = "melhor-preco" if is_melhor_preco else "preco-normal"
                    
                    st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
                    
                    st.subheader(f"🏪 {r.get('mercado', 'Mercado Desconhecido')}")

                    col1, col2 = st.columns([1, 2])
                    with col1:
                        imagem_url = r.get("imagem", "N/A")
                        if imagem_url and imagem_url != "N/A":
                            st.image(imagem_url, width=150)
                        else:
                            st.write("📷 Imagem não disponível")

                    with col2:
                        st.write(f"**Nome:** {r.get('nome', 'Não disponível')}")
                        st.write(f"**Marca:** {r.get('marca', 'Não disponível')}")

                        preco = r.get("preco")
                        if isinstance(preco, (int, float)):
                            st.write(f"**Preço:** R$ {preco:.2f}")
                        else:
                            st.write("**Preço:** Não disponível")

                        link = r.get("link")
                        if link:
                            st.markdown(f"[🔗 Link para compra]({link})", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                    # Seção de outros produtos
                    mercado = r.get('mercado')
                    if mercado in outros_produtos and outros_produtos[mercado]:
                        with st.expander(f"Produtos similares"):
                            st.markdown('<div class="outros-produtos">', unsafe_allow_html=True)
                            for outro_produto in outros_produtos[mercado][:5]:  # Mostrar apenas os 5 primeiros
                                col1, col2 = st.columns([1, 2])
                                with col1:
                                    if "imagem" in outro_produto and outro_produto["imagem"]:
                                        st.image(outro_produto["imagem"], width=100)
                                    else:
                                        st.write("📷")
                                with col2:
                                    st.write(f"**{outro_produto.get('nome', 'Nome não disponível')}**")
                                    if "preco" in outro_produto and isinstance(outro_produto["preco"], (int, float)):
                                        st.write(f"R$ {outro_produto['preco']:.2f}")
                                    if "link" in outro_produto:
                                        st.markdown(f"[🔗 Ver produto]({outro_produto['link']})", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("---")
        else:
            st.warning("❌ Nenhum produto encontrado.")



st.markdown(
    """
    <style>
    /* ====== Ajustes Globais ====== */
    body {
        background-color: #f5f7fa;
        font-family: "Open Sans", sans-serif;
        color: #333;
    }

    /* ====== Seção do Produto ====== */
    .produto-section {
        margin-bottom: 40px;
        padding: 20px;
        border-radius: 12px;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .produto-section h2 {
        margin-bottom: 20px;
        color: #2c3e50;
        font-size: 1.5rem;
        font-weight: 700;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* ====== Card do Produto ====== */
    .produto-card {
        background: #fafafa;
        border: 1px solid #ececec;
        border-radius: 12px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 550px;  /* Altura fixa do card */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .produto-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
    }

    /* ====== Nome do Mercado ====== */
    .mercado-nome {
        font-weight: 700;
        font-size: 1.5rem;
        color: #34495e;
        margin-bottom: 10px;
    }

    /* ====== Container da Imagem ====== */
    .produto-imagem {
        width: 150px;     /* Largura fixa */
        height: 150px;    /* Altura fixa */
        margin: 0 auto 15px auto;  /* Centraliza horizontalmente */
    }
    .produto-imagem img {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Recorta a imagem sem deformar */
        border-radius: 8px;
    }

    /* ====== Informações do Produto ====== */
    .produto-info {
        margin-bottom: 10px;
    }
    .produto-info p {
        margin: 5px 0;
        font-size: 1.5rem;
        color: #444;
    }

    /* ====== Preço do Produto ====== */
    .produto-preco {
        font-size: 1.4rem;
        font-weight: 600;
        color: #27ae60; /* Verde para destaque */
        margin-bottom: 10px;
    }

    /* ====== Link / Botão de Ação ====== */
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
    </style>
    """,
    unsafe_allow_html=True
)

with tab2:

    with st.container():
        st.title("📂 Upload de Arquivo")
        st.write("Cole uma lista de produtos para comparar os preços.")

        produtos_texto = st.text_area("Cole os nomes dos produtos (um por linha):")

        if st.button("Buscar Produtos"):

            if "produtos_aprovados" in st.session_state:
                del st.session_state.produtos_aprovados

            produtos_lista = [p.strip() for p in produtos_texto.split("\n") if p.strip()]
            
            if not produtos_lista:
                st.warning("⚠️ Nenhum produto válido encontrado.")
            else:
                st.success(f"🔍 {len(produtos_lista)} produtos detectados para busca!")

                mercados = {
                    "Pão de Açúcar": buscar_pao_de_acucar,
                    "Extra": buscar_extra,
                    "Sonda": buscar_sonda,
                    "Carrefour": buscar_carrefour,
                    "St Marche": buscar_st_marche
                }

                # Inicializa a lista de produtos aprovados, se ainda não existir
                if "produtos_aprovados" not in st.session_state:
                    st.session_state.produtos_aprovados = {}

                progress_bar = st.progress(0)
                status_text = st.empty()

                total_produtos = len(produtos_lista)
                resultado_buscado = {}

                for idx_produto, produto in enumerate(produtos_lista):
                    progress = (idx_produto + 1) / total_produtos
                    progress_bar.progress(progress)
                    status_text.text(f"🔄 Buscando ({idx_produto + 1}/{total_produtos}): {produto}")

                    resultado_buscado[produto] = {"principais": [], "outros": {}}

                    for nome_mercado, funcao in mercados.items():
                        try:
                            resultado = funcao(produto)
                            if resultado:
                                produto_principal, outros = resultado

                                if isinstance(produto_principal, dict) and "erro" not in produto_principal:
                                    produto_principal["id"] = 0
                                    produto_principal["mercado"] = nome_mercado
                                    # Ajusta nome e marca para o produto principal
                                    produto_principal["nome"] = produto_principal.get("nome")
                                    produto_principal["nome"] = produto_principal["nome"].title() if produto_principal["nome"] else "-"
                                    produto_principal["marca"] = produto_principal.get("marca")
                                    produto_principal["marca"] = produto_principal["marca"].lower().title() if produto_principal["marca"] else "-"
                                    resultado_buscado[produto]["principais"].append(produto_principal)

                                    for i, similar in enumerate(outros, start=1):
                                        similar["id"] = i
                                        similar["nome"] = similar.get("nome")
                                        similar["nome"] = similar["nome"].title() if similar["nome"] else "-"
                                        similar["marca"] = similar.get("marca")
                                        similar["marca"] = similar["marca"].lower().title() if similar["marca"] else "-"
                                        
                                    resultado_buscado[produto]["outros"][nome_mercado] = outros
                        except Exception as e:
                            st.error(f"⚠️ Erro ao buscar {produto} no {nome_mercado}: {str(e)}")

                progress_bar.progress(1.0)
                status_text.text("✅ Busca concluída!")
                st.session_state.resultado_buscado = resultado_buscado
                st.rerun()  

        PLACEHOLDER_URL = "https://via.placeholder.com/150?text=Sem+Imagem"

        if "resultado_buscado" in st.session_state and st.session_state.resultado_buscado:
            st.markdown("## 📊 Resultados da Busca")

            for produto, resultados in st.session_state.resultado_buscado.items():
                # Título do produto
                st.markdown(
                    f"<div class='produto-section'><h2 style='color:#4CAF50;'>🛍️ {produto}</h2></div>",
                    unsafe_allow_html=True
                )
                
                if resultados["principais"]:
                    # Cria colunas de acordo com o número de produtos encontrados
                    colunas = st.columns(len(resultados["principais"]))

                    for idx, produto_info in enumerate(resultados["principais"]):
                        with colunas[idx]:
                            # Verifica se a imagem é válida; caso contrário, usa placeholder
                            imagem_url = produto_info.get("imagem")
                            if not imagem_url or imagem_url == "N/A":
                                imagem_url = PLACEHOLDER_URL
                            
                            # Define chave única para o card (usando o nome do produto e o mercado)
                            unique_key = f"{produto}_{produto_info.get('mercado', '-')}"
                            is_aprovado = unique_key in st.session_state.produtos_aprovados
                            
                            # Se aprovado, adiciona sinalização visual
                            card_style = "border: 3px solid green;" if is_aprovado else ""
                            approved_badge = ("<div style='background-color: green; color: white; padding: 4px; "
                                              "border-radius: 4px; margin-bottom: 10px;'>APROVADO</div>") if is_aprovado else ""
                            
                            # Monta o HTML do card, incluindo sinalização se aprovado
                            card_html = f"""
                            <div class="produto-card" style="{card_style}">
                                {approved_badge}
                                <!-- Nome do Mercado -->
                                <div class="mercado-nome">
                                    🏪 {produto_info.get('mercado', '-') or '-'}
                                </div>
                                
                                <!-- Imagem -->
                                <div class="produto-imagem">
                                    <img src="{imagem_url}" alt="Imagem do Produto"/>
                                </div>
                                
                                <!-- Informações -->
                                <div class="produto-info">
                                    <p><strong>Nome:</strong> {produto_info.get('nome') or '-'}</p>
                                    <p><strong>Marca:</strong> {produto_info.get('marca') or '-'}</p>
                                </div>
                                
                                <!-- Preço -->
                                <div class="produto-preco">
                                    {"R$ " + f"{produto_info.get('preco'):.2f}" if isinstance(produto_info.get("preco"), (int, float)) else "-"}
                                </div>
                                
                                <!-- Link de Compra -->
                                <div class="produto-link">
                                    {f"<a href='{produto_info.get('link')}' target='_blank'>🔗 Comprar agora</a>" if produto_info.get("link") else "-"}
                                </div>
                            </div>
                            """
                            # Renderiza o HTML do card
                            st.html(card_html)

                            
                            # Botão de Aprovar/Desaprovar para o produto principal
                            if is_aprovado:
                                if st.button("Desaprovar", key=f"aprovar_{unique_key}"):
                                    del st.session_state.produtos_aprovados[unique_key]
                                    st.rerun()
                            else:
                                if st.button("Aprovar", key=f"aprovar_{unique_key}"):
                                    st.write(produto_info)
                                    st.session_state.produtos_aprovados[unique_key] = produto_info
                                    st.rerun()
                                                        
                            # Alternativas (já existentes)
                            mercado_atual = produto_info.get("mercado")
                            outros_produtos = resultados["outros"].get(mercado_atual, [])
                            if outros_produtos:
                                with st.expander("Ver alternativas"):
                                    for alternative in outros_produtos:
                                        alt_nome = alternative.get("nome") or "-"
                                        alt_marca = alternative.get("marca") or "-"
                                        alt_preco = (
                                            f"R$ {alternative.get('preco'):.2f}"
                                            if isinstance(alternative.get("preco"), (int, float))
                                            else "-"
                                        )
                                        alternative_label = f"{alt_nome} - {alt_marca} - {alt_preco}"
                                        if st.button(alternative_label, key=f"{produto}_{mercado_atual}_{alternative['id']}"):
                                            alternative["mercado"] = mercado_atual
                                            # Swap: o produto principal atual vai para os outros e o selecionado se torna o principal.
                                            st.session_state.resultado_buscado[produto]["outros"][mercado_atual] = [
                                                alt for alt in st.session_state.resultado_buscado[produto]["outros"][mercado_atual]
                                                if alt["id"] != alternative["id"]
                                            ]
                                            st.session_state.resultado_buscado[produto]["outros"][mercado_atual].append(produto_info)
                                            st.session_state.resultado_buscado[produto]["principais"][idx] = alternative
                                            # Se o produto estava aprovado, removemos a aprovação,
                                            # pois o produto principal mudou.
                                            if unique_key in st.session_state.produtos_aprovados:
                                                del st.session_state.produtos_aprovados[unique_key]
                                            st.rerun()
                else:
                    st.warning(f"❌ Nenhum produto encontrado para {produto}.")

    # Ao final, exibe a lista de produtos aprovados para teste
    if 'produtos_aprovados' in st.session_state:
        st.markdown("## Produtos Aprovados")

        if st.button("Gerar Tabela Final"):
            # Define a ordem das colunas que queremos
            colunas = [
                "Produto",
                "avg_price_extra",
                "avg_price_pao_de_acucar",
                "avg_price_sonda",
                "avg_price_carrefour",
                "avg_price_st_marche",
                "link_extra",
                "link_pao_de_acucar",
                "link_sonda",
                "link_carrefour",
                "link_st_marche"
            ]

            # Lista onde guardaremos os dicionários (cada um será uma linha da tabela)
            dados_linhas = []

            mercados_slug = {
                "Extra": "extra",
                "Pão de Açúcar": "pao_de_acucar",
                "Sonda": "sonda",
                "Carrefour": "carrefour",
                "St Marche": "st_marche"
            }

            # Percorre todos os produtos buscados
            for produto_nome, resultados in st.session_state.resultado_buscado.items():
                linha = {
                    "Produto": produto_nome,
                    "avg_price_extra": "-",
                    "avg_price_pao_de_acucar": "-",
                    "avg_price_sonda": "-",
                    "avg_price_carrefour": "-",
                    "avg_price_st_marche": "-",
                    "link_extra": "-",
                    "link_pao_de_acucar": "-",
                    "link_sonda": "-",
                    "link_carrefour": "-",
                    "link_st_marche": "-"
                }

                # Verifica se há algum produto aprovado por mercado
                for mercado_nome, mercado_slug in mercados_slug.items():
                    unique_key = f"{produto_nome}_{mercado_nome}"
                    if unique_key in st.session_state.produtos_aprovados:
                        info_aprovado = st.session_state.produtos_aprovados[unique_key]
                        preco = info_aprovado.get("preco", "-")
                        link = info_aprovado.get("link", "-")

                        linha[f"avg_price_{mercado_slug}"] = preco
                        linha[f"link_{mercado_slug}"] = link

                dados_linhas.append(linha)

            # Monta o DataFrame final
            df_final = pd.DataFrame(dados_linhas, columns=colunas)

            # ========== [1] ESTILIZANDO A TABELA COM HTML + CSS ========== #
            table_css = """
            <style>
            .styled-table {
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 14px;
                font-family: sans-serif;
                min-width: 600px;
                width: 100%;
            }

            .styled-table thead tr {
                background-color: #009879;
                color: #ffffff;
                /* não precisa colocar text-align aqui */
                font-size: 16px;
                font-weight: bold;
            }

            /* Força a centralização das células de cabeçalho,
            mesmo que haja estilo inline gerado pelo pandas */
            .styled-table thead th {
                text-align: center !important;
            }

            .styled-table th,
            .styled-table td {
                padding: 12px 15px;
                border: 1px solid #dddddd;
            }

            .styled-table tbody tr {
                border-bottom: 1px solid #dddddd;
            }

            .styled-table tbody tr:nth-of-type(even) {
                background-color: #f3f3f3;
            }

            .styled-table tbody tr:last-of-type {
                border-bottom: 2px solid #009879;
            }
            </style>
            """

            # E então:
            html_table = df_final.to_html(classes="styled-table", index=False)
            st.html(table_css + html_table)

            # [2] BOTÃO PARA DOWNLOAD EM EXCEL
            # Converte o DataFrame em bytes (Excel em memória)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df_final.to_excel(writer, index=False, sheet_name="Dados")
            # Pega o conteúdo binário
            excel_data = buffer.getvalue()

            # Exibe o botão de download
            st.download_button(
                label="Exportar para Excel",
                data=excel_data,
                file_name="supermercados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )






                        
