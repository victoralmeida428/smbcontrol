class SMBProtocolError(Exception):
    """Erro base para qualquer problema relacionado ao cmbprotocol."""
    pass

class SMBParseError(SMBProtocolError):
    """Lançado quando há um erro ao ler/analisar um arquivo."""
    pass

class SMBSerializeError(SMBProtocolError):
    """Lançado quando há um erro ao salvar/serializar um arquivo."""
    pass