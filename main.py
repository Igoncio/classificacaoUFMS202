import PyPDF2

def extrair_texto_pdf(caminho_pdf):
    """
    Lê o conteúdo de um arquivo PDF e retorna como texto.
    """
    try:
        with open(caminho_pdf, 'rb') as pdf_file:
            leitor = PyPDF2.PdfReader(pdf_file)
            texto_completo = ""
            for pagina in leitor.pages:
                texto_completo += pagina.extract_text()
            return texto_completo
    except Exception as e:
        print(f"Erro ao ler o PDF: {e}")
        return None

def calcular_media_inscritos(texto, termo="Sistemas de Informação"):
    """
    Calcula a média dos inscritos para um termo específico no texto.
    """
    linhas = texto.split('\n')
    inscritos = []

    for linha in linhas:
        if termo in linha:
            # Extrai os números da linha
            numeros = [int(num) for num in linha.split() if num.isdigit()]
            inscritos.extend(numeros)

    if inscritos:
        media = sum(inscritos) / len(inscritos)
        return media
    else:
        print(f"Nenhum dado encontrado para '{termo}'.")
        return None

# Caminho do arquivo PDF
caminho_pdf = "inscritos.pdf"  # Substitua pelo caminho do seu arquivo PDF

# Processo de leitura e cálculo
texto_pdf = extrair_texto_pdf(caminho_pdf)
if texto_pdf:
    media_inscritos = calcular_media_inscritos(texto_pdf)
    if media_inscritos is not None:
        print(f"A média dos inscritos em Sistemas de Informação é: {media_inscritos:.2f}")
    else:
        print("Não foi possível calcular a média.")
