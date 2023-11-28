from pydoc import cli

from model.comandas import Comanda
from model.clientes import Cliente

from conexion.mongo_queries import MongoQueries
from controller.controller_cliente import Controller_Cliente

from reports.relatorios import Relatorio

from datetime import datetime
from utils import config

from bson import ObjectId
import pandas as pd

class Controller_Comanda:

    
    data_hoje = datetime.today().strftime("%m-%d-%Y")
    
        
    def __init__(self):
        
        self.ctrl_cliente = Controller_Cliente()
        self.mongo = MongoQueries()
        self.relatorio = Relatorio()
        
    def inserir_comanda(self) -> Comanda:
               
        # Cria uma nova conexão com o banco
        self.mongo.connect()
        
        # Lista os clientes existentes para inserir na comanda
        self.relatorio.get_relatorio_clientes()
        cpf = str(input("Digite o número do CPF do Cliente: "))
        cliente = self.valida_cliente(cpf)
        if cliente == None:
            return None

        proxima_comanda = self.mongo.db["comandas"].aggregate([
                                                            {
                                                                '$group': {
                                                                    '_id': '$comandas', 
                                                                    'proxima_comanda': {
                                                                        '$max': '$id_comanda'
                                                                    }
                                                                }
                                                            }, {
                                                                '$project': {
                                                                    'proxima_comanda': {
                                                                        '$sum': [
                                                                            '$proxima_comanda', 1
                                                                        ]
                                                                    }, 
                                                                    '_id': 0
                                                                }
                                                            }
                                                        ])
    
        proxima_comanda = list(proxima_comanda)
        if proxima_comanda:
            proxima_comanda = int(proxima_comanda[0]['proxima_comanda'])
        else:
            proxima_comanda = 1
        
        # Cria um dicionário para mapear as variáveis de entrada e saída
        data = dict(id_comanda=proxima_comanda, data_comanda=self.data_hoje, status_comanda="Aberto",cpf_cliente=cliente.get_CPF())
        
        
        
        # insere e recupera o código da nova comanda
        id_comanda = self.mongo.db["comandas"].insert_one(data)
        
        # Recupera os dados da nova comanda criado transformando em um DataFrame
        df_comanda = self.recupera_comanda(id_comanda.inserted_id)
        # Cria um novo objeto Comanda
        nova_comanda = Comanda(df_comanda.id_comanda.values[0], df_comanda.data_comanda.values[0], df_comanda.status_comanda.values[0], cliente)
        # Exibe os atributos da nova comanda
        print(nova_comanda.to_string())
        # Retorna o objeto nova_comanda para utilização posterior, caso necessário
        return nova_comanda

    def atualizar_status_comanda(self) -> Comanda:
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o código da comanda a ser alterada
        id_comanda = int(input("Código da Comanda que irá alterar: "))        

        # Verifica se a comanda existe na base de dados
        if not self.verifica_existencia_comanda(id_comanda):

            comanda = self.valida_comanda(id_comanda)
            if comanda ==  None:
                return None        
            
            cliente = self.valida_cliente(comanda.get_cliente().get_CPF())
            if cliente == None:
                return None

            # Exibe o satus atual da comanda
            print(f"\nStatus da comanda [{id_comanda}]: {comanda.get_status_comanda()}\n")
            
            print("----------ESCOLHA O OPÇÃO DO STATUS DA COMANDA----------\n")
            # Menu das opções de status da comanda "Aberto", "Em Andamento", "Finalizado", "Pronto"
            status_comanda = int(input(config.STATUS_COMANDA))
            
            # Chama o método de atualizar status da comanda 
            novo_status = comanda.atualizar_status_comanda(status_comanda)
            
            print(f"Novo status: {novo_status}")
            print(f"Cliente: {comanda.get_cliente().get_CPF()}")
            
            
            self.mongo.db["comandas"].update_one({"id_comanda": id_comanda}, 
                                    {"$set": {"status_comanda": novo_status}})

            
            
            # Recupera os dados da nova comanda criado transformando em um DataFrame
            #APAGARdf_comanda = oracle.sqlToDataFrame(f"select * from comandas where id_comanda = {id_comanda}")
            df_comanda = self.recupera_comanda_id(id_comanda)
            
            # Cria um novo objeto comanda
            comanda_atualizado = Comanda(df_comanda.id_comanda.values[0], df_comanda.data_comanda.values[0], df_comanda.status_comanda.values[0], cliente)
            # Exibe os atributos da nova comanda
            print(comanda_atualizado.to_string())
            self.mongo.close()
            # Retorna o objeto comanda_atualizado para utilização posterior, caso necessário
            return comanda_atualizado
        else:
            self.mongo.close()
            print(f"O código {id_comanda} não existe.")
            return None

    def excluir_comanda(self):
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o código do comanda a ser alterado
        id_comanda = int(input("Código do Comanda que irá excluir: "))        

        # Verifica se o comanda existe na base de dados
        if not self.verifica_existencia_comanda(id_comanda):         
            # Recupera os dados da nova comanda criada transformando em um DataFrame
            df_comanda = self.recupera_comanda_id(id_comanda)
            cliente = self.valida_cliente(df_comanda.cpf_cliente.values[0])
            
            from controller.controller_item_comanda import Controller_Item_Comanda
            self.ctrl_item_comanda = Controller_Item_Comanda()

            # Verifica se a comanda existe na base de dados

            opcao_excluir = input(f"Tem certeza que deseja excluir a comanda {id_comanda} [S ou N]: ")
            if opcao_excluir.lower() == "s":
                print("Atenção, caso a comanda possua itens, também serão excluídos!")
                opcao_excluir = input(f"Tem certeza que deseja excluir a comanda {id_comanda} [S ou N]: ")
                if opcao_excluir.lower() == "s":
                    # Remove os itens da comanda
                    self.mongo.db["itens_comanda"].delete_one({"id_comanda": id_comanda})
                    print("Itens da comanda removidos com sucesso!")
                    # Remove a comanda
                    self.mongo.db["comandas"].delete_one({"id_comanda": id_comanda})

                    comanda_excluido = Comanda(df_comanda.id_comanda.values[0], df_comanda.data_comanda.values[0], df_comanda.status_comanda.values[0], cliente)
                    self.mongo.close()

                    # Exibe os atributos da comanda excluído
                    print("Comanda Removida com Sucesso!")
                    print(comanda_excluido.to_string())
        
        else:
            self.mongo.close()
            print(f"O código {id_comanda} não existe.")

    def verifica_existencia_comanda_cliente(self, cpf_cliente:str=None) -> bool:
    # Recupera os dados da nova comanda criada, transformando em um DataFrame
        df_comanda = pd.DataFrame(list(self.mongo.db["comandas"].find({"cpf_cliente": cpf_cliente}, {"id_comanda": 1, "data_comanda": 1, "status_comanda": 1, "cpf_cliente": 1, "_id": 0})))
        return df_comanda.empty

    def verifica_existencia_comanda(self, id_comanda:int=None, external:bool=False) -> bool:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()
            
        # Recupera os dados da nova comanda criado transformando em um DataFrame
        df_comanda = pd.DataFrame(self.mongo.db["comandas"].find({"id_comanda": id_comanda}, {"id_comanda": 1, "data_comanda": 1, "status_comanda": 1, "cpf_cliente": 1,"_id": 0}))

        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return df_comanda.empty
    
    def recupera_comanda(self, _id:ObjectId=None) -> bool:
        # Recupera os dados da nova comanda criada transformando em um DataFrame
        df_comanda = pd.DataFrame(list(self.mongo.db["comandas"].find({"_id":_id}, {"id_comanda": 1, "data_comanda": 1, "status_comanda": 1, "cpf_cliente": 1, "_id": 0})))
        return df_comanda

    def recupera_comanda_id(self, codigo:int=None, external: bool = False) -> bool:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()

        # Recupera os dados da nova comanda criado transformando em um DataFrame
        df_comanda = pd.DataFrame(list(self.mongo.db["comandas"].find({"id_comanda": codigo}, {"id_comanda": 1, "data_comanda": 1, "status_comanda": 1, "cpf_cliente": 1, "_id": 0})))

        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return df_comanda

    def valida_cliente(self, cpf:str=None) -> Cliente:
        if self.ctrl_cliente.verifica_existencia_cliente(cpf=cpf, external=True):
            print(f"O CPF {cpf} informado não existe na base.")
            return None
        else:
            # Recupera os dados do novo cliente criado transformando em um DataFrame
            df_cliente = self.ctrl_cliente.recupera_cliente(cpf=cpf, external=True)
            # Cria um novo objeto cliente
            cliente = Cliente(df_cliente.cpf_cliente.values[0], df_cliente.nome_cliente.values[0] ,df_cliente.telefone_cliente.values[0], df_cliente.email_cliente.values[0])
            return cliente

    def valida_comanda(self, id_comanda:int=None) -> Comanda: 
        if self.verifica_existencia_comanda(id_comanda=id_comanda, external=True):
            print(f"O id comanda {id_comanda} informado não existe na base.")
            return None
        else:
            # Recupera os dados da nova comanda criado transformando em um DataFrame
            df_comanda = self.recupera_comanda_id(id_comanda, external=True)
            # Cria um novo objeto cliente
            cliente = self.valida_cliente(df_comanda.cpf_cliente.values[0])
            
            comanda = Comanda(df_comanda.id_comanda.values[0], df_comanda.data_comanda.values[0], df_comanda.status_comanda.values[0], cliente)
            return comanda
        
    def valida_comanda_cliente(self, cpf_cliente:str=None) -> Comanda:
        if self.verifica_existencia_comanda_cliente(cpf_cliente):
            print(f"\n\nNão existe comanda associada ao cpf {cpf_cliente} na base.\n\n")
            return None
        else:
            # Recupera os dados da nova comanda criada transformando em um DataFrame
            df_comanda = pd.DataFrame(list(self.mongo.db["comandas"].find({"cpf_cliente": cpf_cliente}, {"id_comanda": 1, "data_comanda": 1, "status_comanda": 1, "cpf_cliente": 1, "_id": 0})))
            
            # Cria um novo objeto cliente
            cliente = self.valida_cliente(df_comanda.cpf_cliente.values[0])
            
            # Cria um novo objeto comanda
            comanda = Comanda(df_comanda.id_comanda.values[0], df_comanda.data_comanda.values[0], df_comanda.status_comanda.values[0], cliente)
            return comanda
    
    

        
        
        
    