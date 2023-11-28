from conexion.mongo_queries import MongoQueries
import os
import pandas as pd
from pymongo import ASCENDING, DESCENDING
from controller.controller_cliente import Controller_Cliente

class Relatorio:
    def __init__(self):
        
        self.ctrl_cliente = Controller_Cliente()
    
        """
        #Relatorio clientes
        self.query_relatorio_clientes = '''    
            select c.cpf_cliente
            , c.nome_cliente
            , c.telefone_cliente
            , c.email_cliente
            from clientes c
            order by c.cpf_cliente 
        '''
        #Relatorio comandas de todos os clientes
        self.query_relatorio_comandas = '''
            SELECT co.ID_COMANDA,
            i.ID_ITEM_COMANDA as item_comanda,
            c.CPF_CLIENTE,
            c.NOME_CLIENTE as cliente,
            co.DATA_COMANDA,
            co.STATUS_COMANDA,
            i.DESCRICAO_PRODUTO as produto,
            i.QTD_ITEM as quantidade,
            i.VALOR_UNITARIO_ITEM as valor_unitario,
            (i.QTD_ITEM * i.VALOR_UNITARIO_ITEM) as valor_total
            FROM LABDATABASE.CLIENTES c
            INNER JOIN LABDATABASE.COMANDAS co ON c.CPF_CLIENTE = co.CPF_CLIENTE
            LEFT JOIN LABDATABASE.ITENS_COMANDA i ON co.ID_COMANDA = i.ID_COMANDA
            ORDER BY c.NOME_CLIENTE, i.ID_ITEM_COMANDA
        '''
        #Relatorio itens comanda de todos os clientes
        self.query_relatorio_itens_comanda = ''' 
            select i.id_comanda
            , i.id_item_comanda
            , i.descricao_produto
            , i.qtd_item
            , i.valor_unitario_item
            , (i.qtd_item * i.valor_unitario_item) as valor_total
            from itens_comanda i
            order by i.id_comanda
        '''       
        """
        
    def get_relatorio_comandas_cliente(self, cpf_cliente):
        
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        
        # Verifica se o cliente existe na base de dados
        cliente = mongo.db["clientes"].find_one({"cpf_cliente": cpf_cliente})
        
        if cliente is None:
            print("Cliente não encontrado")
            return

        # Recupera os dados das comandas
        query_result_comandas = mongo.db["comandas"].find({"cpf_cliente": cpf_cliente}, 
                                                        {"id_comanda": 1, 
                                                        "data_comanda": 1,
                                                        "status_comanda": 1,
                                                        "cpf_cliente": 1, 
                                                        "_id": 0
                                                        }).sort("id_comanda", ASCENDING)
        df_comandas = pd.DataFrame(list(query_result_comandas))

        # Recupera os dados dos itens das comandas
        query_result_itens = mongo.db["itens_comanda"].find({}, 
                                                            {"id_item_comanda": 1, 
                                                            "qtd_item": 1,
                                                            "descricao_produto": 1,
                                                            "valor_unitario_item": 1, 
                                                            "id_comanda": 1,
                                                            "_id": 0
                                                            }).sort("id_item_comanda", ASCENDING)
        df_itens = pd.DataFrame(list(query_result_itens))

        # Fecha a conexão com o mongo
        mongo.close()

        # Verifica se df_itens está vazio
        if df_itens.empty:
            print(df_comandas)
        else:
            # Junta os dois DataFrames usando o campo 'id_comanda'
            df = pd.merge(df_comandas, df_itens, on='id_comanda')

            # Calcula o valor total para cada item
            df['valor_total'] = df['qtd_item'] * df['valor_unitario_item']

            # Exibe o resultado
            print(df)

        input("Pressione Enter para Sair do Relatório de Comandas")



    def get_relatorio_clientes(self):
        # Cria uma nova conexão com o banco que permite alteração
  
        mongo = MongoQueries()
        mongo.connect()
        
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["clientes"].find({}, 
                                                 {"cpf_cliente": 1, 
                                                  "nome_cliente": 1,
                                                  "telefone_cliente": 1,
                                                  "email_cliente": 1, 
                                                  "_id": 0
                                                 }).sort("nome_cliente", ASCENDING)
        df_cliente = pd.DataFrame(list(query_result))
        # Fecha a conexão com o mongo
        mongo.close()
        # Exibe o resultado
        print(df_cliente)
        input("Pressione Enter para Sair do Relatório de Clientes")
        
    '''
    def get_relatorio_comandas(self):
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()
        
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["comandas"].aggregate([
            {
                '$lookup': {
                    'from': 'clientes', 
                    'localField': 'cpf_cliente', 
                    'foreignField': 'cpf_cliente', 
                    'as': 'cliente'
                }
            }, 
            {
                '$unwind': {
                    'path': '$cliente'
                }
            }, 
            {
                '$lookup': {
                    'from': 'itens_comanda', 
                    'localField': 'id_comanda', 
                    'foreignField': 'id_comanda', 
                    'as': 'itens'
                }
            }, 
            {
                '$unwind': {
                    'path': '$itens'
                }
            }, 
            {
                '$project': {
                    'id_comanda': 1, 
                    'item_comanda': '$itens.id_item_comanda',
                    'cpf_cliente': 1,
                    'cliente': '$cliente.nome_cliente',
                    'data_comanda': 1,
                    'status_comanda': 1,
                    'produto': '$itens.descricao_produto',
                    'quantidade': '$itens.qtd_item',
                    'valor_unitario': '$itens.valor_unitario_item',
                    'valor_total': { '$multiply': [ "$itens.qtd_item", "$itens.valor_unitario_item" ] },
                    '_id': 0
                }
            },
            {
                '$sort': { 'cliente': 1, 'item_comanda': 1 }
            }
        ])
        
        # Transforma o resultado em um DataFrame e exibe
        df_comandas = pd.DataFrame(list(query_result))
        
        # Fecha a conexão com o mongo
        mongo.close()
        
        columns = ["id_comanda", "item_comanda", "cpf_cliente", "cliente", "data_comanda", "status_comanda", "produto", "quantidade", "valor_unitario", "valor_total"]
        existing_columns = [col for col in columns if col in df_comandas.columns]
        print(df_comandas[existing_columns])
        
        input("Pressione Enter para Sair do Relatório de Comandas")
    '''
    
    def get_relatorio_comandas(self):
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()

        # Recupera os dados das comandas
        query_result_comandas = mongo.db["comandas"].find({}, 
                                                        {"id_comanda": 1, 
                                                        "data_comanda": 1,
                                                        "status_comanda": 1,
                                                        "cpf_cliente": 1, 
                                                        "_id": 0
                                                        }).sort("id_comanda", ASCENDING)
        df_comandas = pd.DataFrame(list(query_result_comandas))

        # Recupera os dados dos itens das comandas
        query_result_itens = mongo.db["itens_comanda"].find({}, 
                                                            {"id_item_comanda": 1, 
                                                            "qtd_item": 1,
                                                            "descricao_produto": 1,
                                                            "valor_unitario_item": 1, 
                                                            "id_comanda": 1,
                                                            "_id": 0
                                                            }).sort("id_item_comanda", ASCENDING)
        df_itens = pd.DataFrame(list(query_result_itens))

        # Fecha a conexão com o mongo
        mongo.close()

        # Verifica se df_itens está vazio
        if df_itens.empty:
            print(df_comandas)
        else:
            # Junta os dois DataFrames usando o campo 'id_comanda'
            df = pd.merge(df_comandas, df_itens, on='id_comanda')

            # Calcula o valor total para cada item
            df['valor_total'] = df['qtd_item'] * df['valor_unitario_item']

            # Exibe o resultado
            print(df)

        input("Pressione Enter para Sair do Relatório de Comandas")

    def get_relatorio_itens_comanda(self):
        # Cria uma nova conexão com o banco
        mongo = MongoQueries()
        mongo.connect()

        # Recupera os dados dos itens das comandas
        query_result_itens = mongo.db["itens_comanda"].find({}, 
                                                            {"id_item_comanda": 1, 
                                                            "qtd_item": 1,
                                                            "descricao_produto": 1,
                                                            "valor_unitario_item": 1, 
                                                            "id_comanda": 1,
                                                            "_id": 0
                                                            }).sort("id_item_comanda", ASCENDING)
        df_itens = pd.DataFrame(list(query_result_itens))

        # Recupera os dados das comandas
        query_result_comandas = mongo.db["comandas"].find({}, 
                                                        {"id_comanda": 1, 
                                                        "data_comanda": 1,
                                                        "status_comanda": 1,
                                                        "cpf_cliente": 1, 
                                                        "_id": 0
                                                        }).sort("id_comanda", ASCENDING)
        df_comandas = pd.DataFrame(list(query_result_comandas))

        # Verifica se df_itens está vazio
        if df_itens.empty:
            print(df_comandas)
        else:
            # Junta os dois DataFrames usando o campo 'id_comanda'
            df = pd.merge(df_comandas, df_itens, on='id_comanda')

            # Calcula o valor total para cada item
            df['valor_total'] = df['qtd_item'] * df['valor_unitario_item']

            # Exibe o resultado
            print(df)

        input("Pressione Enter para Sair do Relatório de Comandas")

    
    
