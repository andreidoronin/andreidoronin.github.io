import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path

ARQUIVO_XML = "curriculo_lattes_limpo.xml"
ARQUIVO_JSON = "dados_lattes.json"


def obter_atributo(elemento, nome):
    if elemento is None:
        return ""
    return elemento.attrib.get(nome, "").strip()


def extrair_url(texto):
    if not texto:
        return ""
    resultado = re.search(r"https?://[^\]\s]+", texto)
    return resultado.group(0) if resultado else ""


def ler_formacao(raiz):
    formacoes = []
    caminho = "./DADOS-GERAIS/FORMACAO-ACADEMICA-TITULACAO"

    for curso in raiz.findall(caminho + "/*"):
        tipo = curso.tag
        if tipo not in ("GRADUACAO", "MESTRADO", "DOUTORADO"):
            continue

        formacoes.append({
            "tipo": tipo,
            "curso": obter_atributo(curso, "NOME-CURSO"),
            "instituicao": obter_atributo(curso, "NOME-INSTITUICAO"),
            "inicio": obter_atributo(curso, "ANO-DE-INICIO"),
            "conclusao": obter_atributo(curso, "ANO-DE-CONCLUSAO"),
            "status": obter_atributo(curso, "STATUS-DO-CURSO"),
            "titulo": obter_atributo(
                curso, "TITULO-DA-DISSERTACAO-TESE"
            ),
        })

    return formacoes


def ler_artigos(raiz):
    artigos = []
    caminho = "./PRODUCAO-BIBLIOGRAFICA/ARTIGOS-PUBLICADOS/ARTIGO-PUBLICADO"

    for artigo in raiz.findall(caminho):
        dados = artigo.find("DADOS-BASICOS-DO-ARTIGO")
        detalhes = artigo.find("DETALHAMENTO-DO-ARTIGO")

        if dados is None:
            continue

        artigos.append({
            "titulo": obter_atributo(dados, "TITULO-DO-ARTIGO"),
            "ano": obter_atributo(dados, "ANO-DO-ARTIGO"),
            "periodico": obter_atributo(
                detalhes, "TITULO-DO-PERIODICO-OU-REVISTA"
            ),
            "doi": obter_atributo(dados, "DOI"),
            "url": extrair_url(
                obter_atributo(dados, "HOME-PAGE-DO-TRABALHO")
            ),
        })

    return sorted(artigos, key=lambda item: item["ano"], reverse=True)


def main():
    raiz = ET.parse(ARQUIVO_XML).getroot()

    dados_gerais = raiz.find("DADOS-GERAIS")
    resumo = dados_gerais.find("RESUMO-CV") if dados_gerais is not None else None

    dados = {
        "nome": obter_atributo(dados_gerais, "NOME-COMPLETO"),
        "resumo_pt": obter_atributo(resumo, "TEXTO-RESUMO-CV-RH"),
        "resumo_en": obter_atributo(resumo, "TEXTO-RESUMO-CV-RH-EN"),
        "formacao": ler_formacao(raiz),
        "artigos": ler_artigos(raiz),
    }

    Path(ARQUIVO_JSON).write_text(
        json.dumps(dados, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("Arquivo dados_lattes.json criado com sucesso.")


if __name__ == "__main__":
    main()
