from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SMBHeader:
    """Representa o cabeçalho de um arquivo smbprotocol."""
    versao: str
    id_arquivo: str

@dataclass
class SMBItem:
    """Representa um item de dados individual."""
    id: int
    descricao: str
    valor: float

@dataclass
class SMBFile:
    """Representação Python completa de um arquivo smbprotocol."""
    header: SMBHeader
    itens: List[SMBItem]
    metadata: Dict[str, str]

@dataclass
class ClientProperties:
    servidor: str
    share: str
    usuario: str
    senha: str
    encoding: str = "utf-8"