from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import secrets
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex()

# Función para conectar a la base de datos
def conectar_mysql():
    try:
        # Configura la conexión a la base de datos
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456789",
            database="softwareganadero"
        )
        print("¡Conexión exitosa a MySQL!")
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
        return None

# Ruta para la página de inicio
@app.route("/")
def inicio():
    return render_template("inicio.html")

# Ruta para mostrar el formulario de registro de animales y procesar los datos
@app.route("/registrar_animal", methods=["GET", "POST"])
def registrar_animal():
    if request.method == "POST":
        # Capturar los datos del formulario
        idAnimal = int(request.form["idAnimal"])
        fechaNacimiento = request.form["fechaNacimiento"]
        sexoAnimal = request.form["sexoAnimal"].upper()
        pesoAnimal = int(request.form["pesoAnimal"])
        estadoSalud = request.form["estadoSalud"]
        nomAnimal = request.form["nomAnimal"]
        idRaza = int(request.form["idRaza"])
        estado = int(request.form["estado"])

        # Validar que el sexo sea M o H
        if sexoAnimal not in ['M', 'H']:
            flash("Error: El sexo debe ser 'M' o 'H'.", "error")
            return redirect(url_for("registrar_animal"))

        # Validar que la fecha esté en el formato correcto (YYYY-MM-DD)
        try:
            fechaNacimiento = datetime.strptime(fechaNacimiento, "%Y-%m-%d").date()
        except ValueError:
            flash("Error: La fecha debe estar en formato YYYY-MM-DD.", "error")
            return redirect(url_for("registrar_animal"))

        # Crear un diccionario con los datos del animal
        datos_animal = {
            "idAnimal": idAnimal,
            "fechaNacimiento": fechaNacimiento,
            "sexoAnimal": sexoAnimal,
            "pesoAnimal": pesoAnimal,
            "estadoSalud": estadoSalud,
            "nomAnimal": nomAnimal,
            "idRaza": idRaza,
            "estado": estado
        }


        # Guardar los datos en la base de datos
        guardar_datos_animal(datos_animal)
        flash("Animal registrado correctamente.", "success")
        return redirect(url_for("registrar_animal"))
    else:
        razas = obtener_razas()
        # Mostrar el formulario (GET)
        return render_template("registroanimal.html", razas=razas)

# Función para guardar los datos en la base de datos
def guardar_datos_animal(datos):
    conexion = conectar_mysql()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        query = """
        INSERT INTO registroanimal (idAnimal, fechaNacimiento, sexoAnimal, pesoAnimal, estadoSalud, nomAnimal, idRaza, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            datos["idAnimal"],
            datos["fechaNacimiento"],
            datos["sexoAnimal"],
            datos["pesoAnimal"],
            datos["estadoSalud"],
            datos["nomAnimal"],
            datos["idRaza"],
            datos["estado"]
        )
        cursor.execute(query, valores)
        conexion.commit()
        print("Datos del animal guardados correctamente.")
    except Exception as e:
        print(f"Error al guardar los datos: {e}")
    finally:
        cursor.close()
        conexion.close()

@app.route("/informes_registro_animal")
def informes_registro_animal():
    conexion = conectar_mysql()
    if conexion is None:
        return "Error al conectar a la base de datos", 500

    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT ra.idAnimal, rz.descripcionRaza, ra.fechaNacimiento, ra.sexoAnimal, ra.pesoAnimal, ra.estadoSalud, ra.nomAnimal, ra.estado
        FROM registroanimal ra
        JOIN raza rz ON ra.idRaza = rz.idRaza
        """
        cursor.execute(query)
        animales = cursor.fetchall()
        return render_template("informesregistroanimal.html", animales=animales)
    except mysql.connector.Error as err:
        print(f"Error al obtener los datos de los animales: {err}")
        return "Error al obtener los datos de los animales", 500
    finally:
        cursor.close()
        conexion.close()

def obtener_razas():
    conexion = conectar_mysql()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT idRaza, descripcionRaza FROM raza WHERE estado = 1")  # Solo razas activas
        razas = cursor.fetchall()
        return razas
    except mysql.connector.Error as err:
        print(f"Error al obtener las razas: {err}")
        return []
    finally:
        cursor.close()
        conexion.close()

#Funcion para registrar la raza
@app.route("/registrar_raza", methods=["GET", "POST"])
def registrar_raza():
    if request.method == "POST":
        # Capturar los datos del formulario
        idRaza = int(request.form["idRaza"])
        descripcionRaza = request.form["descripcionRaza"]
        estado = int(request.form["estado"])

        # Crear un diccionario con los datos de la raza
        datos_raza = {
            "idRaza": idRaza,
            "descripcionRaza": descripcionRaza,
            "estado": estado
        }

        # Guardar los datos en la base de datos
        guardar_datos_raza(datos_raza)
        flash("Raza registrada correctamente.", "success")
        return redirect(url_for("registrar_raza"))
    else:
        # Mostrar el formulario (GET)
        return render_template("registrarraza.html")
    
    # Función para guardar los datos en la base de datos
def guardar_datos_raza(datos):
    conexion = conectar_mysql()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        query = """
        INSERT INTO raza (idRaza, descripcionRaza, estado)
        VALUES (%s, %s, %s)
        """
        valores = (
            datos["idRaza"],
            datos["descripcionRaza"],
            datos["estado"]
        )
        cursor.execute(query, valores)
        conexion.commit()
        print("Datos de la raza guardados correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al guardar los datos: {err}")
    finally:
        cursor.close()
        conexion.close()

@app.route("/informes_razas")
def informes_razas():
    conexion = conectar_mysql()
    if conexion is None:
        return "Error al conectar a la base de datos", 500

    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT idRaza, descripcionRaza, estado FROM raza
        """
        cursor.execute(query)
        razas = cursor.fetchall()
        return render_template("informesderazas.html", razas=razas)
    except mysql.connector.Error as err:
        print(f"Error al obtener los datos de las razas: {err}")
        return "Error al obtener los datos de las razas", 500
    finally:
        cursor.close()
        conexion.close()



# Registro para el historial de animal
@app.route("/registrar_historial_animal", methods=["GET", "POST"])
def registrar_historial_animal():
    if request.method == "POST":
        # Capturar los datos del formulario
        idHistorial = int(request.form["idHistorial"])
        fechaHistorial = request.form["fechaHistorial"]
        idAnimal = int(request.form["idAnimal"])
        estado = int(request.form["estado"])

        # Validar que la fecha esté en el formato correcto (YYYY-MM-DD)
        try:
            fechaHistorial = datetime.strptime(fechaHistorial, "%Y-%m-%d").date()
        except ValueError:
            flash("Error: La fecha debe estar en formato YYYY-MM-DD.", "error")
            return redirect(url_for("registrar_historial_animal"))

        # Crear un diccionario con los datos del historial
        datos_historial = {
            "idHistorial": idHistorial,
            "fechaHistorial": fechaHistorial,
            "idAnimal": idAnimal,
            "estado": estado
        }

        # Guardar los datos en la base de datos
        guardar_datos_historial(datos_historial)
        flash("Historial del animal registrado correctamente.", "success")
        return redirect(url_for("registrar_historial_animal"))
    else:
        # Obtener la lista de animales para el formulario
        animales = obtener_animales()
        return render_template("historialanimal.html", animales=animales)

# Función para guardar los datos del historial en la base de datos
def guardar_datos_historial(datos):
    conexion = conectar_mysql()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        query = """
        INSERT INTO historialanimal (idHistorial, fechaHistorial, idAnimal, estado)
        VALUES (%s, %s, %s, %s)
        """
        valores = (
            datos["idHistorial"],
            datos["fechaHistorial"],
            datos["idAnimal"],
            datos["estado"]
        )
        cursor.execute(query, valores)
        conexion.commit()
        print("Datos del historial del animal guardados correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al guardar los datos: {err}")
    finally:
        cursor.close()
        conexion.close()

# Función para obtener la lista de animales
def obtener_animales():
    conexion = conectar_mysql()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT idAnimal, nomAnimal FROM registroanimal WHERE estado = 1")  # Solo animales activos
        animales = cursor.fetchall()
        return animales
    except mysql.connector.Error as err:
        print(f"Error al obtener los animales: {err}")
        return []
    finally:
        cursor.close()
        conexion.close()

@app.route("/informes_historial_animal")
def informes_historial_animal():
    conexion = conectar_mysql()
    if conexion is None:
        return "Error al conectar a la base de datos", 500

    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT h.idHistorial, h.fechaHistorial, r.idAnimal, h.estado
        FROM historialanimal h
        JOIN registroanimal r ON h.idAnimal = r.idAnimal
        """
        cursor.execute(query)
        historiales = cursor.fetchall()
        return render_template("informeshistorialanimal.html", historiales=historiales)
    except mysql.connector.Error as err:
        print(f"Error al obtener los datos del historial: {err}")
        return "Error al obtener los datos del historial", 500
    finally:
        cursor.close()
        conexion.close()


#Funcion para Registro de tratamiento
@app.route("/registrar_tratamiento", methods=["GET", "POST"])
def registrar_tratamiento():
    if request.method == "POST":
        # Capturar los datos del formulario
        idTratamientos = int(request.form["idTratamientos"])
        fechaTratamiento = request.form["fechaTratamiento"]
        diagnosticoTratamiento = request.form["diagnosticoTratamiento"]
        idHistorial = int(request.form["idHistorial"])
        idVeterinario = int(request.form["idVeterinario"])
        estado = int(request.form["estado"])

        # Validar que la fecha esté en el formato correcto (YYYY-MM-DD)
        try:
            fechaTratamiento = datetime.strptime(fechaTratamiento, "%Y-%m-%d").date()
        except ValueError:
            flash("Error: La fecha debe estar en formato YYYY-MM-DD.", "error")
            return redirect(url_for("registrar_tratamiento"))

        # Crear un diccionario con los datos del tratamiento
        datos_tratamiento = {
            "idTratamientos": idTratamientos,
            "fechaTratamiento": fechaTratamiento,
            "diagnosticoTratamiento": diagnosticoTratamiento,
            "idHistorial": idHistorial,
            "idVeterinario": idVeterinario,
            "estado": estado
        }

        # Guardar los datos en la base de datos
        guardar_datos_tratamiento(datos_tratamiento)
        flash("Tratamiento registrado correctamente.", "success")
        return redirect(url_for("registrar_tratamiento"))
    else:
        # Obtener la lista de historiales y veterinarios para el formulario
        historiales = obtener_historiales()
        veterinarios = obtener_veterinarios()
        return render_template("registrotratamientos.html", historiales=historiales, veterinarios=veterinarios)

# Función para guardar los datos del tratamiento en la base de datos
def guardar_datos_tratamiento(datos):
    conexion = conectar_mysql()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        query = """
        INSERT INTO tratamientos (idTratamientos, fechaTratamiento, diagnosticoTratamiento, idHistorial, idVeterinario, estado)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        valores = (
            datos["idTratamientos"],
            datos["fechaTratamiento"],
            datos["diagnosticoTratamiento"],
            datos["idHistorial"],
            datos["idVeterinario"],
            datos["estado"]
        )
        cursor.execute(query, valores)
        conexion.commit()
        print("Datos del tratamiento guardados correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al guardar los datos: {err}")
    finally:
        cursor.close()
        conexion.close()

# Función para obtener la lista de historiales
def obtener_historiales():
    conexion = conectar_mysql()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT idHistorial, fechaHistorial FROM historialanimal WHERE estado = 1")  # Solo historiales activos
        historiales = cursor.fetchall()
        return historiales
    except mysql.connector.Error as err:
        print(f"Error al obtener los historiales: {err}")
        return []
    finally:
        cursor.close()
        conexion.close()

# Función para obtener la lista de veterinarios
def obtener_veterinarios():
    conexion = conectar_mysql()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT idVeterinario, nombreVeterinario FROM veterinario WHERE estado = 1")  # Solo veterinarios activos
        veterinarios = cursor.fetchall()
        return veterinarios
    except mysql.connector.Error as err:
        print(f"Error al obtener los veterinarios: {err}")
        return []
    finally:
        cursor.close()
        conexion.close()

@app.route("/informes_tratamientos")
def informes_tratamientos():
    conexion = conectar_mysql()
    if conexion is None:
        return "Error al conectar a la base de datos", 500

    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT t.idTratamientos, t.fechaTratamiento, t.diagnosticoTratamiento, h.idHistorial, v.nombreVeterinario, t.estado
        FROM tratamientos t
        JOIN historialanimal h ON t.idHistorial = h.idHistorial
        JOIN veterinario v ON t.idVeterinario = v.idVeterinario
        """
        cursor.execute(query)
        tratamientos = cursor.fetchall()
        return render_template("informesregistrotratamientos.html", tratamientos=tratamientos)
    except mysql.connector.Error as err:
        print(f"Error al obtener los datos de los tratamientos: {err}")
        return "Error al obtener los datos de los tratamientos", 500
    finally:
        cursor.close()
        conexion.close()

    ##Funcion para Registro de tipo de vacunas
@app.route("/registrar_tipo_vacuna", methods=["GET", "POST"])
def registrar_tipo_vacuna():
    if request.method == "POST":
        # Capturar los datos del formulario
        idTipoVacuna = int(request.form["idTipoVacuna"])
        descripcionVacuna = request.form["descripcionVacuna"]
        estado = int(request.form["estado"])

        # Crear un diccionario con los datos del tipo de vacuna
        datos_tipo_vacuna = {
            "idTipoVacuna": idTipoVacuna,
            "descripcionVacuna": descripcionVacuna,
            "estado": estado
        }

        # Guardar los datos en la base de datos
        guardar_datos_tipo_vacuna(datos_tipo_vacuna)
        flash("Tipo de vacuna registrado correctamente.", "success")
        return redirect(url_for("registrar_tipo_vacuna"))
    else:
        # Mostrar el formulario (GET)
        return render_template("tiposvacuna.html")

# Función para guardar los datos del tipo de vacuna en la base de datos
def guardar_datos_tipo_vacuna(datos):
    conexion = conectar_mysql()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        query = """
        INSERT INTO tipovacuna (idTipoVacuna, descripcionVacuna, estado)
        VALUES (%s, %s, %s)
        """
        valores = (
            datos["idTipoVacuna"],
            datos["descripcionVacuna"],
            datos["estado"]
        )
        cursor.execute(query, valores)
        conexion.commit()
        print("Datos del tipo de vacuna guardados correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al guardar los datos: {err}")
    finally:
        cursor.close()
        conexion.close()


@app.route("/informes_tipos_vacuna")
def informes_tipos_vacuna():
    conexion = conectar_mysql()
    if conexion is None:
        return "Error al conectar a la base de datos", 500

    try:
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT idTipoVacuna, descripcionVacuna, estado FROM TipoVacuna"
        cursor.execute(query)
        tipos_vacuna = cursor.fetchall()
        return render_template("informestiposvacuna.html", tipos_vacuna=tipos_vacuna)
    except mysql.connector.Error as err:
        print(f"Error al obtener los datos de los tipos de vacuna: {err}")
        return "Error al obtener los datos de los tipos de vacuna", 500
    finally:
        cursor.close()
        conexion.close()

#Funcion para registrar empleados
@app.route("/registrar_empleado", methods=["GET", "POST"])
def registrar_empleado():
    if request.method == "POST":
        # Capturar los datos del formulario
        idEmpleado = int(request.form["idEmpleado"])
        nombreEmpleado = request.form["nombreEmpleado"]
        apellidoEmpleado = request.form["apellidoEmpleado"]
        estadoCivil = request.form["estadoCivil"]
        telefonoEmpleado = request.form["telefonoEmpleado"]
        fechaIngreso = request.form["fechaIngreso"]
        fechaNacimiento = request.form["fechaNacimiento"]
        estado = int(request.form["estado"])

        # Validar que las fechas estén en el formato correcto (YYYY-MM-DD)
        try:
            fechaIngreso = datetime.strptime(fechaIngreso, "%Y-%m-%d").date()
            fechaNacimiento = datetime.strptime(fechaNacimiento, "%Y-%m-%d").date()
        except ValueError:
            flash("Error: Las fechas deben estar en formato YYYY-MM-DD.", "error")
            return redirect(url_for("registrar_empleado"))

        # Crear un diccionario con los datos del empleado
        datos_empleado = {
            "idEmpleado": idEmpleado,
            "nombreEmpleado": nombreEmpleado,
            "apellidoEmpleado": apellidoEmpleado,
            "estadoCivil": estadoCivil,
            "telefonoEmpleado": telefonoEmpleado,
            "fechaIngreso": fechaIngreso,
            "fechaNacimiento": fechaNacimiento,
            "estado": estado
        }

        # Guardar los datos en la base de datos
        guardar_datos_empleado(datos_empleado)
        flash("Empleado registrado correctamente.", "success")
        return redirect(url_for("registrar_empleado"))
    else:
        # Mostrar el formulario (GET)
        return render_template("gestionempleados.html")

# Función para guardar los datos del empleado en la base de datos
def guardar_datos_empleado(datos):
    conexion = conectar_mysql()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        query = """
        INSERT INTO empleado (idEmpleado, nombreEmpleado, apellidoEmpleado, estadoCivil, telefonoEmpleado, fechaIngreso, fechaNacimiento, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            datos["idEmpleado"],
            datos["nombreEmpleado"],
            datos["apellidoEmpleado"],
            datos["estadoCivil"],
            datos["telefonoEmpleado"],
            datos["fechaIngreso"],
            datos["fechaNacimiento"],
            datos["estado"]
        )
        cursor.execute(query, valores)
        conexion.commit()
        print("Datos del empleado guardados correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al guardar los datos: {err}")
    finally:
        cursor.close()
        conexion.close()

@app.route("/informes_empleados")
def informes_empleados():
    conexion = conectar_mysql()
    if conexion is None:
        return "Error al conectar a la base de datos", 500

    try:
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT idEmpleado, nombreEmpleado, apellidoEmpleado, estadoCivil, telefonoEmpleado, fechaIngreso, fechaNacimiento, estado FROM empleado"
        cursor.execute(query)
        empleados = cursor.fetchall()
        return render_template("informesgestionempleados.html", empleados=empleados)
    except mysql.connector.Error as err:
        print(f"Error al obtener los datos de los empleados: {err}")
        return "Error al obtener los datos de los empleados", 500
    finally:
        cursor.close()
        conexion.close()

#Funcion para registrar vacunas
@app.route("/registrar_vacuna", methods=["GET", "POST"])
def registrar_vacuna():
    if request.method == "POST":
        # Capturar los datos del formulario
        idVacuna = int(request.form["idVacuna"])
        fechaVacunacion = request.form["fechaVacunacion"]
        idTipoVacuna = int(request.form["idTipoVacuna"])
        estado = int(request.form["estado"])

        # Validar que la fecha esté en el formato correcto (YYYY-MM-DD)
        try:
            fechaVacunacion = datetime.strptime(fechaVacunacion, "%Y-%m-%d").date()
        except ValueError:
            flash("Error: La fecha debe estar en formato YYYY-MM-DD.", "error")
            return redirect(url_for("registrar_vacuna"))

        # Crear un diccionario con los datos de la vacuna
        datos_vacuna = {
            "idVacuna": idVacuna,
            "fechaVacunacion": fechaVacunacion,
            "idTipoVacuna": idTipoVacuna,
            "estado": estado
        }

        # Guardar los datos en la base de datos
        guardar_datos_vacuna(datos_vacuna)
        flash("Vacuna registrada correctamente.", "success")
        return redirect(url_for("registrar_vacuna"))
    else:
        # Obtener la lista de tipos de vacuna para el formulario
        tipos_vacuna = obtener_tipos_vacuna()
        return render_template("gestionvacunas.html", tipos_vacuna=tipos_vacuna)

# Función para guardar los datos de la vacuna en la base de datos
def guardar_datos_vacuna(datos):
    conexion = conectar_mysql()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        query = """
        INSERT INTO vacuna (idVacuna, fechaVacunacion, idTipoVacuna, estado)
        VALUES (%s, %s, %s, %s)
        """
        valores = (
            datos["idVacuna"],
            datos["fechaVacunacion"],
            datos["idTipoVacuna"],
            datos["estado"]
        )
        cursor.execute(query, valores)
        conexion.commit()
        print("Datos de la vacuna guardados correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al guardar los datos: {err}")
    finally:
        cursor.close()
        conexion.close()

# Función para obtener la lista de tipos de vacuna
def obtener_tipos_vacuna():
    conexion = conectar_mysql()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT idTipoVacuna, descripcionVacuna FROM TipoVacuna WHERE estado = 1")  # Solo tipos de vacuna activos
        tipos_vacuna = cursor.fetchall()
        return tipos_vacuna
    except mysql.connector.Error as err:
        print(f"Error al obtener los tipos de vacuna: {err}")
        return []
    finally:
        cursor.close()
        conexion.close()

@app.route("/informes_vacunas")
def informes_vacunas():
    conexion = conectar_mysql()
    if conexion is None:
        return "Error al conectar a la base de datos", 500

    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT v.idVacuna, v.fechaVacunacion, tv.descripcionVacuna, v.estado
        FROM vacuna v
        JOIN TipoVacuna tv ON v.idTipoVacuna = tv.idTipoVacuna
        """
        cursor.execute(query)
        vacunas = cursor.fetchall()
        return render_template("informesgestionvacunas.html", vacunas=vacunas)
    except mysql.connector.Error as err:
        print(f"Error al obtener los datos de las vacunas: {err}")
        return "Error al obtener los datos de las vacunas", 500
    finally:
        cursor.close()
        conexion.close()

#Funcion para registrar especialidad
@app.route("/registrar_especialidad", methods=["GET", "POST"])
def registrar_especialidad():
    if request.method == "POST":
        # Capturar los datos del formulario
        idEspecialidad = int(request.form["idEspecialidad"])
        descripcionEspecialidad = request.form["descripcionEspecialidad"]
        estado = int(request.form["estado"])

        # Crear un diccionario con los datos de la especialidad
        datos_especialidad = {
            "idEspecialidad": idEspecialidad,
            "descripcionEspecialidad": descripcionEspecialidad,
            "estado": estado
        }

        # Guardar los datos en la base de datos
        guardar_datos_especialidad(datos_especialidad)
        flash("Especialidad registrada correctamente.", "success")
        return redirect(url_for("registrar_especialidad"))  # Recarga la página actual
    else:
        # Mostrar el formulario (GET)
        return render_template("registrarespecialidad.html")

# Función para guardar los datos de la especialidad en la base de datos
def guardar_datos_especialidad(datos):
    conexion = conectar_mysql()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        query = """
        INSERT INTO especialidad (idEspecialidad, descripcionEspecialidad, estado)
        VALUES (%s, %s, %s)
        """
        valores = (
            datos["idEspecialidad"],
            datos["descripcionEspecialidad"],
            datos["estado"]
        )
        cursor.execute(query, valores)
        conexion.commit()
        print("Datos de la especialidad guardados correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al guardar los datos: {err}")
    finally:
        cursor.close()
        conexion.close()

@app.route("/informes_especialidades")
def informes_especialidades():
    conexion = conectar_mysql()
    if conexion is None:
        return "Error al conectar a la base de datos", 500

    try:
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT idEspecialidad, descripcionEspecialidad, estado FROM especialidad"
        cursor.execute(query)
        especialidades = cursor.fetchall()
        return render_template("informesespecialidad.html", especialidades=especialidades)
    except mysql.connector.Error as err:
        print(f"Error al obtener los datos de las especialidades: {err}")
        return "Error al obtener los datos de las especialidades", 500
    finally:
        cursor.close()
        conexion.close()

#Funcion para registrar veterinarios
@app.route("/registrar_veterinario", methods=["GET", "POST"])
def registrar_veterinario():
    if request.method == "POST":
        # Capturar los datos del formulario
        idEVeterinario= int(request.form["idVeterinario"])
        nombreVeterinario = request.form["nombreVeterinario"]
        apellidoVeterinario = request.form["apellidoVeterinario"]
        telefonoVeterinario = request.form["telefonoVeterinario"]
        correoVeterinario = request.form["correoVeterinario"]
        direccionVeterinario = request.form["direccionVeterinario"]
        idEspecialidad = int(request.form["idEspecialidad"])
        estado = int(request.form["estado"])

        # Crear un diccionario con los datos del veterinario
        datos_veterinario = {
            "idVeterinario": idEVeterinario,
            "nombreVeterinario": nombreVeterinario,
            "apellidoVeterinario": apellidoVeterinario,
            "telefonoVeterinario": telefonoVeterinario,
            "correoVeterinario": correoVeterinario,
            "direccionVeterinario": direccionVeterinario,
            "idEspecialidad": idEspecialidad,
            "estado": estado
        }

        # Guardar los datos en la base de datos
        guardar_datos_veterinario(datos_veterinario)
        flash("Veterinario registrado correctamente.", "success")
        return redirect(url_for("registrar_veterinario"))  # Recarga la página actual
    else:
        # Obtener la lista de especialidades para el formulario
        especialidades = obtener_especialidades()
        return render_template("registrarveterinario.html", especialidades=especialidades)

# Función para guardar los datos del veterinario en la base de datos
def guardar_datos_veterinario(datos):
    conexion = conectar_mysql()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        query = """
        INSERT INTO veterinario (idVeterinario, nombreVeterinario, apellidoVeterinario, telefonoVeterinario, correoVeterinario, direccionVeterinario, idEspecialidad, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            datos["idVeterinario"],
            datos["nombreVeterinario"],
            datos["apellidoVeterinario"],
            datos["telefonoVeterinario"],
            datos["correoVeterinario"],
            datos["direccionVeterinario"],
            datos["idEspecialidad"],
            datos["estado"]
        )
        cursor.execute(query, valores)
        conexion.commit()
        print("Datos del veterinario guardados correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al guardar los datos: {err}")
    finally:
        cursor.close()
        conexion.close()

# Función para obtener la lista de especialidades
def obtener_especialidades():
    conexion = conectar_mysql()
    if conexion is None:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT idEspecialidad, descripcionEspecialidad FROM especialidad WHERE estado = 1")  # Solo especialidades activas
        especialidades = cursor.fetchall()
        return especialidades
    except mysql.connector.Error as err:
        print(f"Error al obtener las especialidades: {err}")
        return []
    finally:
        cursor.close()
        conexion.close()

@app.route("/informes_veterinarios")
def informes_veterinarios():
    conexion = conectar_mysql()
    if conexion is None:
        return "Error al conectar a la base de datos", 500

    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
        SELECT v.idVeterinario, v.nombreVeterinario, v.apellidoVeterinario, v.telefonoVeterinario, v.correoVeterinario, v.direccionVeterinario, e.descripcionEspecialidad, v.estado
        FROM veterinario v
        JOIN especialidad e ON v.idEspecialidad = e.idEspecialidad
        """
        cursor.execute(query)
        veterinarios = cursor.fetchall()
        return render_template("informesveterinario.html", veterinarios=veterinarios)
    except mysql.connector.Error as err:
        print(f"Error al obtener los datos de los veterinarios: {err}")
        return "Error al obtener los datos de los veterinarios", 500
    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    app.run(debug=True)