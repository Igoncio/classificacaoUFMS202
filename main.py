import PyPDF2
import re

def extrair_texto_pdf(caminho_pdf):

    # Lê o conteúdo de um arquivo PDF e retorna como texto.

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

def filtraInscritosCurso(inscritosCompleto, notas_pdf, curso="Sistemas de Informação"):

    # Os cursos estão todos em letras maiúsculas originalmente no PDF,
    # então decidi transformar todas as linhas com
    # os nomes dos inscritos em uppercase para que a
    # a condicional pudesse funcionar, pois, a lista
    # inscritosCurso estava retornando vazia.

    linhas = inscritosCompleto.upper().split('\n')
    curso = curso.upper()

    inscritosCurso = []
    dictInscritos = {}

    # Contador de inscritos ausentes ou eliminados

    ausentes_ou_eliminados = 0

    #Filtra todos os inscritos em SI

    for linha in linhas:
        if curso in linha:
            match = re.match("^[0-9]{7}", linha) # Filtra apenas as linhas que começam com 7 números (número de inscrição)
            if match:
                inscritosCurso.append(match.group())
    
    # Se o inscritosCurso não tiver preenchido, não faz sentido
    # continuar com a função, então já retorno um dict com apenas
    # a key curso.

    if not len(inscritosCurso):
        return dict(curso=curso)

    # Extrai o texto completo do notas.pdf

    notasPdfCompleto = extrair_texto_pdf(notas_pdf)
    linhas = notasPdfCompleto.upper().split('\n')

    for linha in linhas:

        # Por algum motivo desconhecido, o PDF não quebra linha
        # em algumas linhas e coloca SERVIÇO PÚBLICO FEDERAL
        # concatenado à nota. Então, foi necessário splitar esta 
        # substring para não dar erro futuramente

        if "SERVIÇO PÚBLICO FEDERAL" in linha:
            linha = linha.replace("SERVIÇO PÚBLICO FEDERAL", "")

        # Como a primeira coluna do notas.pdf sempre vai ser o
        # número de inscrição do candidato, então acabo pegando
        # apenas os primeiros 7 caracteres da string para comparar

        if linha[0:7] in inscritosCurso:
            
            # Todos os candidatos eliminados tem associado à ele o 
            # item do edital que fez ele ser eliminado. Além disso,
            # os candidatos ausentes são indicados que estavam ausentes.
            # Por conta disso, não faz sentido continuar com o código
            # para estes candidatos. Porém, ainda assim, quis contabilizar
            # a quantidade de ausentes ou eliminados para mostrar ao candidato
            # que está executando o script a quantidade de pessoas que não vão
            # ser contabilizados para o curso escolhido.

            if "ITEM" in linha or "AUSENTE" in linha:
                ausentes_ou_eliminados += 1
                continue

            linha = linha.replace(",", ".")
            match = re.split(r"\s", linha)

            # A condicional do tamanho é por conta que os candidatos
            # treineiros não tem a coluna modalidade, afinal, são treineiros.
            # Como treineiros não valem a disputa pela vaga, então podemos
            # desconsiderá-los.

            if len(match) < 7:
                continue
            else:
                for i in range(2, 7):
                    match[i] = float(match[i])

            if match:
                dictInscritos[match[0]] = {"modalidade":match[1],
                                           "vL":match[2],
                                           "vH":match[3],
                                           "vN":match[4],
                                           "vM":match[5],
                                           "redacao":match[6],
                                           "curso":curso,
                                        }
    return dictInscritos, ausentes_ou_eliminados

def calcular_media_inscritos(inscritosCompleto, caminho_pdf="notas.pdf"):

    # Pesos respectivos de cada matéria abaixo:

    pR = 2 # Peso redação 
    pH = 1 # Peso humanas
    pN = 1 # Peso naturezas
    pL = 2 # Peso linguagens
    pM = 2 # Peso matemática

    notasOrdenadas = []

    inscritos, ausentes_ou_eliminados = filtraInscritosCurso(inscritosCompleto, caminho_pdf)

    if len(inscritos.keys()):
        for numInscricao, inscrito in inscritos.items():
            inscrito["vL"] = 500 + 100 * (inscrito["vL"] - 16.4309) / 4.6012
            inscrito["vH"] = 500 + 100 * (inscrito["vH"] - 16.3687) / 6.3131
            inscrito["vN"] = 500 + 100 * (inscrito["vN"] - 10.3303) / 5.1418
            inscrito["vM"] = 500 + 100 * (inscrito["vM"] - 10.1569) / 6.0060
            inscrito["notaFinal"] = (inscrito["vL"] * pL + inscrito["vH"] * pH + inscrito["vN"] * pN + inscrito["vM"] * pM + 
                                    inscrito["redacao"] * pR) / sum([pR, pH, pN, pL, pM])
            # print("{} : {}".format(numInscricao, inscrito["notaFinal"]))
            notasOrdenadas.append((numInscricao, inscrito["notaFinal"]))

    else:
        print(f"Nenhum dado encontrado para '{inscritos["curso"]}'.")
        return None

    for i in list(enumerate(sorted(notasOrdenadas, key= lambda inscrito: inscrito[1]))):
        print("{}. {} : {}".format(i[0], i[1][0], i[1][1])) 

    print("Total de ausentes ou eliminados: {}".format(ausentes_ou_eliminados))

# Caminho do arquivo PDF
caminho_pdf = "inscritos.pdf"  # Substitua pelo caminho do seu arquivo PDF

# Processo de leitura e cálculo
texto_pdf = extrair_texto_pdf(caminho_pdf)

if texto_pdf:
    media_inscritos = calcular_media_inscritos(texto_pdf)
