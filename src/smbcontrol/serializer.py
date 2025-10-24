
from .models import SMBFile
from .exceptions import SMBSerializeError
from typing import TextIO

def serialize(dados: SMBFile, arquivo: TextIO):
    """
    Converte um objeto SMBFile e o escreve em um arquivo (em modo texto).
    """
    try:
        header_str = f"{dados.header.versao}{dados.header.id_arquivo}\n"
        arquivo.write(header_str)
        
        for item in dados.itens:
            # Exemplo de formatação (substitua pelo seu):
            item_str = f"{item.id:05d}{item.descricao:<15s}{item.valor:10.2f}\n"
            arquivo.write(item_str)
            
        arquivo.write("FIM\n")
        
    except Exception as e:
        raise SMBSerializeError(f"Falha ao serializar dados: {e}") from e