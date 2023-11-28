Exemplo de Sistema em Python fazendo CRUD no MongoDB

Esse sistema de exemplo é composto por um conjunto de coleções(collections) que representam pedidos de uma lanchonete, contendo coleções como: clientes, comandas e itens comandas.

O sistema exige que as coleções existam, então basta executar o script Python a seguir para criação das coleções:

~$ python createCollectionsAndData.py 

Para executar o sistema basta executar o script Python a seguir:

~$ python principal.py

Organização

diagrams: Nesse diretório está o diagrama relacional (lógico) do sistema.
O sistema possui três entidades: CLIENTES, COMANDAS e ITENS_COMANDA

src: Nesse diretório estão os scripts do sistema

conexion: Nesse repositório encontra-se o módulo de conexão com o banco de dados Mongo. 

Exemplo de utilização para consultas simples no Oracle:

def listar_clientes(self, oracle:OracleQueries, need_connect:bool=False):
    query = """
            select c.cpf
                , c.nome 
            from clientes c
            order by c.nome
            """
    if need_connect:
        oracle.connect()
    print(oracle.sqlToDataFrame(query))
Exemplo de utilização para alteração de registros no Oracle

from conexion.oracle_queries import OracleQueries
def inserir_cliente(self) -> Cliente:
    # Cria uma nova conexão com o banco que permite alteração
    oracle = OracleQueries(can_write=True)
    oracle.connect()

    # Solicita ao usuario o novo CPF
    cpf = input("CPF (Novo): ")

    if self.verifica_existencia_cliente(oracle, cpf):
        # Solicita ao usuario o novo nome
        nome = input("Nome (Novo): ")
        # Insere e persiste o novo cliente
        oracle.write(f"insert into clientes values ('{cpf}', '{nome}')")
        # Recupera os dados do novo cliente criado transformando em um DataFrame
        df_cliente = oracle.sqlToDataFrame(f"select cpf, nome from clientes where cpf = '{cpf}'")
        # Cria um novo objeto Cliente
        novo_cliente = Cliente(df_cliente.cpf.values[0], df_cliente.nome.values[0])
        # Exibe os atributos do novo cliente
        print(novo_cliente.to_string())
        # Retorna o objeto novo_cliente para utilização posterior, caso necessário
        return novo_cliente
    else:
        print(f"O CPF {cpf} já está cadastrado.")
        return None

Exemplo de utilização para conexão no Mongo;

      # Importa o módulo MongoQueries
      from conexion.mongo_queries import MongoQueries
      
      # Cria o objeto MongoQueries
      mongo = MongoQueries()

      # Realiza a conexão com o Mongo
      mongo.connect()

      # Fecha a conexão com o Mong
      mongo.close()

Exemplo de criação de um documento no Mongo:

      from conexion.mongo_queries import MongoQueries

      import pandas as pd
      
      # Cria o objeto MongoQueries
      mongo = MongoQueries()

      # Realiza a conexão com o Mongo
      mongo.connect()

      # Solicita ao usuario o novo CPF
      cpf = input("CPF (Novo): ")
      # Solicita ao usuario o novo nome
      nome = input("Nome (Novo): ")
      # Solicita ao usuario o novo nome
      telefone = input("Telefone (Novo): ")
      # Solicita ao usuario o novo nome
      email = input("Email (Novo): ")


      # Insere e persiste o novo cliente
      mongo.db["clientes"].insert_one({"cpf_cliente": cpf, "nome_cliente": nome, "telefone_cliente": telefone, "email_cliente": email})
      # Recupera os dados do novo cliente criado transformando em um DataFrame
      df_cliente = pd.DataFrame(list(mongo.db["clientes"].find({"cpf":f"{cpf_cliente}"}, {"cpf_cliente": 1, "nome_cliente": 1, "telefone_cliente": 1, "email_cliete": 1, _id": 0})))
      # Exibe os dados do cliente em formato DataFrame
      print(df_cliente)

      # Fecha a conexão com o Mong
      mongo.close()
controller: Nesse diretório encontram-sem as classes controladoras, responsáveis por realizar inserção, alteração e exclusão dos registros das tabelas.

model: Nesse diretório encontram-ser as classes das entidades descritas no diagrama relacional

reports Nesse diretório encontra-se a classe responsável por gerar todos os relatórios do sistema

utils: Nesse diretório encontram-se scripts de configuração e automatização da tela de informações iniciais

createCollectionsAndData.py: Script responsável por criar as tabelas e registros fictícios. Esse script deve ser executado antes do script principal.py para gerar as tabelas, caso não execute os scripts diretamente no SQL Developer ou em alguma outra IDE de acesso ao Banco de Dados.

principal.py: Script responsável por ser a interface entre o usuário e os módulos de acesso ao Banco de Dados. Deve ser executado após a criação das tabelas.

 
