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
def registrar_areas(areas, contactos, configuracion):
    """(Caja negra: pendiente de desarrollo)."""
    mostrar_mensaje("FUNCIONALIDAD EN DESARROLLO")


# =============================================================================
#                 2. CONFIGURACIÓN DE LA LISTA DE CONTACTOS
# =============================================================================
def configurar_lista(areas, configuracion):
    """(Caja negra: pendiente de desarrollo)."""
    mostrar_mensaje("FUNCIONALIDAD EN DESARROLLO")


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
