# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1P4", echo=False, execution_options={"autocommit":False})

def dbConnect():
    return db_engine.connect()

def dbCloseConnect(db_conn):
    db_conn.close()

def getListaCliMes(db_conn, mes, anio, iumbral, iintervalo, use_prepare, break0, niter):

    # TODO: implementar la consulta; asignar nombre 'cc' al contador resultante
    consulta = " SELECT COUNT(DISTINCT customerid) AS cc FROM orders WHERE date_part('year', orderdate) = " + anio + " AND date_part('month', orderdate) = " + mes + " AND totalamount > "

    # TODO: ejecutar la consulta
    # - mediante PREPARE, EXECUTE, DEALLOCATE si use_prepare es True
    # - mediante db_conn.execute() si es False

    # Array con resultados de la consulta para cada umbral
    dbr=[]

    for ii in range(niter):

        query = consulta + str(iumbral) + "; "

        # TODO: ...
        if use_prepare == True:
            db_conn.execute("PREPARE query AS " + query)
            res = db_conn.execute("EXECUTE query;").first()
            db_conn.execute("DEALLOCATE query;")

        else:
            res = db_conn.execute(query).first()

        # Guardar resultado de la query
        dbr.append({"umbral":iumbral,"contador":res['cc']})

        # TODO: si break0 es True, salir si contador resultante es cero
        if res['cc'] == 0:
            break

        # Actualizacion de umbral
        iumbral = iumbral + iintervalo

    return dbr

def getMovies(anio):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select movietitle from imdb_movies where year = '" + anio + "'"
    resultproxy=db_conn.execute(query)

    a = []
    for rowproxy in resultproxy:
        d={}
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for tup in rowproxy.items():
            # build up the dictionary
            d[tup[0]] = tup[1]
        a.append(d)

    resultproxy.close()

    db_conn.close()

    return a

def getCustomer(username, password):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select * from customers where username='" + username + "' and password='" + password + "'"
    res=db_conn.execute(query).first()

    db_conn.close()

    if res is None:
        return None
    else:
        return {'firstname': res['firstname'], 'lastname': res['lastname']}

def delCustomer(customerid, bFallo, bSQL, duerme, bCommit):
    db_conn = db_engine.connect()

    # Array de trazas a mostrar en la página
    dbr=[]

    try:
        # Ejecutar consultas
        db_conn.execute('BEGIN;')
        dbr.append('Iniciamos una transacción')

        query = 'DELETE FROM orderdetail WHERE orderid IN (SELECT orderid FROM orders WHERE customerid={})'.format(customerid)
        dbr.append('Intentamos borrar los detalles de todos los pedidos y el carrito del usuario')
        db_conn.execute(query)
        dbr.append('Borramos los detalles de todos los pedidos y el carrito del usuario')

        if not bFallo:
            time.sleep(duerme)

            query = 'DELETE FROM orders WHERE customerid={}'.format(customerid)
            dbr.append('Intentamos borrar los pedidos y el carrito del usuario')
            db_conn.execute(query)
            dbr.append('Borramos los pedidos y el carrito del usuario')

            query = 'DELETE FROM customers WHERE customerid={}'.format(customerid)
            dbr.append('Intentamos borrar el usuario')
            db_conn.execute(query)
            dbr.append('Borramos el usuario')

        else:
            if bCommit:
                # Hacemos un commit intermedio antes del error, y otro begin
                dbr.append('Hacemos un commit intermedio')
                db_conn.execute('COMMIT;')
                db_conn.execute('BEGIN;')
                dbr.append('Iniciamos otra transacción')

            query = 'DELETE FROM customers WHERE customerid={}'.format(customerid)
            dbr.append('Intentamos borrar el usuario')
            db_conn.execute(query)
            dbr.append('Borramos el usuario')

            query = 'DELETE FROM orders WHERE customerid={}'.format(customerid)
            dbr.append('Intentamos borrar los pedidos y el carrito del usuario')
            db_conn.execute(query)
            dbr.append('Borramos los pedidos y el carrito del usuario')

    except Exception as e:
        # Deshacer en caso de error
        dbr.append('Ha habido un error, hacemos Rollback')
        db_conn.execute('ROLLBACK;')

    else:
        # Confirmar cambios si todo va bien
        dbr.append('Hacemos commit de la transacción')
        db_conn.execute('COMMIT;')

    return dbr
