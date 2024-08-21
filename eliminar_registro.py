import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('agua.db')
cursor = conn.cursor()

# Eliminar un registro específico
id_a_eliminar = 5  # Cambia este valor por el ID del registro que deseas eliminar
cursor.execute("DELETE FROM mediciones WHERE id = ?", (id_a_eliminar,))

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()

print(f"Registro con ID {id_a_eliminar} eliminado correctamente.")
