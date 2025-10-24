# smbcontrol 🐍

Uma biblioteca Python de alto nível para facilitar a interação com compartilhamentos de rede SMB, com foco principal na integração direta com o Pandas.

Esta biblioteca atua como um wrapper sobre a smbprotocol, projetada para tornar a leitura e escrita de DataFrames do Pandas em servidores SMB tão fácil quanto se estivessem no disco local.

Ela gerencia automaticamente a autenticação segura (NTLMv2, Criptografia) e o ciclo de vida da conexão, permitindo que você se concentre na manipulação dos dados.

## Funcionalidades Principais

Gerenciamento de Sessão Simplificado: Use um bloco with Client(...) as client: para abrir e fechar conexões de forma segura.

## Integração com Pandas:

 - read_csv(): Lê um CSV da rede diretamente para um DataFrame.

 - read_excel(): Lê um Excel da rede diretamente para um DataFrame.

 - write_csv(): Escreve um DataFrame em um arquivo CSV na rede.

 - write_excel(): Escreve um DataFrame em um arquivo Excel na rede.

## Utilitários de Arquivo:

 - list_dir(): Lista nomes de arquivos e pastas.

 - scandir(): Escaneia um diretório (retornando detalhes como is_dir()).


## Dependências

Este projeto requer as seguintes bibliotecas Python:

 - smbprotocol

 - pandas

 - openpyxl (Necessário para a funcionalidade read_excel e write_excel)

## Instalação


## Usando uv
uv pip install git+[https://github.com/victoralmeida428/smbcontrol](https://github.com/seu-usuario/smbcontrol.git)

## Usando pip
pip install git+[https://github.com/victoralmeida428/smbcontrol](https://github.com/seu-usuario/smbcontrol.git)


# Guia Rápido (Exemplo de Uso)

Este é o padrão de uso recomendado, que gerencia a conexão automaticamente usando um bloco with.
```py
import pandas as pd
from smbcontrol.client import Client, ClientProperties
from smbcontrol.exceptions import SMBProtocolError 

def main():
    # 1. Configure as propriedades da sua conexão
    #    (Baseado na sua imagem: smb://pastor.local/servicos/)
    clientProps = ClientProperties(
        servidor="servidor",              # Ou o IP: "10.202.40.53"
        usuario="usuario",                # Formato recomendado: DOMINIO\usuario
        senha="sua-senha-secreta-aqui",
        share="Analytics",                # O compartilhamento raiz
        encoding="latin-1"                # Encoding padrão para CSVs
    )

    try:
        # 2. Use 'with' para gerenciar a conexão de forma segura
        #    A conexão é aberta no início e fechada no final, mesmo se der erro.
        with Client(clientProps) as client:

            # 3. Listar arquivos em um diretório (ex: na raiz do share)
            print("Escaneando a raiz do share 'Analytics':")
            # Para escanear uma subpasta: client.scandir("subpasta", "outra_pasta")
            for item in client.scandir():
                tipo = "PASTA" if item.is_dir() else "ARQUIVO"
                print(f"- [{tipo}] {item.name}")

            # 4. Ler um CSV diretamente do SMB para um DataFrame
            print("\nLendo 'MalaDiretaCoordenadas.csv'...")
            df = client.read_csv_smb(
                'MalaDiretaCoordenadas.csv', # Caminho/arquivo dentro do share
                encoding='latin-1',          # Argumento opcional do pandas
                sep=';'                      # Argumento opcional do pandas
            )
            print("Leitura concluída. Head do DataFrame:")
            print(df.head())

            # 5. Escrever o DataFrame de volta para o SMB em um novo arquivo
            print("\nEscrevendo cópia do arquivo...")
            client.write_csv_smb(
                df,                                  # O DataFrame
                'MalaDiretaCoordenadas_copia.csv', # Caminho/arquivo de saída
                sep=";",
                index=False # Argumento opcional do pandas
            )
            print("Arquivo de cópia salvo com sucesso!")

    except SMBProtocolError as e:
        print(f"Erro de SMB (conexão, permissão, etc): {e}")
    except FileNotFoundError:
        print(f"Erro: O arquivo não foi encontrado no servidor.")
    except pd.errors.ParserError as e:
        print(f"Erro do Pandas ao tentar ler o arquivo: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    main()
```

Licença

Distribuído sob a licença MIT