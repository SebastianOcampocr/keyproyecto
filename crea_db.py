# Hecho por Keylan, fecha 8/3/2024
import sqlite3

conn = sqlite3.connect('inventario.db')  # Conectamos a la base de datos 'inventario.db'
cursor = conn.cursor()

# Crear tablas
cursor.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    categoría_id INTEGER,
    precio REAL,
    cantidad INTEGER,
    proveedor_id INTEGER
)
''')  # Creamos la tabla 'productos' si no existe

cursor.execute('''
CREATE TABLE IF NOT EXISTS categorías (
    id INTEGER PRIMARY KEY,
    nombre TEXT
)
''')  # Creamos la tabla 'categorías' si no existe

cursor.execute('''
CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    contacto TEXT
)
''')  # Creamos la tabla 'proveedores' si no existe

# Se crea la tabla de ventas
cursor.execute('''
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY,
    producto_id INTEGER,
    cantidad INTEGER,
    fecha TEXT,
    total REAL,
    FOREIGN KEY (producto_id) REFERENCES productos (id)
)
''')  # Creamos la tabla 'ventas' si no existe

# Insertar categorías
categorias = [
    ("Bebidas",),
    ("Lácteos",),
    ("Enlatados",),
    ("Snacks",),
    ("Congelados",),
    ("Productos Frescos",),
    ("Cereales",),
    ("Fideos",),
]  # Lista de categorías para insertar

cursor.executemany("INSERT INTO categorías (nombre) VALUES (?)", categorias)  # Insertamos categorías

# Insertar proveedores
proveedores = [
    ("Dos Pinos", "contacto@dospinos.com"),
    ("Pura Vida", "contacto@puravida.com"),
    ("Tico Fruta", "contacto@ticofruta.com"),
    ("Supermercado Automercado", "contacto@automercado.com"),
    ("Café Britt", "contacto@cafebritt.com"),
    ("Coca-Cola Femsa S.A.", "contacto@femsa.com"),
]  # Lista de proveedores para insertar

cursor.executemany("INSERT INTO proveedores (nombre, contacto) VALUES (?, ?)", proveedores)  # Insertamos proveedores

# Inserta datos de prueba en ventas (opcional)
ventas = [
    (1, 5, '2024-08-03', 500.00),  # producto_id, cantidad, fecha, total
    (2, 3, '2024-08-03', 300.00),
]  # Lista de ventas de prueba para insertar

cursor.executemany("INSERT INTO ventas (producto_id, cantidad, fecha, total) VALUES (?, ?, ?, ?)", ventas)  # Insertamos ventas

conn.commit()  # Guardamos los cambios en la base de datos
conn.close()  # Cerramos la conexión a la base de datos
