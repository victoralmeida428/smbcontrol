import smbclient
from .models import SMBFile, ClientProperties
from . import parser
from . import serializer
from typing import List, Iterator, Any
from .exceptions import SMBProtocolError
import os
import pandas as pd

class Client:
    """
    Cliente para ler e escrever arquivos cmbprotocol
    DIRETAMENTE de um compartilhamento SMB.
    """

    _session_registered = False

    def __init__(self, properties: ClientProperties):
        """
        Inicializa o cliente com as credenciais do servidor SMB.

        Args:
            servidor: O IP ou nome do host do servidor (ex: "192.168.1.50")
            share: O nome do compartilhamento (ex: "Documentos")
            usuario: Nome de usuário para o login no SMB
            senha: Senha para o login no SMB
            encoding: Encoding dos arquivos
        """
        self.servidor = properties.servidor
        self.share = properties.share
        self.usuario = properties.usuario
        self.senha = properties.senha
        self.encoding = properties.encoding
        self.connect()
    
    def connect(self):
        """Registra a sessão SMB explicitamente."""
        if self._session_registered:
            return # Já está conectado
        
        try:
            smbclient.ClientConfig(username=self.usuario,
                password=self.senha,)
            self._session_registered = True
        except Exception as e:
            raise SMBProtocolError(f"Falha ao registrar sessão com {self.servidor}: {e}") from e
    
    def _get_unc_path(self, nome_arquivo: str) -> str:
        """Helper interno para montar o caminho de rede completo."""
        # Garante que o nome do arquivo não tenha barras invertidas no início
        nome_arquivo_limpo = nome_arquivo.lstrip("\\/")
        return rf"\\{self.servidor}\{self.share}\{nome_arquivo_limpo}"

    def read_csv(self, *path_parts: str, **kwargs) -> pd.DataFrame:
        """
        Lê um arquivo CSV de um servidor SMB diretamente em um DataFrame pandas.

        Args:
            *path_parts: Partes do caminho para o arquivo (ex: "dados", "relatorio.csv")
            **kwargs: Argumentos adicionais passados para pandas.read_csv()
                      (ex: sep=';', header=0, dtype={'col': str})
        
        Returns:
            Um pandas.DataFrame com os dados.
        """
        # CORREÇÃO: A assinatura é *args: str, não *args: List[str]
        caminho_completo = self._get_unc_path(os.path.join('', *path_parts))
        
        # 'encoding' em kwargs tem precedência sobre o 'encoding' do cliente
        encoding = kwargs.pop('encoding', self.encoding)

        try:
            with smbclient.open_file(
                caminho_completo,
                mode="r", # CSV é lido como texto
                encoding=encoding
                # Não precisa de username/password, a sessão está registrada
            ) as f:
                # Passa o 'encoding' de volta para o pandas
                if 'encoding' not in kwargs:
                     kwargs['encoding'] = encoding
                return pd.read_csv(f, **kwargs)
        except Exception as e:
            raise SMBProtocolError(f"Falha ao LER CSV do SMB em {caminho_completo}: {e}") from e

    def read_excel(self, *path_parts: str, **kwargs) -> pd.DataFrame:
        """
        Lê um arquivo Excel de um servidor SMB diretamente em um DataFrame pandas.

        Args:
            *path_parts: Partes do caminho para o arquivo (ex: "planilhas", "vendas.xlsx")
            **kwargs: Argumentos adicionais passados para pandas.read_excel()
                      (ex: sheet_name='Aba1', header=2)
        
        Returns:
            Um pandas.DataFrame com os dados.
        """
        caminho_completo = self._get_unc_path(os.path.join('', *path_parts))
        
        try:
            with smbclient.open_file(
                caminho_completo,
                mode="rb"  # IMPORTANTE: Excel é arquivo binário
            ) as f:
                # pandas.read_excel(f) espera um objeto de arquivo binário
                return pd.read_excel(f, **kwargs)
        except Exception as e:
            raise SMBProtocolError(f"Falha ao LER Excel do SMB em {caminho_completo}: {e}") from e

    def write_csv(self, data: pd.DataFrame, *path_parts: str, **kwargs):
        """
        Escreve um DataFrame pandas para um arquivo CSV em um servidor SMB.

        Args:
            data (pd.DataFrame): O DataFrame a ser salvo.
            *path_parts: Partes do caminho para o arquivo (ex: "dados", "saida.csv")
            **kwargs: Argumentos adicionais passados para pandas.to_csv()
                      (ex: sep=';', index=False, decimal=',')
        """
        caminho_completo = self._get_unc_path(os.path.join('', *path_parts))
        
        # Pega o encoding dos kwargs ou usa o padrão do cliente
        # O 'index=False' é muito comum, considere passá-lo por padrão se quiser
        # kwargs.setdefault('index', False) 
        encoding = kwargs.pop('encoding', self.encoding)

        try:
            # Abre em modo 'w' (texto) com o encoding correto
            with smbclient.open_file(
                caminho_completo,
                mode="w",
                encoding=encoding
            ) as f:
                # O 'f' já é um stream de texto, o pandas não precisa de encoding
                data.to_csv(f, **kwargs)
        except Exception as e:
            raise SMBProtocolError(f"Falha ao ESCREVER CSV no SMB em {caminho_completo}: {e}") from e

    def write_excel(self, data: pd.DataFrame, *path_parts: str, **kwargs):
        """
        Escreve um DataFrame pandas para um arquivo Excel em um servidor SMB.

        Args:
            data (pd.DataFrame): O DataFrame a ser salvo.
            *path_parts: Partes do caminho para o arquivo (ex: "planilhas", "saida.xlsx")
            **kwargs: Argumentos adicionais passados para pandas.to_excel()
                      (ex: sheet_name='Resultados', index=False, engine='openpyxl')
        """
        caminho_completo = self._get_unc_path(os.path.join('', *path_parts))
        
        # O 'engine' (ex: 'openpyxl') é passado via kwargs
        # O 'index=False' também é muito comum aqui
        # kwargs.setdefault('index', False)

        try:
            # Abre em modo 'wb' (binário)
            with smbclient.open_file(
                caminho_completo,
                mode="wb"
            ) as f:
                # pandas.to_excel escreve em um stream binário
                data.to_excel(f, **kwargs)
        except Exception as e:
            raise SMBProtocolError(f"Falha ao ESCREVER Excel no SMB em {caminho_completo}: {e}") from e
      
    def list_dir(self, *caminho_diretorio: List[str]) -> List[str]:
        """
        Lista o conteúdo (nomes de arquivos e pastas) de um diretório no servidor SMB.

        Args:
            caminho_diretorio: O caminho do diretório *dentro* do share.
                               Se omitido (string vazia), lista a raiz do share.
                               (ex: "dados", "relatorios_mensais")
        
        Returns:
            Uma lista de strings com os nomes dos arquivos e pastas.
        """

        caminho_completo = self._get_unc_path(os.path.join('', *caminho_diretorio))
        
        try:
            return smbclient.listdir(
                caminho_completo,
                username=self.usuario,
                password=self.senha
            )
        except Exception as e:
            raise SMBProtocolError(f"Falha ao LISTAR diretório SMB em {caminho_completo}: {e}") from e

    def scandir(self, *caminho_diretorio: List[str]) -> Iterator[Any]:
        """
        Escaneia um diretório no servidor SMB, retornando mais detalhes.

        Args:
            caminho_diretorio: O caminho do diretório *dentro* do share.
                               Se omitido (string vazia), escaneia a raiz do share.
        
        Returns:
            Um iterador de objetos DirEntry, que contêm .name, .is_dir(), .is_file() etc.
        """
        caminho_completo = self._get_unc_path(os.path.join('', *caminho_diretorio))
        
        try:
            # scandir retorna um iterador, o que é eficiente
            yield from smbclient.scandir(
                caminho_completo,
                username=self.usuario,
                password=self.senha
            )
        except Exception as e:
            raise SMBProtocolError(f"Falha ao ESCANEAR diretório SMB em {caminho_completo}: {e}") from e