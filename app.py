# Hecho por Keylan, fecha 8/3/2024

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from datetime import datetime

app = FastAPI()  # Aquí iniciamos nuestra aplicación FastAPI
templates = Jinja2Templates(directory=".")  # Configuramos la carpeta donde están las plantillas HTML

def connect_db():
    # Función que abre una conexión con la base de datos
    return sqlite3.connect('inventario.db')

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    conn = connect_db()  # Conectamos a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()  # Obtenemos todos los productos
    
    # Cargar categorías y proveedores
    cursor.execute("SELECT * FROM categorías")
    categorias = cursor.fetchall()
    
    cursor.execute("SELECT * FROM proveedores")
    proveedores = cursor.fetchall()
    
    conn.close()  # Cerramos la conexión a la base de datos
    return templates.TemplateResponse("producto.html", {
        "request": request,
        "productos": productos,
        "categorias": categorias,
        "proveedores": proveedores
    })

@app.get("/ventas", response_class=HTMLResponse)
async def listar_ventas(request: Request):
    conn = connect_db()  # Conectamos a la base de datos
    cursor = conn.cursor()
    
    # Obtener las ventas junto con los nombres de los productos
    cursor.execute("SELECT v.id, p.nombre, v.cantidad, v.fecha, v.total FROM ventas v JOIN productos p ON v.producto_id = p.id")
    ventas = cursor.fetchall()  # Obtenemos todas las ventas
    
    conn.close()  # Cerramos la conexión a la base de datos
    return templates.TemplateResponse("Sales.html", {
        "request": request,
        "ventas": ventas
    })

@app.get("/proveedores", response_class=HTMLResponse)
async def listar_proveedores(request: Request):
    conn = connect_db()  # Conectamos a la base de datos
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM proveedores")
    proveedores = cursor.fetchall()  # Obtenemos todos los proveedores
    
    conn.close()  # Cerramos la conexión a la base de datos
    return templates.TemplateResponse("Supplier.html", {
        "request": request,
        "proveedores": proveedores
    })

@app.post("/agregar_proveedor")
async def agregar_proveedor(
    request: Request,
    nombre: str = Form(...),
    contacto: str = Form(...)
):
    conn = connect_db()  # Conectamos a la base de datos
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO proveedores (nombre, contacto) VALUES (?, ?)",
        (nombre, contacto)  # Agregamos un nuevo proveedor
    )
    conn.commit()  # Guardamos los cambios en la base de datos
    conn.close()  # Cerramos la conexión a la base de datos
    return RedirectResponse(url='/proveedores', status_code=303)  # Redireccionamos a la lista de proveedores

@app.post("/agregar_producto")
async def agregar_producto(
    request: Request,
    nombre: str = Form(...),
    categoria_id: int = Form(...),
    precio: float = Form(...),
    cantidad: int = Form(...),
    proveedor_id: int = Form(...)
):
    conn = connect_db()  # Conectamos a la base de datos
    cursor = conn.cursor()
    
    # Verificar si el producto ya existe con el mismo nombre y precio
    cursor.execute("SELECT * FROM productos WHERE nombre = ? AND precio = ?", (nombre, precio))
    producto_existente = cursor.fetchone()
    
    if producto_existente:
        # Si el producto existe, actualizar solo la cantidad
        nueva_cantidad = producto_existente[4] + cantidad
        cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, producto_existente[0]))
    else:
        # Si el producto no existe, agregarlo como un nuevo producto
        cursor.execute(
            "INSERT INTO productos (nombre, categoría_id, precio, cantidad, proveedor_id) VALUES (?, ?, ?, ?, ?)",
            (nombre, categoria_id, precio, cantidad, proveedor_id)
        )
    
    conn.commit()  # Guardamos los cambios en la base de datos
    conn.close()  # Cerramos la conexión a la base de datos
    return RedirectResponse(url='/', status_code=303)  # Redireccionamos a la página principal

@app.post("/modificar_cantidad/{producto_id}")
async def modificar_cantidad(producto_id: int, nueva_cantidad: int = Form(...)):
    conn = connect_db()  # Conectamos a la base de datos
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, producto_id))  # Actualizamos la cantidad del producto
    conn.commit()  # Guardamos los cambios en la base de datos
    conn.close()  # Cerramos la conexión a la base de datos
    return RedirectResponse(url='/', status_code=303)  # Redireccionamos a la página principal

@app.post("/eliminar_producto/{producto_id}")
async def eliminar_producto(producto_id: int):
    conn = connect_db()  # Conectamos a la base de datos
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))  # Eliminamos el producto
    conn.commit()  # Guardamos los cambios en la base de datos
    conn.close()  # Cerramos la conexión a la base de datos
    return RedirectResponse(url='/', status_code=303)  # Redireccionamos a la página principal

@app.post("/reducir_cantidad/{producto_id}")
async def reducir_cantidad(producto_id: int, cantidad: int = Form(...)):
    conn = connect_db()  # Conectamos a la base de datos
    cursor = conn.cursor()
    
    # Obtener la cantidad actual del producto
    cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
    producto = cursor.fetchone()
    
    if producto and producto[4] >= cantidad:  # Verificamos si hay suficiente cantidad del producto
        nueva_cantidad = producto[4] - cantidad
        cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, producto_id))  # Actualizamos la cantidad del producto
        
        # Registrar la venta
        fecha_venta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO ventas (producto_id, cantidad, fecha, total) VALUES (?, ?, ?, ?)",
                       (producto_id, cantidad, fecha_venta, producto[3] * cantidad))  # precio * cantidad

        conn.commit()  # Guardamos los cambios en la base de datos
        conn.close()  # Cerramos la conexión a la base de datos
        return RedirectResponse(url='/', status_code=303)  # Redireccionamos a la página principal
    else:
        conn.close()  # Cerramos la conexión a la base de datos
        raise HTTPException(status_code=400, detail="Cantidad insuficiente o producto no encontrado")  # Lanzamos un error si no hay suficiente cantidad

@app.post("/eliminar_venta/{venta_id}")
async def eliminar_venta(venta_id: int):
    conn = connect_db()  # Conectamos a la base de datos
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ventas WHERE id = ?", (venta_id,))  # Eliminamos la venta
    conn.commit()  # Guardamos los cambios en la base de datos
    conn.close()  # Cerramos la conexión a la base de datos
    return RedirectResponse(url='/ventas', status_code=303)  # Redireccionamos a la lista de ventas

@app.post("/eliminar_proveedor/{proveedor_id}")
async def eliminar_proveedor(proveedor_id: int):
    conn = connect_db()  # Conectamos a la base de datos
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proveedores WHERE id = ?", (proveedor_id,))  # Eliminamos el proveedor
    conn.commit()  # Guardamos los cambios en la base de datos
    conn.close()  # Cerramos la conexión a la base de datos
    return RedirectResponse(url='/proveedores', status_code=303)  # Redireccionamos a la lista de proveedores

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)  # Iniciamos el servidor con uvicorn
