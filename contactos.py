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
def registrar_contactos(contactos, areas, configuracion, grupos,
                        contactos_por_grupo):
    """(Caja negra: pendiente de desarrollo)."""
    mostrar_mensaje("FUNCIONALIDAD EN DESARROLLO")


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
