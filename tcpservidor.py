# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 10:21:23 2023

@author: jgvm
"""

import socket
import threading
import hashlib
import os
import logging

# Configuración del servidor
HOST = '0.0.0.0'
PORT = 8000
MAX_CONNECTIONS = 25
FILES_DIRECTORY = '/archivos'
LOGS_DIRECTORY = '/logs'

# Configuración del registro
logging.basicConfig(filename=f'{LOGS_DIRECTORY}/server.log', level=logging.INFO)

# Función para manejar cada conexión entrante
def handle_connection(client_socket, file_path, num_clients):
    try:
        # Esperar a que todos los clientes estén listos
        clients_ready = 0
        while clients_ready < num_clients:
            data = client_socket.recv(1024)
            if not data:
                break
            if data.decode('utf-8') == 'ready':
                clients_ready += 1

        # Calcular el hash del archivo
        hash_value = hashlib.sha256()
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                hash_value.update(data)

        # Enviar el hash al cliente
        client_socket.send(hash_value.digest())

        # Enviar el archivo al cliente
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                client_socket.send(data)
    except Exception as e:
        logging.error(f'Error en la conexión: {str(e)}')
    finally:
        client_socket.close()

# Función principal del servidor
def run_server():
    try:
        # Crear un socket de servidor TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CONNECTIONS)
        logging.info(f'Servidor iniciado en {HOST}:{PORT}')

        # Esperar conexiones entrantes
        while True:
            client_socket, address = server_socket.accept()
            logging.info(f'Nueva conexión desde {address[0]}:{address[1]}')

            # Seleccionar archivo y número de clientes
            file_name = input('Ingrese el nombre del archivo a enviar (100MB o 250MB): ')
            num_clients = int(input('Ingrese el número de clientes: '))

            # Validar archivo y número de clientes
            if file_name == '100MB':
                file_path = os.path.join(FILES_DIRECTORY, '100MB.zip')
            elif file_name == '250MB':
                file_path = os.path.join(FILES_DIRECTORY, '250MB.zip')
            else:
                logging.error('Archivo no válido')
                client_socket.close()
                continue
            if num_clients < 1 or num_clients > MAX_CONNECTIONS:
                logging.error('Número de clientes no válido')
                client_socket.close()
                continue

            # Crear un subproceso para manejar la conexión
            connection_thread = threading.Thread(target=handle_connection, args=(client_socket, file_path, num_clients))
            connection_thread.start()
    except Exception as e:
        logging.error(f'Error en el servidor: {str(e)}')
    finally:
        server_socket.close()

# Ejecutar el servidor
if __name__ == '__main__':
    run_server()
