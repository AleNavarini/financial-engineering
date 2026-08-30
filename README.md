# Ingenieria Financiera - UCEMA

Este proyecto fue desarrollado como trabajo final de la materia Ingeniería Financiera de UCEMA, dictada por el profesor Mariano Alejandro Kruskevich, por los alumnos Alejandro Navarini y Tomás Pérez.

Es una aplicación de Python desarrollada con FastAPI que incluye un dashboard web estático. Permite consultar información de LSEG Workspace mediante el proxy local que Workspace proporciona para las sesiones de escritorio.

Esta guía explica cómo instalar y ejecutar el proyecto en Windows. Está dirigida a personas que no necesitan conocimientos técnicos previos.

## Antes de comenzar

Se necesita lo siguiente:

- Una computadora con Windows.
- Una cuenta activa de LSEG Workspace.
- Un App Key de LSEG con los permisos indicados en esta guía.
- Permisos para instalar programas en la computadora.

## Instalación

### 1. Descargar el proyecto

1. Abrir el [repositorio del proyecto en GitHub](https://github.com/AleNavarini/financial-engineering).
2. Hacer clic en el botón verde `<> Code`.
3. Seleccionar `Download ZIP`.
4. Guardar el archivo ZIP en una ubicación fácil de encontrar, por ejemplo, el Escritorio o la carpeta Descargas.
5. Abrir la carpeta donde se guardó el archivo.
6. Hacer clic derecho sobre el archivo ZIP y seleccionar **Extraer todo**.
7. Confirmar la extracción.

Al finalizar, se tendrá una carpeta llamada `financial-engineering`. Esta es la carpeta del proyecto. Todos los pasos siguientes deben realizarse dentro de ella.

### 2. Instalar Python

Python es el programa que permite ejecutar esta herramienta.

> **Importante:** se debe instalar Python de **64 bits**. El proyecto fue probado con Python 3.12 de 64 bits. Es posible que versiones posteriores a Python 3.12 también funcionen, pero todavía no han sido comprobadas.

1. Descargar e instalar [Python 3.12.9](https://www.python.org/ftp/python/3.12.9/python-3.12.9.exe).
2. En la primera pantalla del instalador, marcar la opción **Add python.exe to PATH**.
3. Hacer clic en **Install Now**.
4. Esperar a que finalice la instalación y cerrar el instalador.

La opción **Add python.exe to PATH** es importante. Permite que el proyecto encuentre Python automáticamente cuando se ejecute.

### 3. Instalar LSEG Workspace

Instalar **LSEG Workspace** en la computadora si todavía no está instalado. Se puede descargar desde la [página oficial de LSEG](https://www.lseg.com/en/data-analytics/products/workspace/download-workspace). La aplicación de escritorio es necesaria para que el proyecto pueda consultar los datos de mercado.

Después de instalarlo, no es necesario ejecutar el proyecto todavía. Primero hay que configurar el App Key.

### 4. Obtener el App Key

El App Key es un código que identifica a esta aplicación frente a LSEG. No es la contraseña de LSEG Workspace y no debe compartirse públicamente.

1. Abrir [App Key Generator](https://amers1-apps.platform.refinitiv.com/apps/AppkeyGenerator).
2. Iniciar sesión con la cuenta correspondiente.
3. Revisar los App Keys disponibles.
4. El usuario 3 de UCEMA ya tiene App Keys creados. Si no hay uno disponible o se utiliza otro usuario, es necesario crear uno nuevo.
5. Verificar que el App Key tenga permisos para:
   - **Side by Side API**
   - **EDP API**
   - **Eikon Data API**
6. Copiar el valor que aparece en la columna `API Key`.

Guardar este valor temporalmente. Se necesitará en el paso siguiente.

### 5. Desactivar Smart App Control

Windows puede bloquear una dependencia necesaria para ejecutar el proyecto. Por este motivo, es necesario desactivar **Smart App Control** en la computadora donde se instalará la herramienta.

1. Abrir el menú Inicio de Windows.
2. Buscar `Smart App Control`.
3. Abrir la configuración que aparece en los resultados.
4. Cambiar la opción de `On` a `Off`.
5. Si Windows solicita confirmación, confirmar el cambio.

### 6. Configurar el App Key

Ahora es necesario guardar el App Key en el archivo de configuración del proyecto.

1. Abrir la carpeta `financial-engineering` que se creó al extraer el archivo ZIP.
2. Buscar el archivo `.env.example`.
3. Hacer una copia del archivo y cambiar el nombre de la copia a `.env`.
4. Si Windows muestra una advertencia sobre cambiar la extensión del archivo, confirmar la acción.
5. Abrir `.env` con el Bloc de notas.
6. Buscar esta línea:

   ```env
   LSEG_APP_KEY=YOUR_APP_KEY
   ```

7. Reemplazar solamente `YOUR_APP_KEY` por el valor copiado desde App Key Generator. El resultado debe verse así:

   ```env
   LSEG_APP_KEY=tuvaloraca
   ```

8. Guardar el archivo y cerrar el Bloc de notas.

No agregar comillas ni espacios antes o después del App Key. No compartir el archivo `.env` ni subirlo a Internet, porque contiene una credencial de acceso.

## Ejecutar el programa

Antes de iniciar el programa, confirmar que la instalación terminó y que el archivo `.env` está dentro de la carpeta principal `financial-engineering`.

1. Abrir **LSEG Workspace**.
2. Iniciar sesión con la cuenta de LSEG.
3. Esperar a que Workspace termine de cargar y muestre la pantalla principal.
4. Mantener LSEG Workspace abierto.
5. Abrir la carpeta `financial-engineering`.
6. Hacer doble clic en el archivo `start.cmd`.
7. Si Windows muestra una ventana de seguridad o solicita permiso de acceso, permitir la ejecución.
8. Esperar mientras se prepara el entorno y se inicia el programa. La primera ejecución puede tardar unos minutos.

Cuando el programa esté listo, abrir el siguiente enlace en el navegador:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

Esta dirección apunta al programa que se está ejecutando en tu propia computadora. Para que el dashboard funcione, LSEG Workspace debe permanecer abierto y con la sesión iniciada.

## Detener el programa

Para cerrar el programa, volver a la ventana negra que se abrió al ejecutar `start.cmd` y presionar `Ctrl + C`. Se puede cerrar LSEG Workspace después de detener el programa.
