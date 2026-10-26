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
def administrar_grupos(grupos, contactos_por_grupo, contactos, areas,
                       configuracion):
    """(Caja negra: pendiente de desarrollo)."""
    mostrar_mensaje("FUNCIONALIDAD EN DESARROLLO")


# =============================================================================
#                   5. LISTA DE CONTACTOS (ARCHIVO PDF)
# =============================================================================
def lista_contactos(contactos, areas, grupos, contactos_por_grupo):
    """(Caja negra: pendiente de desarrollo)."""
    mostrar_mensaje("FUNCIONALIDAD EN DESARROLLO")


# =============================================================================
#                          6. AYUDA  /  7. ACERCA DE
# =============================================================================
def ayuda():
    """(Caja negra: pendiente de desarrollo)."""
    mostrar_mensaje("FUNCIONALIDAD EN DESARROLLO")


def acerca_de():
    """(Caja negra: pendiente de desarrollo)."""
    mostrar_mensaje("FUNCIONALIDAD EN DESARROLLO")


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
