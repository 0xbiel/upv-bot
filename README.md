<img src="assets/header.svg" width="1500px"/>

----
# UPV-BOT

## Descripción
UPV-BOT es una herramienta automatizada desarrollada en Python para gestionar reservas en la intranet de la UPV. Permite listar horarios disponibles, realizar reservas de forma sencilla o mediante fuerza bruta, y gestionar múltiples reservas simultáneamente.

## Requisitos
- Python 3.x
- Librerías especificadas en [`requirements.txt`](requirements.txt)

## Estructura del Proyecto
```
.gitignore
assets/
bot.py
README.md
```

## Instalación
1. Clona el repositorio:
    ```sh
    git clone https://github.com/0xbiel/upv-bot.git
    cd upv_bot
    ```

2. Crea un entorno virtual y activa:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Instala las dependencias:
    ```sh
    pip install -r requirements.txt
    ```

## Uso
### Modo Manual
1. Ejecuta el script sin argumentos:
    ```sh
    python bot.py
    ```

2. Introduce las credenciales cuando se te solicite.

3. Sigue las opciones del menú:
    - `l` : Mostrar lista de la actividad
    - `b` : Fuerza bruta hasta conseguir la actividad
    - `r` : Reservar simple
    - `u` : Cambiar URL
    - `e` : Salir

### Modo Automático
1. Ejecuta el script con argumentos:
    ```sh
    python bot.py -u <usuario> -p <contraseña> -l <Y> -x "<preferencias>" -b <Y> -a "<URL>"
    ```

    - `-u`, `--user`: Usuario
    - `-p`, `--password`: Contraseña
    - `-l`, `--list`: Listar horarios disponibles (Y)
    - `-x`, `--preferencias`: Preferencias de actividades (e.g., "MU002,MU003")
    - `-b`, `--loop`: Intentar hasta que esté disponible (Y)
    - `-a`, `--activity`: URL de la actividad que deseas reservar

## Funciones Principales
- [`login(user, passwd)`](bot.py#L48): Autentica al usuario en la intranet.
- [`get_schedule()`](bot.py#L53): Obtiene el horario de la actividad desde la URL proporcionada.
- [`get_time(schedule)`](bot.py#L83): Procesa el horario obtenido.
- [`print_schedule(items)`](bot.py#L99): Imprime el horario en formato de tabla.
- [`reservar(item)`](bot.py#L167): Intenta realizar una reserva para el ítem especificado.
- [`loop_reserva(item)`](bot.py#L181): Ejecuta `reservar(item)` en bucle hasta que se consiga la reserva.
- [`holy_func(preferences)`](bot.py#L188): Reserva ítems en paralelo usando hilos.
- [`holy_func_looping(preferences)`](bot.py#L201): Reserva ítems en paralelo en bucle usando hilos.
- [`handle_options()`](bot.py#L245): Maneja las opciones seleccionadas por el usuario.
- [`get_user_choice()`](bot.py#L232): Obtiene la opción elegida por el usuario.
- [`get_user_preferences()`](bot.py#L240): Obtiene las preferencias de actividades del usuario.
- [`set_url()`](bot.py#L218): Establece la URL de la actividad deseada.
- [`check_args(args)`](bot.py#L215): Verifica si se pasaron argumentos al ejecutar el script.

## Ejemplo de Uso
### Reservar una Actividad Manualmente
1. Ejecuta:
    ```sh
    python bot.py
    ```
2. Selecciona la opción `r` para reserva simple.
3. Introduce las preferencias de actividades cuando se te solicite.

### Listar Horarios Disponibles
1. Ejecuta:
    ```sh
    python bot.py -u DNI -p CONTRASEÑA -l Y -a URL
    ```

## Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo [`LICENSE`](LICENSE.txt) para más detalles.