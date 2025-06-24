import psycopg2
from time import sleep


def mn():
    print('CONECTANDO AO BANCO DE DADOS', end='')
    for _ in range(4):
        print('.', end='')
        sleep(0.2)
    print()


def conectar(database, host, user, password):
    _conexao = False
    mn()
    try:
        cnx = psycopg2.connect(
            database=f'{database}',
            host=f'{host}',
            user=f'{user}',
            password=f'{password}'
        )
        _conexao = True
    except psycopg2.Error as e:
        print('\033[31mErro na Conexão com o Banco de Dados:\033[m', end=' ')
        print(f'{e}')

    finally:
        if _conexao is True:
            print(f'\033[31mConectado com sucesso\033[m')
            return cnx
        else:
            raise e


def listar(cnx):
    try:
        with cnx.cursor() as cursor:
            cursor.execute('SELECT * FROM produtos')
            produtos = cursor.fetchall()

        if len(produtos) > 0:
            for p in produtos:
                print(f'ID - {p[0]}')
                print(f'Nome - {p[1]}')
                print(f'Preco - {p[2]}')
                print(f'Estoque - {p[3]}')
                print('_')
        else:
            print('Nenhum produto para ser Listado!')
    except psycopg2.Error as e:
        print(f'Erro na conexao - {e}')
    finally:
        cnx.close()


def inserir(cnx, v1, v2, v3):
    try:
        with cnx.cursor() as cursor:
            query = 'INSERT INTO produtos(nome, preco, estoque) VALUES(%s,%s,%s)'
            cursor.execute(query, (v1, v2, v3))
            cnx.commit()

        if cursor.rowcount == 1:
            print(f'Produto {v1} adicionado com sucesso!')
        else:
            print('Nao foi possivel inserir o produto!')

    except psycopg2.Error as e:
        print(f'Erro ao inserir no Banco de Dados - {e}')
        cnx.rollback()

    except ValueError as v:
        print(f'Erro nos valores - {v}')
        cnx.rollback()

    finally:
        cnx.close()


def atualizar(cnx):
    try:
        nv_nome = str(input('Novo Produto -> '))
        nv_preco = input('Novo Preco -> ')
        nv_estoque = int(input('Quantidade em Estoque -> '))
        id_produto = int(input('Id Produto ->'))

        with cnx.cursor() as cursor:
            query = 'UPDATE produtos SET nome = %s, preco = %s, estoque = %s WHERE id = %s'
            cursor.execute(query, (nv_nome, nv_preco, nv_estoque, id_produto))
            cnx.commit()

        if cursor.rowcount == 1:
            print(f'Produto {nv_nome} atualizado!')
        else:
            print('Nao foi possivel inserir o Produto!')
            cnx.rollback()

    except psycopg2.Error as e:
        print(f'Erro ao atualizar o Banco de Dados! - {e}')
        cnx.rollback()

    except ValueError as v:
        print(f'Erro nos valores inseridos - {v}')
        cnx.rollback()

    finally:
        cnx.close()


def deletar(cnx, id):
    try:
        with cnx.cursor() as cursor:
            query = 'DELETE FROM produtos WHERE id = %s'
            cursor.execute(query, (id))
            cnx.commit()

            if cursor.rowcount == 1:
                print(f'Produto com id: {id} foi removido da Tabela!')
            else:
                print(f'Erro ao apagar, ID nao encontrado!')

    except psycopg2.Error as e:
        print(f'Erro ao apagar tabela - {e}')
        cnx.rollback()

    except Exception as e:
        print(f"\033[31mErro inesperado:\033[m {e}")
        cnx.rollback()

    finally:
        cnx.close()
