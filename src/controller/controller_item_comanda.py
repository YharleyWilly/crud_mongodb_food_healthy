import pandas as pd
from bson import ObjectId

from reports.relatorios import Relatorio

from model.itens_comanda import ItemComanda
from model.comandas import Comanda

from controller.controller_comanda import Controller_Comanda
#APAGARfrom conexion.oracle_queries import OracleQueries

from conexion.mongo_queries import MongoQueries

from utils import config

class Controller_Item_Comanda:
    def __init__(self):
 
        self.ctrl_comanda = Controller_Comanda()
        self.mongo = MongoQueries()
        self.relatorio = Relatorio()
        
    def inserir_item_comanda(self) -> ItemComanda:
        ''' Ref.: https://cx-oracle.readthedocs.io/en/latest/user_guide/plsql_execution.html#anonymous-pl-sql-blocks'''
        
        # Cria uma nova conexão com o banco
        self.mongo.connect()
        
        # Lista as comandas existentes para inserir no item de comanda
        #self.listar_comandas(need_connect=True)
        self.relatorio.get_relatorio_comandas()
        
        #Espaçamento
        print("\n")   
        
        id_comanda = int(input("Digite o número da Comanda onde serão inserido os itens: "))
        comanda = self.ctrl_comanda.valida_comanda(id_comanda)
        
        if comanda == None:
            return None

        #Exibe o cardapio
        print(config.MENU_CARDAPIO)
 
        opcao_produto = str(input(f"Informe a opção do produto da comanda {comanda.get_id_comanda()} | Cliente {comanda.cliente.get_nome()}:  "))

        print("\n")
                 
        # A descrição e valor do produto serão definidos de acordo com a opção escolhida pelo usuário.
        opcao = opcao_produto.upper()

        if opcao == '1':
            descricao_produto = "Sanduíche Natural"
            valor_unitario_item = 9.90
            print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

        elif opcao == '2':
            descricao_produto = "Salada de Frutas"
            valor_unitario_item = 6.50
            print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

        elif opcao == '3':
            descricao_produto = "Smoothie de Frutas"
            valor_unitario_item = 7.90
            print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

        elif opcao == '4':
            descricao_produto = "Wrap de Vegetais"
            valor_unitario_item = 8.50
            print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

        elif opcao == '5':
            descricao_produto = "Iogurte com Granola"
            valor_unitario_item = 5.50
            print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

        elif opcao == 'A':
            descricao_produto = "Água Mineral"
            valor_unitario_item = 3.00
            print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

        elif opcao == 'B':
            descricao_produto = "Suco Natural"
            valor_unitario_item = 5.00
            print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

        elif opcao == 'C':
            descricao_produto = "Chá Verde"
            valor_unitario_item = 4.00
            print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

        else:
            print("Opção inválida.")

        
        
        # Solicita a quantidade de itens da comanda selecionada
        quantidade = int(input(f"Informe a quantidade de itens da comanda {comanda.get_id_comanda()} | Cliente {comanda.cliente.get_nome()}: "))
        
        #Espaçamento
        print("\n")   
        
        proximo_item_comanda = self.mongo.db["itens_comanda"].aggregate([
                                                    {
                                                        '$group': {
                                                            '_id': '$itens_comanda', 
                                                            'proximo_item_comanda': {
                                                                '$max': '$id_item_comanda'
                                                            }
                                                        }
                                                    }, {
                                                        '$project': {
                                                            'proximo_item_comanda': {
                                                                '$sum': [
                                                                    '$proximo_item_comanda', 1
                                                                ]
                                                            }, 
                                                            '_id': 0
                                                        }
                                                    }
                                                ])
        
        proximo_item_comanda = list(proximo_item_comanda)
        if proximo_item_comanda:
            proximo_item_comanda = int(proximo_item_comanda[0]['proximo_item_comanda'])
        else:
            proximo_item_comanda = 1
        
        # Cria um dicionário para mapear as variáveis de entrada e saída
        data = dict(id_item_comanda=proximo_item_comanda, qtd_item=quantidade, descricao_produto=descricao_produto,valor_unitario_item=valor_unitario_item, id_comanda=int(comanda.get_id_comanda()))
        
        # Insere e recupera o código do novo item de comanda
        id_item_comanda = self.mongo.db["itens_comanda"].insert_one(data)
        
        # Recupera os dados do novo item de comanda criado transformando em um DataFrame
        df_item_comanda = self.recupera_item_comanda(id_item_comanda.inserted_id)
        # Cria um novo objeto Item de Comanda
        novo_item_comanda = ItemComanda(df_item_comanda.id_item_comanda.values[0], df_item_comanda.qtd_item.values[0], df_item_comanda.descricao_produto.values[0], df_item_comanda.valor_unitario_item.values[0], comanda)
        # Exibe os atributos do novo Item de Comanda
        print(novo_item_comanda.to_string())
        self.mongo.close()
        # Retorna o objeto novo_item_comanda para utilização posterior, caso necessário
        return novo_item_comanda

    def atualizar_item_comanda(self) -> ItemComanda:
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o código do item de comanda a ser alterado
        codigo_item_comanda = int(input("Código do Item de Comanda que irá alterar: "))        

        #Espaçamento
        print("\n")   
        
        # Verifica se o item de comanda existe na base de dados
        if not self.verifica_existencia_item_comanda(codigo_item_comanda):

            # Lista as comanda existentes para atualizar os itens de comanda
            self.relatorio.get_relatorio_comandas()
            id_comanda = int(str(input("Digite o número da Comanda: ")))
            comanda = self.ctrl_comanda.valida_comanda(id_comanda)
            if comanda == None:
                return None
            
            #Espaçamento
            print("\n")   
            
            
                #Exibe o cardapio
            print(config.MENU_CARDAPIO)
            
            opcao_produto = str(input(f"Informe a NOVA opção do produto Item de comanda {codigo_item_comanda} | Cliente {comanda.cliente.get_nome()}:  "))

            print("\n")
            
            # A descrição e valor do produto serão definidos de acordo com a opção escolhida pelo usuário.
            opcao = opcao_produto.upper()

            if opcao == '1':
                descricao_produto = "Sanduíche Natural"
                valor_unitario_item = 9.90
                print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

            elif opcao == '2':
                descricao_produto = "Salada de Frutas"
                valor_unitario_item = 6.50
                print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

            elif opcao == '3':
                descricao_produto = "Smoothie de Frutas"
                valor_unitario_item = 7.90
                print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

            elif opcao == '4':
                descricao_produto = "Wrap de Vegetais"
                valor_unitario_item = 8.50
                print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

            elif opcao == '5':
                descricao_produto = "Iogurte com Granola"
                valor_unitario_item = 5.50
                print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

            elif opcao == 'A':
                descricao_produto = "Água Mineral"
                valor_unitario_item = 3.00
                print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

            elif opcao == 'B':
                descricao_produto = "Suco Natural"
                valor_unitario_item = 5.00
                print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

            elif opcao == 'C':
                descricao_produto = "Chá Verde"
                valor_unitario_item = 4.00
                print(f"Cliente: {comanda.cliente.get_nome()} | Descrição produto: {descricao_produto} | Valor unitario: {valor_unitario_item}")

            else:
                print("Opção inválida.")

            # Solicita a quantidade de itens da comanda para o item de comanda selecionado
            quantidade = int(input(f"Informe a nova quantidade de itens do produto: "))
            
            # Atualiza o item de comanda existente
            self.mongo.db["itens_comanda"].update_one({"id_item_comanda": codigo_item_comanda},
                                                     {"$set": {"qtd_item": quantidade,
                                                               "descricao_produto":  descricao_produto,
                                                               "valor_unitario_item": valor_unitario_item,
                                                               "id_comanda": int(comanda.get_id_comanda())
                                                          }
                                                     })
            
            # Recupera os dados do novo item de comanda criado transformando em um DataFrame
            df_item_comanda = self.recupera_item_comanda_id(codigo_item_comanda)
            # Cria um novo objeto Item de Comanda
            item_comanda_atualizado = ItemComanda(df_item_comanda.id_item_comanda.values[0], df_item_comanda.qtd_item.values[0], df_item_comanda.descricao_produto.values[0], df_item_comanda.valor_unitario_item.values[0], comanda)
            # Exibe os atributos do item de comanda
            print(item_comanda_atualizado.to_string())
            self.mongo.close()
            # Retorna o objeto comanda_atualizado para utilização posterior, caso necessário
            return item_comanda_atualizado
        else:
            self.mongo.close()
            print(f"O código {codigo_item_comanda} não existe.")
            return None

    def excluir_item_comanda(self):
        # Cria uma nova conexão com o banco que permite alteração
        self.mongo.connect()

        # Solicita ao usuário o código do item de comanda a ser alterado
        codigo_item_comanda = int(input("Código do Item de Comanda que irá excluir: "))        

        # Verifica se o item de comanda existe na base de dados
        if not self.verifica_existencia_item_comanda(codigo_item_comanda):            
            # Recupera os dados do novo item de comanda criado transformando em um DataFrame
            df_item_comanda = self.recupera_item_comanda_id(codigo_item_comanda)
            comanda = self.ctrl_comanda.valida_comanda(int(df_item_comanda.id_comanda.values[0]))
                    
            opcao_excluir = input(f"Tem certeza que deseja excluir o item de comanda {codigo_item_comanda} [S ou N]: ")
            
            if opcao_excluir.lower() == "s":
                # Revome o item de comanda da tabela
                
                self.mongo.db["itens_comanda"].delete_one({"id_item_comanda": codigo_item_comanda})

                                
                # Cria um novo objeto Item de Comanda para informar que foi removido
                item_comanda_excluido = ItemComanda(df_item_comanda.id_item_comanda.values[0], df_item_comanda.qtd_item.values[0], df_item_comanda.descricao_produto.values[0], df_item_comanda.valor_unitario_item.values[0], comanda)
                self.mongo.close()
                # Exibe os atributos do produto excluído
                print("Item da Comanda Removido com Sucesso!")
                print(item_comanda_excluido.to_string())
        else:
            self.mongo.close()
            print(f"O código {codigo_item_comanda} não existe.")
            
    
    def verifica_existencia_item_comanda(self, id_item_comanda:int=None, external:bool=False) -> bool:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()
            
        # Recupera os dados da nova comanda criado transformando em um DataFrame
        df_item_comanda = pd.DataFrame(self.mongo.db["itens_comanda"].find({"id_item_comanda": id_item_comanda}, {"id_item_comanda": 1, "qtd_item": 1, "descricao_produto": 1, "valor_unitario_item": 1, "id_comanda" :1,"_id": 0}))

        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return df_item_comanda.empty
    
    def recupera_item_comanda(self, _id:ObjectId=None) -> bool:
        # Recupera os dados do novo item comanda criado transformando em um DataFrame
        df_item_comanda = pd.DataFrame(list(self.mongo.db["itens_comanda"].find({"_id": _id}, {"id_item_comanda":1, "qtd_item": 1, "descricao_produto": 1, "valor_unitario_item": 1, "id_comanda": 1, "_id": 0})))
        return df_item_comanda
    
    def recupera_item_comanda_id(self, codigo:int=None, external:bool=False) -> bool:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()
            
        # Recupera os dados do novo item comanda criado transformando em um DataFrame
        df_item_comanda = pd.DataFrame(self.mongo.db["itens_comanda"].find({"id_item_comanda": codigo}, {"id_item_comanda": 1, "qtd_item": 1, "descricao_produto": 1, "valor_unitario_item": 1, "id_comanda": 1, "_id": 0}))
        
        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()
        
        return df_item_comanda

        
    def valida_item_comanda(self, id_item_comanda:int=None) -> ItemComanda:
        if self.verifica_existencia_item_comanda(id_item_comanda, external=True):
            print(f"\n\nO Item de comanda {id_item_comanda} informado não existe na base.\n\n")
            return None
        else:
            
            # Recupera os dados do novo item de comanda criado transformando em um DataFrame
            df_item_comanda = self.recupera_item_comanda_id(id_item_comanda, external=True)
            
            # Cria um novo objeto comanda
            comanda = self.ctrl_comanda.valida_comanda(df_item_comanda.id_comanda.values[0])
                  
            itensComanda = ItemComanda(df_item_comanda.id_item_comanda.values[0], df_item_comanda.qtd_item.values[0], df_item_comanda.descricao_produto.values[0], df_item_comanda.valor_unitario_item.values[0], comanda)    
            return itensComanda
       
        
        