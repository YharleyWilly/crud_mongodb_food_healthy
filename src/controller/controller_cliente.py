import pandas as pd
from model.clientes import Cliente
from model.comandas import Comanda
from model.itens_comanda import ItemComanda
#APAGARfrom conexion.oracle_queries import OracleQueries
from conexion.mongo_queries import MongoQueries

class Controller_Cliente:
    
    def __init__(self):
        pass
        self.mongo = MongoQueries()
    
    def inserir_cliente(self) -> Cliente:
        ''' Ref.: https://cx-oracle.readthedocs.io/en/latest/user_guide/plsql_execution.html#anonymous-pl-sql-blocks'''
        
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuario o novo CPF
        cpf = input("CPF (Novo): ")

        #Se cpf do cliente não existe na tablea CLIENTES
        if self.verifica_existencia_cliente(cpf):
            
            # Solicita ao usuario o novo nome
            nome = input("Nome (Novo): ")
            # Solicita ao usuario o novo telefone
            telefone = input("Telefone (Novo): ")
            # Solicita ao usuario o novo email
            email = input("Email (Novo): ")
            
            # Insere e persiste o novo cliente
            self.mongo.db["clientes"].insert_one({"cpf_cliente": cpf, "nome_cliente": nome, "telefone_cliente": telefone, "email_cliente": email})
            
            # Recupera os dados do novo cliente criado transformando em um DataFrame
            df_cliente = self.recupera_cliente(cpf)
            # Cria um novo objeto Cliente
            novo_cliente = Cliente(df_cliente.cpf_cliente.values[0], df_cliente.nome_cliente.values[0], df_cliente.telefone_cliente.values[0], df_cliente.email_cliente.values[0])
            # Exibe os atributos do novo cliente
            print(novo_cliente.to_string())
            self.mongo.close()
            # Retorna o objeto novo_cliente para utilização posterior, caso necessário
            return novo_cliente
        else:
            self.mongo.close()
            print(f"O CPF {cpf} já está cadastrado.")
            return None

    def atualizar_cliente(self) -> Cliente:
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o código do cliente a ser alterado
        cpf = int(input("CPF do cliente que deseja alterar o nome: "))

        # Verifica se o cliente existe na base de dados
        if not self.verifica_existencia_cliente(cpf):
            # Solicita a nova descrição do cliente
            
            # Solicita o novo nome
            novo_nome = input("Nome (Novo): ")
            # Solicita o novo telefone
            novo_telefone = input("Telefone (Novo): ")
            # Solicita o novo email
            novo_email = input("Email (Novo): ")
            
            # Atualiza os dados do cliente existente no banco de dados
            self.mongo.db["clientes"].update_one({"cpf_cliente": f"{cpf}"}, {"$set": {"nome_cliente": novo_nome, "telefone_cliente": novo_telefone, "email_cliente": novo_email}})
            
            
            # Recupera os dados do novo cliente criado transformando em um DataFrame
            df_cliente = self.recupera_cliente(cpf)
            # Cria um novo objeto cliente
            cliente_atualizado = Cliente(df_cliente.cpf_cliente.values[0], df_cliente.nome_cliente.values[0], df_cliente.telefone_cliente.values[0], df_cliente.email_cliente.values[0])
            # Exibe os atributos do novo cliente
            print(cliente_atualizado.to_string())
            self.mongo.close()
            # Retorna o objeto cliente_atualizado para utilização posterior, caso necessário
            return cliente_atualizado
        else:
            self.mongo.close()
            print(f"O CPF {cpf} não existe.")
            return None

    def excluir_cliente(self):
        from controller.controller_comanda import Controller_Comanda
        from controller.controller_item_comanda import Controller_Item_Comanda

        self.ctrl_item_comanda = Controller_Item_Comanda()
        self.ctrl_comanda = Controller_Comanda()

        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o CPF do Cliente a ser alterado
        cpf = int(input("CPF do Cliente que irá excluir: "))        

        # Verifica se o cliente existe na base de dados
        if not self.verifica_existencia_cliente(cpf):            
            # Recupera os dados do novo cliente criado transformando em um DataFrame
            df_cliente = self.recupera_cliente(cpf)
            # Revome o cliente da tabela
            self.mongo.db["clientes"].delete_one({"cpf_cliente":f"{cpf}"})

            # Recupera as comandas associadas a este cliente
            comandas = self.mongo.db["comandas"].find({"cpf_cliente":f"{cpf}"})

            # Para cada comanda, remove os itens de comanda associados
            for comanda in comandas:
                self.mongo.db["itens_comanda"].delete_many({"id_comanda": comanda["id_comanda"]})

            # Remove as comandas associadas a este cliente
            self.mongo.db["comandas"].delete_many({"cpf_cliente":f"{cpf}"})

            # Cria um novo objeto Cliente para informar que foi removido
            cliente_excluido = Cliente(df_cliente.cpf_cliente.values[0], df_cliente.nome_cliente.values[0], df_cliente.telefone_cliente.values[0], df_cliente.email_cliente.values[0])
            self.mongo.close()
            # Exibe os atributos do cliente excluído
            print("Cliente Removido com Sucesso!")
            print(cliente_excluido.to_string())
        else:
            self.mongo.close()
            print(f"O CPF {cpf} não existe.")

        '''
        # Verifica se o cliente existe na base de dados
        if not self.verifica_existencia_cliente(cpf):            
            # Recupera os dados do novo cliente criado transformando em um DataFrame
            df_cliente = self.recupera_cliente(cpf)
            
            comanda_cliente = self.ctrl_comanda.valida_comanda_cliente(cpf)
            
            # Se comanda é vazia pode excluir diretamente o cliente, pois não existe itens sem uma comanda criada
            if comanda_cliente == None:

                # Revome o cliente da tabela
                self.mongo.db["clientes"].delete_one({"cpf_cliente":f"{cpf}"})            
                # Cria um novo objeto Cliente para informar que foi removido
                cliente_excluido = Cliente(df_cliente.cpf_cliente.values[0], df_cliente.nome_cliente.values[0], df_cliente.telefone_cliente.values[0], df_cliente.email_cliente.values[0])
                self.mongo.close()
                # Exibe os atributos do cliente excluído
                print("Cliente Removido com Sucesso!")
                print(cliente_excluido.to_string())
            
            # Se a comanda existe    
            else:
                
                # Valida existencia item comanda associada a comanda e retorna o objeto
                item_comanda = self.ctrl_item_comanda.valida_item_comanda_comanda(comanda_cliente.get_id_comanda())
                
                #Se não existe item comanda exclui comanda depois o cliente
                if item_comanda == None:
                    
                    # Revome o cliente da tabela
                    self.mongo.db["comandas"].delete_one({"cpf_cliente": f"{cpf}"})
                    self.mongo.db["clientes"].delete_one({"cpf_cliente": f"{cpf}"})          
                    # Cria um novo objeto Cliente para informar que foi removido
                    cliente_excluido = Cliente(df_cliente.cpf_cliente.values[0], df_cliente.nome_cliente.values[0], df_cliente.telefone_cliente.values[0], df_cliente.email_cliente.values[0])
                    self.mongo.close()
                    # Exibe os atributos do cliente excluído
                    print("Cliente Removido com Sucesso!")
                    print(cliente_excluido.to_string())
                
                # Se existe comanda e item comanda associada a mesma
                else:
                    
                    self.mongo.db["itens_comanda"].delete_one({"id_comanda": f"{comanda_cliente.get_id_comanda()}"})
                    self.mongo.db["comandas"].delete_one({"cpf_cliente": f"{cpf}"})
                    self.mongo.db["clientes"].delete_one({"cpf_cliente": f"{cpf}"})

                    # Cria um novo objeto Cliente para informar que foi removido
                    cliente_excluido = Cliente(df_cliente.cpf_cliente.values[0], df_cliente.nome_cliente.values[0], df_cliente.telefone_cliente.values[0], df_cliente.email_cliente.values[0])
                    self.mongo.close()
                    # Exibe os atributos do cliente excluído
                    print("Cliente Removido com Sucesso!")
                    print(cliente_excluido.to_string())
             


            #VERIFICAR SE EXISTE COMANDA COM CPF DO CLIENTE
            
        else:
            self.mongo.close()
            print(f"O CPF {cpf} não existe.")
        '''

    def verifica_existencia_cliente(self, cpf:str=None, external:bool=False) -> bool:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()

        # Recupera os dados do novo cliente criado transformando em um DataFrame
        df_cliente = pd.DataFrame(self.mongo.db["clientes"].find({"cpf_cliente":f"{cpf}"}, {"cpf_cliente": 1, "nome_cliente": 1, "telefone_cliente": 1, "email_cliente": 1, "_id": 0}))

        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return df_cliente.empty

    def recupera_cliente(self, cpf:str=None, external:bool=False) -> pd.DataFrame:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()

        # Recupera os dados do novo cliente criado transformando em um DataFrame
        df_cliente = pd.DataFrame(list(self.mongo.db["clientes"].find({"cpf_cliente":f"{cpf}"}, {"cpf_cliente": 1, "nome_cliente": 1, "telefone_cliente": 1, "email_cliente": 1, "_id": 0})))
        
        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return df_cliente    