# =============================================================================
#  PROGRAMA:      LISTA DIGITAL DE CONTACTOS
#  ARCHIVO:       contactos.py
#  CURSO:         Taller de Programación - Ingeniería en Computación - TEC
#  AUTOR:         Cristhoper Jara Salazar
#  VERSIÓN:       1.0
#  CREACIÓN:      25/10/2026
#  LENGUAJE:      Python 3.14 (usa match-case, requiere Python 3.10 o superior)
#
#  DESCRIPCIÓN:
#  Programa con interfaz de texto (TUI) para registrar y consultar contactos.
#  Permite mantener (agregar, consultar, modificar y eliminar) áreas
#  telefónicas, contactos y grupos de contactos, configurar valores por
#  omisión y emitir un listado filtrado de contactos en un archivo PDF.
#
#  ESTRUCTURAS DE DATOS PRINCIPALES (se crean en main y se pasan por
#  parámetro a las funciones que las ocupan):
#   - areas:               lista de tuplas (codigo_area, nombre_area)
#   - configuracion:       lista [area_por_omision, tipo_por_omision]
#                          (None mientras no se haya configurado)
#   - contactos:           lista de listas, cada una con:
#                          [telefono, area, tipo, nombre, correo, direccion,
#                           fecha_nacimiento, pasatiempos, notas]
#   - grupos:              lista de strings (nombres de grupos)
#   - contactos_por_grupo: lista de listas de tuplas (telefono, area).
#                          Relación 1:1 con grupos: el elemento en el índice
#                          n pertenece al grupo grupos[n].
# =============================================================================

import os
import re
import datetime
import webbrowser

# ------------------------------- CONSTANTES ---------------------------------
NOMBRE_PROGRAMA = "LISTA DIGITAL DE CONTACTOS"
VERSION = "1.0"
FECHA_CREACION = "25/10/2026"
AUTOR = "Cristhoper Jara Salazar"

# Tipos de teléfono: para cada tipo se guarda un código y su descripción
TIPOS_TELEFONO = ("M", "Móvil", "C", "Casa", "T", "Trabajo", "O", "Otro")

# Posición (índice) de cada dato dentro de un contacto
TEL, AREA, TIPO, NOMBRE, CORREO, DIRECCION, FECHA, PASATIEMPOS, NOTAS = range(9)

# Carpeta donde está el programa (ahí se guardan los PDF y está el manual)
CARPETA_PROGRAMA = os.path.dirname(os.path.abspath(__file__))

# ----------------------------- DATOS DE PRUEBA -------------------------------
# Datos ya probados que se cargan al iniciar, para no tener que digitarlos
# cada vez que se ejecuta el programa (sugerencia del enunciado).
AREAS_PRUEBA = [(506, "Costa Rica"), (47, "Noruega"), (502, "Guatemala")]

CONTACTOS_PRUEBA = [
    [12345678, 506, "M", "Alberto Castillo Matamoros", "a_castillo@yahoo.com",
     "Cartago centro", "30/01/2001", "futbol, basquet, videojuegos",
     "está de vacaciones"],
    [12345679, 506, "C", "William Mata Rojas", "wmata@gmail.com",
     "San José, Curridabat", "15/08/0000", "lectura, ajedrez", ""],
    [12345670, 506, "T", "María Fernández Castillo", "mfernandez@tec.ac.cr",
     "", 0, "ciclismo, cocina", "compañera del TEC"],
    [98765432, 502, "M", "Luis Pérez Gómez", "lperez@hotmail.com",
     "Ciudad de Guatemala", "05/12/1999", "videojuegos", ""],
]

GRUPOS_PRUEBA = ["COMPAS DEL COLEGIO", "BARRIO"]
CONTACTOS_POR_GRUPO_PRUEBA = [[(12345678, 506), (12345679, 506),
                               (12345670, 506)], []]


# =============================================================================
#                         FUNCIONES DE USO GENERAL
# =============================================================================
def limpiar_pantalla():
    """Borra la consola (cls en Windows, clear en Linux/Mac)."""
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_encabezado(subtitulo):
    """Limpia la pantalla y muestra el título del programa y el subtítulo."""
    limpiar_pantalla()
    print("=" * 72)
    print("  " + NOMBRE_PROGRAMA)
    print("  " + subtitulo)
    print("=" * 72)


def mostrar_error(mensaje):
    """Despliega un mensaje de error resaltado."""
    print("   *** " + mensaje + " ***")


def pausar():
    """Detiene la ejecución hasta que el usuario presione Enter."""
    input("\n  Presione <Enter> para continuar...")


def mostrar_mensaje(mensaje):
    """Muestra un mensaje informativo y espera Enter."""
    print("\n  >> " + mensaje)
    pausar()


def etiqueta(texto):
    """Retorna la etiqueta de un dato alineada a 24 caracteres."""
    return "  " + texto.ljust(24)


def mostrar_menu(subtitulo, opciones):
    """Muestra un menú numerado con las opciones recibidas y la opción 0.
    Entradas: subtitulo (str), opciones (lista de str).
    Salida: la opción digitada por el usuario (str)."""
    mostrar_encabezado(subtitulo)
    for i in range(len(opciones)):
        print(f"  {i + 1}. {opciones[i]}")
    print("  0. Fin")
    return input("\n  OPCIÓN ").strip()


def leer_opcion_aceptar_cancelar():
    """Pide la opción final de una pantalla.
    Salida: True si el usuario acepta (A), False si cancela (C)."""
    while True:
        opcion = input("\n  OPCIÓN A-ACEPTAR C-CANCELAR ").strip().upper()
        if opcion == "A":
            return True
        if opcion == "C":
            return False
        mostrar_error("OPCIÓN INVÁLIDA, DIGITE A o C")


def leer_aceptar():
    """Pide la opción ACEPTAR (pantallas de solo consulta)."""
    while input("\n  OPCIÓN A-ACEPTAR ").strip().upper() != "A":
        mostrar_error("DIGITE A PARA ACEPTAR")


def confirmar_eliminacion():
    """Pide confirmación antes de borrar. Salida: True si responde SI."""
    while True:
        respuesta = input("  CONFIRMA LA ELIMINACIÓN (SI/NO) ").strip().upper()
        if respuesta in ("SI", "SÍ"):
            return True
        if respuesta == "NO":
            return False
        mostrar_error("RESPUESTA INVÁLIDA, DIGITE SI o NO")


def leer_texto(nombre_dato, minimo, maximo, actual=None):
    """Lee un string con largo entre minimo y maximo caracteres.
    Si 'actual' no es None (modificación) y el usuario da solo <Enter>,
    retorna el valor actual sin cambios."""
    while True:
        texto = input(etiqueta(nombre_dato)).strip()
        if texto == "" and actual is not None:
            return actual
        if minimo <= len(texto) <= maximo:
            return texto
        mostrar_error(f"DEBE TENER ENTRE {minimo} Y {maximo} CARACTERES")


# =============================================================================
#                          1. REGISTRAR ÁREAS
# =============================================================================
def buscar_area(areas, codigo):
    """Busca un código en la lista areas.
    Salida: índice del área en la lista, o -1 si no existe."""
    for i in range(len(areas)):
        if areas[i][0] == codigo:
            return i
    return -1


def nombre_area(areas, codigo):
    """Retorna el nombre de un área, o "" si el código no existe."""
    indice = buscar_area(areas, codigo)
    if indice == -1:
        return ""
    return areas[indice][1]


def validar_codigo_area(texto):
    """Valida que el texto sea un entero entre 1 y 999.
    Salida: el código como entero, o None si no es válido."""
    if texto.isdigit():
        codigo = int(texto)
        if 1 <= codigo <= 999:
            return codigo
    return None


def leer_codigo_area(nombre_dato):
    """Pide un código de área válido (1 a 999).
    Salida: el código (int) o None si el usuario digita C (cancelar)."""
    while True:
        texto = input(etiqueta(nombre_dato)).strip()
        if texto.upper() == "C":
            return None
        codigo = validar_codigo_area(texto)
        if codigo is not None:
            return codigo
        mostrar_error("EL ÁREA DEBE SER UN NÚMERO ENTERO ENTRE 1 Y 999")


def leer_area_registrada(areas, mensaje_no_existe):
    """Pide un código de área hasta que exista en la lista.
    Salida: índice del área en la lista, o -1 si el usuario cancela."""
    while True:
        codigo = leer_codigo_area("Área")
        if codigo is None:
            return -1
        indice = buscar_area(areas, codigo)
        if indice != -1:
            return indice
        mostrar_error(mensaje_no_existe)


def area_tiene_contactos(contactos, codigo):
    """Integridad referencial: True si algún contacto usa el área."""
    for contacto in contactos:
        if contacto[AREA] == codigo:
            return True
    return False


def agregar_areas(areas):
    """Opción 1.1: agrega áreas nuevas (código único) a la lista areas."""
    while True:
        mostrar_encabezado("REGISTRAR ÁREAS: AGREGAR")
        print("  (Digite C en Área para regresar al menú anterior)\n")
        while True:
            codigo = leer_codigo_area("Área")
            if codigo is None:
                return
            if buscar_area(areas, codigo) == -1:
                break
            mostrar_error("ESTA ÁREA YA ESTÁ REGISTRADA, NO SE PUEDE AGREGAR")
        nombre = leer_texto("Nombre del área", 1, 40)
        if leer_opcion_aceptar_cancelar():
            areas.append((codigo, nombre))
            mostrar_mensaje("ÁREA AGREGADA")


def consultar_areas(areas):
    """Opción 1.2: muestra el nombre de un área registrada."""
    while True:
        mostrar_encabezado("REGISTRAR ÁREAS: CONSULTAR")
        print("  (Digite C en Área para regresar al menú anterior)\n")
        indice = leer_area_registrada(
            areas, "ESTA ÁREA NO ESTÁ REGISTRADA, NO SE PUEDE CONSULTAR")
        if indice == -1:
            return
        print(etiqueta("Nombre del área") + areas[indice][1])
        leer_aceptar()


def modificar_areas(areas):
    """Opción 1.3: cambia el nombre de un área (<Enter> lo deja igual)."""
    while True:
        mostrar_encabezado("REGISTRAR ÁREAS: MODIFICAR")
        print("  (Digite C en Área para regresar al menú anterior)\n")
        indice = leer_area_registrada(
            areas, "ESTA ÁREA NO ESTÁ REGISTRADA, NO SE PUEDE MODIFICAR")
        if indice == -1:
            return
        codigo, nombre = areas[indice]
        print(etiqueta("Nombre del área") + nombre)
        nuevo_nombre = leer_texto("MODIFICACIÓN", 1, 40, nombre)
        if leer_opcion_aceptar_cancelar():
            areas[indice] = (codigo, nuevo_nombre)   # las tuplas no cambian:
            mostrar_mensaje("ÁREA MODIFICADA")       # se reemplaza la tupla


def eliminar_areas(areas, contactos, configuracion):
    """Opción 1.4: elimina un área que no esté siendo usada por contactos
    ni por la configuración (integridad referencial)."""
    while True:
        mostrar_encabezado("REGISTRAR ÁREAS: ELIMINAR")
        print("  (Digite C en Área para regresar al menú anterior)\n")
        indice = leer_area_registrada(
            areas, "ESTA ÁREA NO ESTÁ REGISTRADA, NO SE PUEDE ELIMINAR")
        if indice == -1:
            return
        codigo = areas[indice][0]
        print(etiqueta("Nombre del área") + areas[indice][1])
        if not leer_opcion_aceptar_cancelar():
            continue
        if area_tiene_contactos(contactos, codigo):
            mostrar_mensaje("EN ESTA ÁREA HAY CONTACTOS REGISTRADOS, "
                            "NO SE PUEDE ELIMINAR")
        elif configuracion[0] == codigo:
            mostrar_mensaje("ESTA ÁREA ES EL ÁREA POR OMISIÓN DE LA "
                            "CONFIGURACIÓN, NO SE PUEDE ELIMINAR")
        elif confirmar_eliminacion():
            del areas[indice]
            mostrar_mensaje("ÁREA ELIMINADA")


def registrar_areas(areas, contactos, configuracion):
    """Opción 1 del menú principal: submenú de mantenimiento de áreas."""
    while True:
        opcion = mostrar_menu("REGISTRAR ÁREAS", [
            "Agregar áreas", "Consultar áreas", "Modificar áreas",
            "Eliminar áreas"])
        match opcion:
            case "1":
                agregar_areas(areas)
            case "2":
                consultar_areas(areas)
            case "3":
                modificar_areas(areas)
            case "4":
                eliminar_areas(areas, contactos, configuracion)
            case "0":
                return
            case _:
                mostrar_error("ESTA OPCIÓN NO EXISTE EN EL MENÚ")
                pausar()


# =============================================================================
#                 2. CONFIGURACIÓN DE LA LISTA DE CONTACTOS
# =============================================================================
def es_tipo_valido(codigo):
    """True si el código existe en la tupla TIPOS_TELEFONO.
    Los códigos están en las posiciones pares de la tupla."""
    for i in range(0, len(TIPOS_TELEFONO), 2):
        if TIPOS_TELEFONO[i] == codigo:
            return True
    return False


def descripcion_tipo(codigo):
    """Retorna la descripción de un tipo de teléfono (ej. M -> Móvil)."""
    for i in range(0, len(TIPOS_TELEFONO), 2):
        if TIPOS_TELEFONO[i] == codigo:
            return TIPOS_TELEFONO[i + 1]
    return ""


def texto_tipos():
    """Arma el texto 'M:Móvil, C:Casa, ...' a partir de TIPOS_TELEFONO."""
    partes = []
    for i in range(0, len(TIPOS_TELEFONO), 2):
        partes.append(TIPOS_TELEFONO[i] + ":" + TIPOS_TELEFONO[i + 1])
    return ", ".join(partes)


def leer_tipo_telefono(nombre_dato, omision):
    """Pide un tipo de teléfono válido. Si omision no es None y el usuario
    da <Enter>, retorna el valor por omisión."""
    while True:
        tipo = input(etiqueta(nombre_dato)).strip().upper()
        if tipo == "" and omision is not None:
            return omision
        if es_tipo_valido(tipo):
            return tipo
        mostrar_error("ESTE TIPO DE TELÉFONO NO EXISTE, NO SE PUEDE "
                      "SELECCIONAR")


def configurar_lista(areas, configuracion):
    """Opción 2: establece el área y el tipo de teléfono por omisión.
    Modifica la lista configuracion solo si el usuario acepta."""
    mostrar_encabezado("CONFIGURACIÓN DE LA LISTA DE CONTACTOS")
    if configuracion[0] is not None:
        print(f"  Configuración actual: área {configuracion[0]} "
              f"({nombre_area(areas, configuracion[0])}), tipo "
              f"{configuracion[1]} ({descripcion_tipo(configuracion[1])})")
    print("  (Digite C en Área por omisión para regresar al menú anterior)\n")
    while True:
        codigo = leer_codigo_area("Área por omisión")
        if codigo is None:
            return
        if buscar_area(areas, codigo) != -1:
            break
        mostrar_error("ESTA ÁREA NO ESTÁ REGISTRADA, NO SE PUEDE SELECCIONAR")
    print(etiqueta("") + nombre_area(areas, codigo))
    print("  Tipo de teléfono por omisión (" + texto_tipos() + ")")
    tipo = leer_tipo_telefono("Tipo por omisión", None)
    if leer_opcion_aceptar_cancelar():
        configuracion[0] = codigo
        configuracion[1] = tipo
        mostrar_mensaje("CONFIGURACIÓN GUARDADA")


# =============================================================================
#                          3. REGISTRAR CONTACTOS
# =============================================================================
def validar_telefono(texto):
    """Valida un número natural de 5 a 12 dígitos (no inicia con 0).
    Salida: el número como entero, o None si no es válido."""
    if texto.isdigit() and 5 <= len(texto) <= 12 and texto[0] != "0":
        return int(texto)
    return None


def validar_correo(texto):
    """Valida el formato parte1@parte2 con una expresión regular:
    [^\\s@]+ significa 'uno o más caracteres que no sean espacio ni @'."""
    return re.fullmatch(r"[^\s@]+@[^\s@]+", texto) is not None


def validar_fecha(texto):
    """Valida una fecha dd/mm/aaaa usando el módulo datetime.
    - Vacío o "0": no se tiene la fecha, retorna 0.
    - Año 0000: no se conoce el año; se valida día y mes con un año
      bisiesto (2000) para aceptar también el 29/02.
    - Con año: no puede ser una fecha futura.
    Salida: la fecha (str), 0, o None si no es válida."""
    if texto == "" or texto == "0":
        return 0
    partes = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", texto)
    if partes is None:
        return None
    dia, mes, anno = int(partes[1]), int(partes[2]), int(partes[3])
    try:
        fecha = datetime.date(anno if anno != 0 else 2000, mes, dia)
    except ValueError:              # día o mes fuera de rango
        return None
    if anno != 0 and fecha > datetime.date.today():
        return None
    return texto


def texto_fecha(fecha):
    """Fecha para desplegar: "" cuando el dato es 0 (no se tiene)."""
    return "" if fecha == 0 else fecha


def leer_correo(nombre_dato, actual=None):
    """Pide un correo válido. En modificación <Enter> conserva el actual."""
    while True:
        texto = input(etiqueta(nombre_dato)).strip()
        if texto == "" and actual is not None:
            return actual
        if validar_correo(texto):
            return texto
        mostrar_error("EL CORREO DEBE TENER EL FORMATO parte1@parte2 "
                      "SIN ESPACIOS")


def leer_fecha(nombre_dato, actual=None):
    """Pide una fecha dd/mm/aaaa (o vacío si no se tiene).
    En modificación <Enter> conserva el valor actual."""
    while True:
        texto = input(etiqueta(nombre_dato)).strip()
        if texto == "" and actual is not None:
            return actual
        fecha = validar_fecha(texto)
        if fecha is not None:
            return fecha
        mostrar_error("FECHA INVÁLIDA: USE dd/mm/aaaa (aaaa PUEDE SER 0000)"
                      " O DÉJELA EN BLANCO")


def buscar_contacto(contactos, telefono, area):
    """Busca un contacto por su teléfono (número + área).
    Salida: índice en la lista contactos, o -1 si no existe."""
    for i in range(len(contactos)):
        if contactos[i][TEL] == telefono and contactos[i][AREA] == area:
            return i
    return -1


def leer_telefono(areas, configuracion):
    """Pide las dos partes del teléfono: número y área.
    Si se da <Enter> en el área se usa el área por omisión.
    Salida: tupla (telefono, area), o None si se digita C en el número."""
    while True:
        texto = input(etiqueta("Teléfono")).strip()
        if texto.upper() == "C":
            return None
        telefono = validar_telefono(texto)
        if telefono is not None:
            break
        mostrar_error("EL TELÉFONO DEBE SER UN NÚMERO NATURAL DE 5 A 12 "
                      "DÍGITOS")
    area_omision = configuracion[0]
    texto_omision = f" [{area_omision}]" if area_omision is not None else ""
    while True:
        texto = input(etiqueta("Área" + texto_omision)).strip()
        if texto == "" and area_omision is not None:
            codigo = area_omision
        else:
            codigo = validar_codigo_area(texto)
            if codigo is None:
                mostrar_error("EL ÁREA DEBE SER UN NÚMERO ENTERO ENTRE 1 Y "
                              "999")
                continue
        if buscar_area(areas, codigo) != -1:
            break
        mostrar_error("ESTA ÁREA NO ESTÁ REGISTRADA")
    print(etiqueta("") + nombre_area(areas, codigo))
    return (telefono, codigo)


def leer_contacto_registrado(contactos, areas, configuracion,
                             mensaje_no_existe):
    """Pide un teléfono hasta que corresponda a un contacto registrado.
    Salida: índice del contacto, o -1 si el usuario cancela."""
    while True:
        telefono = leer_telefono(areas, configuracion)
        if telefono is None:
            return -1
        indice = buscar_contacto(contactos, telefono[0], telefono[1])
        if indice != -1:
            return indice
        mostrar_error(mensaje_no_existe)


def mostrar_datos_contacto(contacto):
    """Despliega los datos de un contacto (excepto teléfono y área)."""
    print(etiqueta("Tipo teléfono") + contacto[TIPO] + " - " +
          descripcion_tipo(contacto[TIPO]))
    print(etiqueta("Nombre contacto") + contacto[NOMBRE])
    print(etiqueta("Correo electrónico") + contacto[CORREO])
    print(etiqueta("Dirección física") + contacto[DIRECCION])
    print(etiqueta("Fecha de nacimiento") + texto_fecha(contacto[FECHA]))
    print(etiqueta("Pasatiempos") + contacto[PASATIEMPOS])
    print(etiqueta("Notas") + contacto[NOTAS])


def grupos_de_contacto(grupos, contactos_por_grupo, telefono, area):
    """Retorna la lista de nombres de grupos a los que pertenece un
    contacto (se usa para la integridad referencial y para los filtros)."""
    resultado = []
    for i in range(len(grupos)):
        if (telefono, area) in contactos_por_grupo[i]:
            resultado.append(grupos[i])
    return resultado


def agregar_contactos(contactos, areas, configuracion):
    """Opción 3.1: agrega un contacto con teléfono (número + área) único."""
    while True:
        mostrar_encabezado("REGISTRAR CONTACTOS: AGREGAR")
        print("  (Digite C en Teléfono para regresar al menú anterior)\n")
        while True:
            telefono = leer_telefono(areas, configuracion)
            if telefono is None:
                return
            if buscar_contacto(contactos, telefono[0], telefono[1]) == -1:
                break
            mostrar_error("ESTE TELÉFONO YA ESTÁ REGISTRADO, NO SE PUEDE "
                          "AGREGAR")
        tipo = leer_tipo_telefono(
            f"Tipo teléfono (M,C,T,O) [{configuracion[1]}]", configuracion[1])
        nombre = leer_texto("Nombre contacto", 1, 50)
        correo = leer_correo("Correo electrónico")
        direccion = leer_texto("Dirección física", 0, 80)
        fecha = leer_fecha("Fecha de nacimiento")
        pasatiempos = leer_texto("Pasatiempos", 0, 60)
        notas = leer_texto("Notas", 0, 60)
        if leer_opcion_aceptar_cancelar():
            contactos.append([telefono[0], telefono[1], tipo, nombre, correo,
                              direccion, fecha, pasatiempos, notas])
            mostrar_mensaje("CONTACTO AGREGADO")


def consultar_contactos(contactos, areas, configuracion):
    """Opción 3.2: despliega los datos de un contacto (sin cambiarlos)."""
    while True:
        mostrar_encabezado("REGISTRAR CONTACTOS: CONSULTAR")
        print("  (Digite C en Teléfono para regresar al menú anterior)\n")
        indice = leer_contacto_registrado(
            contactos, areas, configuracion,
            "ESTE CONTACTO NO ESTÁ REGISTRADO, NO SE PUEDE CONSULTAR")
        if indice == -1:
            return
        mostrar_datos_contacto(contactos[indice])
        leer_aceptar()


def modificar_contactos(contactos, areas, configuracion):
    """Opción 3.3: muestra cada dato y lee su nuevo valor (<Enter> lo deja
    igual). El teléfono y el área no se modifican porque identifican al
    contacto. Los cambios se aplican solo si el usuario acepta."""
    while True:
        mostrar_encabezado("REGISTRAR CONTACTOS: MODIFICAR")
        print("  (Digite C en Teléfono para regresar al menú anterior)")
        print("  (Dé <Enter> en MODIFICACIÓN para dejar el dato igual)\n")
        indice = leer_contacto_registrado(
            contactos, areas, configuracion,
            "ESTE CONTACTO NO ESTÁ REGISTRADO, NO SE PUEDE MODIFICAR")
        if indice == -1:
            return
        contacto = contactos[indice]
        print(etiqueta("Tipo teléfono") + contacto[TIPO])
        print(etiqueta("Nombre contacto") + contacto[NOMBRE])
        nombre = leer_texto("MODIFICACIÓN", 1, 50, contacto[NOMBRE])
        print(etiqueta("Correo electrónico") + contacto[CORREO])
        correo = leer_correo("MODIFICACIÓN", contacto[CORREO])
        print(etiqueta("Dirección física") + contacto[DIRECCION])
        direccion = leer_texto("MODIFICACIÓN", 0, 80, contacto[DIRECCION])
        print(etiqueta("Fecha de nacimiento") + texto_fecha(contacto[FECHA]))
        fecha = leer_fecha("MODIFICACIÓN", contacto[FECHA])
        print(etiqueta("Pasatiempos") + contacto[PASATIEMPOS])
        pasatiempos = leer_texto("MODIFICACIÓN", 0, 60, contacto[PASATIEMPOS])
        print(etiqueta("Notas") + contacto[NOTAS])
        notas = leer_texto("MODIFICACIÓN", 0, 60, contacto[NOTAS])
        if leer_opcion_aceptar_cancelar():
            contacto[NOMBRE] = nombre
            contacto[CORREO] = correo
            contacto[DIRECCION] = direccion
            contacto[FECHA] = fecha
            contacto[PASATIEMPOS] = pasatiempos
            contacto[NOTAS] = notas
            mostrar_mensaje("CONTACTO MODIFICADO")


def eliminar_contactos(contactos, areas, configuracion, grupos,
                       contactos_por_grupo):
    """Opción 3.4: elimina un contacto. Por integridad referencial no se
    permite eliminar un contacto que pertenezca a algún grupo."""
    while True:
        mostrar_encabezado("REGISTRAR CONTACTOS: ELIMINAR")
        print("  (Digite C en Teléfono para regresar al menú anterior)\n")
        indice = leer_contacto_registrado(
            contactos, areas, configuracion,
            "ESTE CONTACTO NO ESTÁ REGISTRADO, NO SE PUEDE ELIMINAR")
        if indice == -1:
            return
        contacto = contactos[indice]
        mostrar_datos_contacto(contacto)
        if not leer_opcion_aceptar_cancelar():
            continue
        sus_grupos = grupos_de_contacto(grupos, contactos_por_grupo,
                                        contacto[TEL], contacto[AREA])
        if sus_grupos:
            mostrar_mensaje("ESTE CONTACTO PERTENECE A LOS GRUPOS: " +
                            ", ".join(sus_grupos) + ". NO SE PUEDE ELIMINAR "
                            "(PRIMERO ELIMÍNELO DE ESOS GRUPOS)")
        elif confirmar_eliminacion():
            del contactos[indice]
            mostrar_mensaje("CONTACTO ELIMINADO")


def registrar_contactos(contactos, areas, configuracion, grupos,
                        contactos_por_grupo):
    """Opción 3 del menú principal: submenú de mantenimiento de contactos.
    Requiere que antes se haya hecho la configuración (opción 2)."""
    if configuracion[0] is None:
        mostrar_mensaje("ANTES DE REGISTRAR CONTACTOS DEBE HACER LA "
                        "CONFIGURACIÓN DE LA LISTA (OPCIÓN 2)")
        return
    while True:
        opcion = mostrar_menu("REGISTRAR CONTACTOS", [
            "Agregar contactos", "Consultar contactos", "Modificar contactos",
            "Eliminar contactos"])
        match opcion:
            case "1":
                agregar_contactos(contactos, areas, configuracion)
            case "2":
                consultar_contactos(contactos, areas, configuracion)
            case "3":
                modificar_contactos(contactos, areas, configuracion)
            case "4":
                eliminar_contactos(contactos, areas, configuracion, grupos,
                                   contactos_por_grupo)
            case "0":
                return
            case _:
                mostrar_error("ESTA OPCIÓN NO EXISTE EN EL MENÚ")
                pausar()


# =============================================================================
#                     4. ADMINISTRAR GRUPOS DE CONTACTOS
# =============================================================================
def buscar_grupo(grupos, nombre):
    """Busca un grupo por nombre sin importar mayúsculas/minúsculas.
    Salida: índice del grupo, o -1 si no existe."""
    for i in range(len(grupos)):
        if grupos[i].upper() == nombre.upper():
            return i
    return -1


def leer_nombre_grupo(nombre_dato):
    """Pide un nombre de grupo de 1 a 40 caracteres (se guarda en
    mayúscula). Salida: el nombre, o None si el usuario digita C."""
    while True:
        nombre = input(etiqueta(nombre_dato)).strip().upper()
        if nombre == "C":
            return None
        if 1 <= len(nombre) <= 40:
            return nombre
        mostrar_error("EL NOMBRE DEL GRUPO DEBE TENER ENTRE 1 Y 40 "
                      "CARACTERES")


def leer_grupo_registrado(grupos, mensaje_no_existe):
    """Pide un nombre de grupo hasta que exista.
    Salida: índice del grupo, o -1 si el usuario cancela."""
    while True:
        nombre = leer_nombre_grupo("Nombre del grupo")
        if nombre is None:
            return -1
        indice = buscar_grupo(grupos, nombre)
        if indice != -1:
            return indice
        mostrar_error(mensaje_no_existe)


def agregar_grupos(grupos, contactos_por_grupo):
    """Opción 4.1: agrega un grupo nuevo; para mantener la relación 1:1
    también agrega una lista vacía en contactos_por_grupo."""
    while True:
        mostrar_encabezado("ADMINISTRAR GRUPOS DE CONTACTOS: AGREGAR GRUPOS")
        print("  (Digite C en Nombre del grupo para regresar)\n")
        while True:
            nombre = leer_nombre_grupo("Nombre del grupo")
            if nombre is None:
                return
            if buscar_grupo(grupos, nombre) == -1:
                break
            mostrar_error("ESTE GRUPO YA ESTÁ REGISTRADO, NO SE PUEDE AGREGAR")
        if leer_opcion_aceptar_cancelar():
            grupos.append(nombre)
            contactos_por_grupo.append([])
            mostrar_mensaje("GRUPO AGREGADO")


def agregar_contactos_grupo(grupos, contactos_por_grupo, contactos, areas,
                            configuracion):
    """Opción 4.2: agrega a un grupo un contacto que exista en la lista
    contactos (integridad referencial) y que no esté ya en el grupo."""
    while True:
        mostrar_encabezado("ADMINISTRAR GRUPOS DE CONTACTOS: "
                           "AGREGAR CONTACTOS A LOS GRUPOS")
        print("  (Digite C en Nombre del grupo para regresar)\n")
        indice_grupo = leer_grupo_registrado(
            grupos, "ESTE GRUPO NO EXISTE, NO PUEDE AGREGARLE CONTACTOS")
        if indice_grupo == -1:
            return
        while True:
            telefono = leer_telefono(areas, configuracion)
            if telefono is None:                   # C: vuelve a pedir grupo
                break
            indice = buscar_contacto(contactos, telefono[0], telefono[1])
            if indice == -1:
                mostrar_error("ESTE CONTACTO NO EXISTE, NO PUEDE AGREGARLO AL "
                              "GRUPO")
            elif telefono in contactos_por_grupo[indice_grupo]:
                mostrar_error("ESTE CONTACTO YA ESTÁ EN EL GRUPO")
            else:
                print(etiqueta("Nombre contacto") + contactos[indice][NOMBRE])
                if leer_opcion_aceptar_cancelar():
                    contactos_por_grupo[indice_grupo].append(telefono)
                    mostrar_mensaje("CONTACTO AGREGADO AL GRUPO")
                break


def modificar_grupos(grupos, contactos_por_grupo):
    """Opción 4.3: cambia el nombre de un grupo. Si el nuevo nombre ya
    existe, los contactos del grupo se pasan a ese grupo (sin repetir) y
    el grupo modificado se borra de grupos y contactos_por_grupo."""
    while True:
        mostrar_encabezado("ADMINISTRAR GRUPOS DE CONTACTOS: MODIFICAR GRUPOS")
        print("  (Digite C en Nombre del grupo para regresar)")
        print("  (Dé <Enter> en MODIFICACIÓN para dejar el nombre igual)\n")
        indice = leer_grupo_registrado(
            grupos, "GRUPO NO ESTÁ REGISTRADO, NO SE PUEDE MODIFICAR")
        if indice == -1:
            return
        nuevo = input(etiqueta("MODIFICACIÓN")).strip().upper()
        while len(nuevo) > 40:
            mostrar_error("EL NOMBRE DEL GRUPO DEBE TENER ENTRE 1 Y 40 "
                          "CARACTERES")
            nuevo = input(etiqueta("MODIFICACIÓN")).strip().upper()
        if nuevo == "":
            nuevo = grupos[indice]
            print(etiqueta("") + nuevo)
        destino = buscar_grupo(grupos, nuevo)
        if destino != -1 and destino != indice:
            mostrar_error("GRUPO YA EXISTE, EN CASO DE ACEPTAR LA OPERACIÓN "
                          "LOS CONTACTOS SE LE AGREGARÁN")
        if not leer_opcion_aceptar_cancelar() or destino == indice:
            continue
        if destino == -1:                          # nombre nuevo: renombrar
            grupos[indice] = nuevo
        else:                                      # unir con grupo existente
            for telefono in contactos_por_grupo[indice]:
                if telefono not in contactos_por_grupo[destino]:
                    contactos_por_grupo[destino].append(telefono)
            del grupos[indice]
            del contactos_por_grupo[indice]
        mostrar_mensaje("GRUPO MODIFICADO")


def eliminar_grupos(grupos, contactos_por_grupo):
    """Opción 4.4: elimina un grupo y su lista de contactos (ambas listas,
    para mantener la relación 1:1). Pide confirmación."""
    while True:
        mostrar_encabezado("ADMINISTRAR GRUPOS DE CONTACTOS: ELIMINAR GRUPOS")
        print("  (Digite C en Nombre del grupo para regresar)\n")
        indice = leer_grupo_registrado(
            grupos, "ESTE GRUPO NO ESTÁ REGISTRADO, NO SE PUEDE ELIMINAR")
        if indice == -1:
            return
        print(etiqueta("Contactos en el grupo") +
              str(len(contactos_por_grupo[indice])))
        if leer_opcion_aceptar_cancelar() and confirmar_eliminacion():
            del grupos[indice]
            del contactos_por_grupo[indice]
            mostrar_mensaje("GRUPO ELIMINADO")


def eliminar_contactos_grupo(grupos, contactos_por_grupo, contactos, areas,
                             configuracion):
    """Opción 4.5: elimina un contacto de un grupo (no de la lista
    contactos). Pide confirmación."""
    while True:
        mostrar_encabezado("ADMINISTRAR GRUPOS DE CONTACTOS: "
                           "ELIMINAR CONTACTOS DE LOS GRUPOS")
        print("  (Digite C en Nombre del grupo para regresar)\n")
        indice_grupo = leer_grupo_registrado(
            grupos, "ESTE GRUPO NO EXISTE, NO PUEDE ELIMINARLE CONTACTOS")
        if indice_grupo == -1:
            return
        while True:
            telefono = leer_telefono(areas, configuracion)
            if telefono is None:
                break
            if telefono not in contactos_por_grupo[indice_grupo]:
                mostrar_error("ESTE CONTACTO NO EXISTE EN EL GRUPO, NO PUEDE "
                              "ELIMINARLO")
                continue
            indice = buscar_contacto(contactos, telefono[0], telefono[1])
            print(etiqueta("Nombre contacto") + contactos[indice][NOMBRE])
            if leer_opcion_aceptar_cancelar() and confirmar_eliminacion():
                contactos_por_grupo[indice_grupo].remove(telefono)
                mostrar_mensaje("CONTACTO ELIMINADO DEL GRUPO")
            break


def administrar_grupos(grupos, contactos_por_grupo, contactos, areas,
                       configuracion):
    """Opción 4 del menú principal: submenú de grupos de contactos."""
    while True:
        opcion = mostrar_menu("ADMINISTRAR GRUPOS DE CONTACTOS", [
            "Agregar grupos", "Agregar contactos a los grupos",
            "Modificar grupos", "Eliminar grupos",
            "Eliminar contactos de los grupos"])
        match opcion:
            case "1":
                agregar_grupos(grupos, contactos_por_grupo)
            case "2":
                agregar_contactos_grupo(grupos, contactos_por_grupo,
                                        contactos, areas, configuracion)
            case "3":
                modificar_grupos(grupos, contactos_por_grupo)
            case "4":
                eliminar_grupos(grupos, contactos_por_grupo)
            case "5":
                eliminar_contactos_grupo(grupos, contactos_por_grupo,
                                         contactos, areas, configuracion)
            case "0":
                return
            case _:
                mostrar_error("ESTA OPCIÓN NO EXISTE EN EL MENÚ")
                pausar()


# =============================================================================
#                   5. LISTA DE CONTACTOS (ARCHIVO PDF)
# =============================================================================
# ----------------------- Filtros con comodín % --------------------------------
def patron_a_regex(patron):
    """Convierte un filtro con comodines % en una expresión regular.
    Se parte el filtro por cada %, cada parte se 'escapa' (para que
    caracteres como . o ( no tengan significado especial) y las partes se
    unen con '.*', que en regex significa 'cero o más caracteres'.
    Ejemplo: 'william%mata' -> 'william.*mata'."""
    partes = patron.split("%")
    for i in range(len(partes)):
        partes[i] = re.escape(partes[i])
    return ".*".join(partes)


def cumple_filtro(valor, patron):
    """True si el valor cumple el filtro. Filtro vacío = cualquier valor.
    Sin % se exige el valor exacto. No distingue mayúsculas/minúsculas."""
    if patron == "":
        return True
    return re.fullmatch(patron_a_regex(patron), str(valor),
                        re.IGNORECASE | re.DOTALL) is not None


def cumple_filtro_grupo(nombres_grupos, patron):
    """True si alguno de los grupos del contacto cumple el filtro."""
    if patron == "":
        return True
    for nombre in nombres_grupos:
        if cumple_filtro(nombre, patron):
            return True
    return False


def filtrar_contactos(contactos, grupos, contactos_por_grupo, filtros):
    """Retorna los contactos que cumplen TODOS los filtros.
    filtros = (nombre, telefono, area, fecha, pasatiempos, grupo)."""
    resultado = []
    for contacto in contactos:
        sus_grupos = grupos_de_contacto(grupos, contactos_por_grupo,
                                        contacto[TEL], contacto[AREA])
        if (cumple_filtro(contacto[NOMBRE], filtros[0])
                and cumple_filtro(contacto[TEL], filtros[1])
                and cumple_filtro(contacto[AREA], filtros[2])
                and cumple_filtro(texto_fecha(contacto[FECHA]), filtros[3])
                and cumple_filtro(contacto[PASATIEMPOS], filtros[4])
                and cumple_filtro_grupo(sus_grupos, filtros[5])):
            resultado.append(contacto)
    return resultado


# ------------------- Generación del archivo PDF ------------------------------
# El PDF se escribe directamente siguiendo la estructura del formato
# (encabezado, objetos, tabla xref y trailer), sin bibliotecas externas.
ANCHO_PAGINA, ALTO_PAGINA = 792, 612        # carta horizontal, en puntos
MARGEN = 28
TAMANO_LETRA = 6.5                          # letra Courier (ancho fijo)
ANCHO_CARACTER = TAMANO_LETRA * 0.6         # en Courier cada letra = 0.6
ALTO_LINEA = 8.5
COLUMNAS_PDF = (("Nombre contacto", 24), ("Teléfono (área)", 17),
                ("Tipo", 8), ("Correo electrónico", 26),
                ("Dirección física", 28), ("F. nacim.", 10),
                ("Pasatiempos", 28), ("Notas", 28))


def escapar_pdf(texto):
    """Escapa los caracteres especiales de los textos dentro de un PDF."""
    return texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def comando_texto(x, y, fuente, tamano, texto):
    """Comando PDF para escribir un texto en la posición (x, y)."""
    return (f"BT /{fuente} {tamano} Tf {x:.1f} {y:.1f} Td "
            f"({escapar_pdf(texto)}) Tj ET\n")


def comando_linea(x1, y1, x2, y2):
    """Comando PDF para dibujar una línea gris."""
    return f"0.6 G 0.4 w {x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S 0 G\n"


def partir_texto(texto, ancho):
    """Divide un texto en líneas de máximo 'ancho' caracteres, sin cortar
    palabras (salvo que una palabra sola sea más larga que el ancho)."""
    lineas = []
    actual = ""
    for palabra in texto.split():
        while len(palabra) > ancho:
            if actual:
                lineas.append(actual)
                actual = ""
            lineas.append(palabra[:ancho])
            palabra = palabra[ancho:]
        if actual == "":
            actual = palabra
        elif len(actual) + 1 + len(palabra) <= ancho:
            actual += " " + palabra
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas if lineas else [""]


def encabezado_pagina_pdf(numero, texto_filtros, total_contactos):
    """Dibuja título, filtros y títulos de columnas de una página.
    Salida: (comandos, posición y donde empiezan las filas)."""
    ahora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    comandos = comando_texto(MARGEN, ALTO_PAGINA - 40, "F3", 15,
                             NOMBRE_PROGRAMA + " - LISTA DE CONTACTOS")
    comandos += comando_texto(MARGEN, ALTO_PAGINA - 56, "F1", 8,
                              f"Emitido: {ahora}    Contactos: "
                              f"{total_contactos}    Página {numero}")
    comandos += comando_texto(MARGEN, ALTO_PAGINA - 68, "F1", 8,
                              "Filtros: " + texto_filtros)
    y = ALTO_PAGINA - 88
    x = MARGEN
    for titulo, ancho in COLUMNAS_PDF:
        comandos += comando_texto(x, y, "F2", TAMANO_LETRA, titulo)
        x += (ancho + 1) * ANCHO_CARACTER
    comandos += comando_linea(MARGEN, y - 3, ANCHO_PAGINA - MARGEN, y - 3)
    return comandos, y - ALTO_LINEA - 4


def generar_paginas_pdf(filas, texto_filtros):
    """Recibe las filas (listas de 8 textos) y arma los comandos de dibujo
    de cada página; si una fila no cabe se crea una página nueva.
    Salida: lista con los comandos de cada página."""
    paginas = []
    comandos, y = encabezado_pagina_pdf(1, texto_filtros, len(filas))
    if not filas:
        comandos += comando_texto(MARGEN, y, "F1", 9, "No hay contactos que "
                                  "cumplan con los filtros indicados.")
    for fila in filas:
        celdas = []
        for i in range(len(COLUMNAS_PDF)):
            celdas.append(partir_texto(fila[i], COLUMNAS_PDF[i][1]))
        lineas_fila = max(len(celda) for celda in celdas)
        if y - lineas_fila * ALTO_LINEA < MARGEN:          # no cabe
            paginas.append(comandos)
            comandos, y = encabezado_pagina_pdf(len(paginas) + 1,
                                                texto_filtros, len(filas))
        x = MARGEN
        for i in range(len(celdas)):
            for j in range(len(celdas[i])):
                comandos += comando_texto(x, y - j * ALTO_LINEA, "F1",
                                          TAMANO_LETRA, celdas[i][j])
            x += (COLUMNAS_PDF[i][1] + 1) * ANCHO_CARACTER
        y -= lineas_fila * ALTO_LINEA
        comandos += comando_linea(MARGEN, y + 5, ANCHO_PAGINA - MARGEN, y + 5)
        y -= 3
    paginas.append(comandos)
    return paginas


def escribir_pdf(ruta, paginas):
    """Escribe el archivo PDF. Objetos: 1 catálogo, 2 árbol de páginas,
    3-5 fuentes y, por cada página, su objeto página y su contenido.
    Al final se escribe la tabla xref con la posición de cada objeto."""
    cantidad = len(paginas)
    hijos = " ".join(f"{6 + 2 * i} 0 R" for i in range(cantidad))
    objetos = [b"<< /Type /Catalog /Pages 2 0 R >>",
               f"<< /Type /Pages /Kids [{hijos}] /Count {cantidad} >>"
               .encode()]
    for fuente in ("Courier", "Courier-Bold", "Helvetica-Bold"):
        objetos.append(f"<< /Type /Font /Subtype /Type1 /BaseFont /{fuente} "
                       f"/Encoding /WinAnsiEncoding >>".encode())
    for i in range(cantidad):
        contenido = paginas[i].encode("cp1252", errors="replace")
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {ANCHO_PAGINA} "
            f"{ALTO_PAGINA}] /Resources << /Font << /F1 3 0 R /F2 4 0 R "
            f"/F3 5 0 R >> >> /Contents {7 + 2 * i} 0 R >>".encode())
        objetos.append(f"<< /Length {len(contenido)} >>\nstream\n".encode()
                       + contenido + b"\nendstream")
    salida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    posiciones = []
    for i in range(len(objetos)):
        posiciones.append(len(salida))
        salida += f"{i + 1} 0 obj\n".encode() + objetos[i] + b"\nendobj\n"
    inicio_xref = len(salida)
    salida += f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode()
    for posicion in posiciones:
        salida += f"{posicion:010d} 00000 n \n".encode()
    salida += (f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\n"
               f"startxref\n{inicio_xref}\n%%EOF\n").encode()
    with open(ruta, "wb") as archivo:
        archivo.write(salida)


def abrir_archivo(ruta):
    """Intenta abrir un archivo con el programa predeterminado del sistema."""
    try:
        if os.name == "nt":
            os.startfile(ruta)
        else:
            webbrowser.open("file://" + ruta)
    except OSError:
        pass


def emitir_pdf(seleccionados, areas, texto_filtros):
    """Arma las filas del listado, escribe el PDF y retorna su ruta."""
    filas = []
    for c in seleccionados:
        filas.append([c[NOMBRE], f"{c[TEL]} ({c[AREA]} "
                      f"{nombre_area(areas, c[AREA])})",
                      descripcion_tipo(c[TIPO]), c[CORREO], c[DIRECCION],
                      texto_fecha(c[FECHA]), c[PASATIEMPOS], c[NOTAS]])
    nombre = ("lista_contactos_" +
              datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".pdf")
    ruta = os.path.join(CARPETA_PROGRAMA, nombre)
    escribir_pdf(ruta, generar_paginas_pdf(filas, texto_filtros))
    return ruta


def lista_contactos(contactos, areas, grupos, contactos_por_grupo):
    """Opción 5: pide los 6 filtros y emite en PDF los contactos que los
    cumplen todos. CANCELAR vuelve a mostrar la pantalla con los filtros
    vacíos; C en el primer filtro regresa al menú principal."""
    nombres = ("Nombre contacto", "Teléfono", "Área", "Fecha de nacimiento",
               "Pasatiempos", "Grupo")
    while True:
        mostrar_encabezado("LISTA DE CONTACTOS")
        print("  Deje un filtro vacío para aceptar cualquier valor. Use % como")
        print("  comodín (cero o más caracteres). Ej.: %castillo%")
        print("  (Digite solo C en Nombre contacto para regresar al menú)\n")
        print("  FILTROS:")
        filtros = []
        for nombre in nombres:
            filtros.append(input(etiqueta(nombre)).strip())
            if len(filtros) == 1 and filtros[0].upper() == "C":
                return
        if not leer_opcion_aceptar_cancelar():
            continue
        seleccionados = filtrar_contactos(contactos, grupos,
                                          contactos_por_grupo, filtros)
        partes = []
        for i in range(len(nombres)):
            if filtros[i] != "":
                partes.append(f"{nombres[i]} = '{filtros[i]}'")
        texto_filtros = "; ".join(partes) if partes else "ninguno (todos)"
        ruta = emitir_pdf(seleccionados, areas, texto_filtros)
        print(f"\n  Contactos que cumplen los filtros: {len(seleccionados)}")
        print("  Listado emitido en: " + ruta)
        abrir_archivo(ruta)
        pausar()


# =============================================================================
#                          6. AYUDA  /  7. ACERCA DE
# =============================================================================
MANUAL_TXT = "manual_de_usuario_contactos.txt"
MANUAL_PDF = "manual_de_usuario_contactos.pdf"
LINEAS_POR_PANTALLA = 20


def ayuda():
    """Opción 6: despliega en pantalla el manual de usuario (archivo de
    texto en la carpeta del programa), de 20 líneas en 20 líneas.
    Al final ofrece abrir la versión PDF del manual (con imágenes)."""
    ruta = os.path.join(CARPETA_PROGRAMA, MANUAL_TXT)
    try:
        with open(ruta, encoding="utf-8") as archivo:
            lineas = archivo.read().splitlines()
    except OSError:
        mostrar_mensaje("NO SE ENCONTRÓ EL ARCHIVO " + MANUAL_TXT)
        return
    for inicio in range(0, len(lineas), LINEAS_POR_PANTALLA):
        mostrar_encabezado("AYUDA - MANUAL DE USUARIO")
        for linea in lineas[inicio:inicio + LINEAS_POR_PANTALLA]:
            print("  " + linea)
        if inicio + LINEAS_POR_PANTALLA < len(lineas):
            if input("\n  <Enter> siguiente página, S salir: ").strip() \
                    .upper() == "S":
                break
    ruta_pdf = os.path.join(CARPETA_PROGRAMA, MANUAL_PDF)
    if os.path.exists(ruta_pdf):
        if input("\n  ¿Desea abrir el manual en PDF (con imágenes)? (SI/NO) "
                 ).strip().upper() in ("SI", "SÍ"):
            abrir_archivo(ruta_pdf)
    else:
        pausar()


def acerca_de():
    """Opción 7: muestra los datos del programa."""
    mostrar_encabezado("ACERCA DE")
    print(etiqueta("Programa") + NOMBRE_PROGRAMA)
    print(etiqueta("Versión") + VERSION)
    print(etiqueta("Fecha de creación") + FECHA_CREACION)
    print(etiqueta("Autor") + AUTOR)
    print(etiqueta("Curso") + "Taller de Programación")
    print(etiqueta("Institución") + "Tecnológico de Costa Rica")
    print(etiqueta("Lenguaje") + "Python 3.14")
    pausar()


# =============================================================================
#                              PROGRAMA PRINCIPAL
# =============================================================================
def main():
    """Crea las estructuras de datos, despliega el menú principal y llama a
    cada funcionalidad según la opción escogida (estructura match-case)."""
    areas = list(AREAS_PRUEBA)
    configuracion = [None, None]   # [área por omisión, tipo por omisión]
    contactos = [list(contacto) for contacto in CONTACTOS_PRUEBA]
    grupos = list(GRUPOS_PRUEBA)
    contactos_por_grupo = [list(lista) for lista in CONTACTOS_POR_GRUPO_PRUEBA]

    while True:
        opcion = mostrar_menu("MENÚ PRINCIPAL", [
            "Registrar áreas", "Configuración de lista de contactos",
            "Registrar contactos", "Administrar grupos de contactos",
            "Lista de contactos", "Ayuda", "Acerca de"])
        match opcion:
            case "1":
                registrar_areas(areas, contactos, configuracion)
            case "2":
                configurar_lista(areas, configuracion)
            case "3":
                registrar_contactos(contactos, areas, configuracion, grupos,
                                    contactos_por_grupo)
            case "4":
                administrar_grupos(grupos, contactos_por_grupo, contactos,
                                   areas, configuracion)
            case "5":
                lista_contactos(contactos, areas, grupos, contactos_por_grupo)
            case "6":
                ayuda()
            case "7":
                acerca_de()
            case "0":
                print("\n  Gracias por usar la " + NOMBRE_PROGRAMA + ".\n")
                break
            case _:
                mostrar_error("ESTA OPCIÓN NO EXISTE EN EL MENÚ")
                pausar()


if __name__ == "__main__":
    main()
