from smbcontrol.client import ClientProperties, Client

def main():
    clientProps = ClientProperties(
        servidor='pastor.local',
        usuario='victorgomes',
        senha='95546353',
        share='Analytics',
        encoding='latin-1'
    )
    client = Client(clientProps)
    df = client.read_csv('MalaDiretaCoordenadas.csv', encoding='latin-1', sep=';')

    client.write_csv(df, 'MalaDiretaCoordenadas_copia.csv', sep=";")
    


if __name__ == "__main__":
    main()
