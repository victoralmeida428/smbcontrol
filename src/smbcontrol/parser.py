from .models import SMBFile, SMBHeader, SMBItem
from .exceptions import SMBParseError
from typing import TextIO

def parse(arquivo: TextIO) -> SMBFile:
    """
    Lê o conteúdo de um arquivo (em modo texto) e o transforma
    em um objeto SMBFile.
    """
    try:
        # --- AQUI VAI SUA LÓGICA DE PARSE ---
        # Exemplo:
        linha_header = arquivo.readline().strip()
        if not linha_header:
            raise ValueError("Cabeçalho não encontrado")

        header = SMBHeader(versao=linha_header[0:3], id_arquivo=linha_header[3:10])
        
        itens = []
        for linha in arquivo:
            if linha.strip() == "FIM":
                break
            item = SMBItem(id=int(linha[0:5]), descricao=linha[5:20], valor=float(linha[20:]))
            itens.append(item)
            
        return SMBFile(header=header, itens=itens, metadata={})

    except Exception as e:
        raise SMBParseError(f"Falha ao analisar o arquivo: {e}") from e