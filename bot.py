#!/usr/bin/python3

# IMPORT LIBRARIES
import requests
import re
import argparse
import time
from bs4 import BeautifulSoup
from getpass import getpass
import sys
import threading

s = requests.session()

def hw():
    print(r"""
   __  ______ _    __   ____        __ 
  / / / / __ \ |  / /  / __ )____  / /_
 / / / / /_/ / | / /  / __  / __ \/ __/
/ /_/ / ____/| |/ /  / /_/ / /_/ / /_  
\____/_/     |___/  /_____/\____/\__/  
                                       
Modified by @0xbiel
    """)

# Patterns
pattern = '(?i)(?<=<td>)(.*)(?=<br>Solo)'
valid_pattern = '(?i)(?<=celista">)(.*)(?=<br>Solo)'

# Temp URL
global campus
campus = "V"
global tipoact
tipoact = "6801"
global codacti
codacti = "21570"
global url
url = f"https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus={campus}&p_tipoact={tipoact}&p_codacti={codacti}&p_vista=intranet&p_idioma=c&p_solo_matricula_sn=&p_anc=filtro_actividad"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0", 
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3", 
    "Accept-Encoding": "gzip, deflate", 
    "Referer": "https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus=V&p_tipoact=6607&p_vista=intranet&p_idioma=c&p_solo_matricula_sn=&p_anc=filtro_programa", 
    "Upgrade-Insecure-Requests": "1", 
    "Sec-Fetch-Dest": "document", 
    "Sec-Fetch-Mode": "navigate", 
    "Sec-Fetch-Site": "same-origin", 
    "Sec-Fetch-User": "?1", 
    "Te": "trailers", 
    "Author": "maiky",
    "Connection": "close"
}
days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

############################################
####               Utils                ####
############################################
def login(user, passwd):
    login_url = "https://intranet.upv.es:443/pls/soalu/est_aute.intraalucomp"
    login_data = {"id": "c", "estilo": "500", "vista": '', "param": '', "cua": "miupv", "dni": user, "clau": passwd}
    s.post(login_url, data=login_data)

def get_schedule():
    global r
    r = s.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table', {'class': 'upv_listacolumnas'})
    schedule = []

    if table:
        rows = table.find_all('tr')
        headers = [th.text.strip() for th in rows[0].find_all('th')]

        for row in rows[1:]:
            cells = row.find_all('td')
            if not cells:
                continue
            time_slot = cells[0].get_text(strip=True)
            for i, cell in enumerate(cells[1:], start=1):
                day = headers[i]
                details = cell.get_text(separator=' ', strip=True)
                code_match = re.search(r'\b[A-Z]+\d+\b', details)
                code = code_match.group() if code_match else 'Desconocido'
                if code != 'Desconocido':
                    schedule.append({
                        'day': day,
                        'time': time_slot,
                        'code': code
                    })
    # Ensure the function always returns the schedule
    return schedule

def get_time(schedule):
    if not schedule:
        return []
    
    items = []
    for entry in schedule:
        day = entry['day']
        time = entry['time']
        code = entry['code']
        items.append({
            'day': day,
            'time': time,
            'code': code
        })
    return items

def get_day_order(day):
    # Dictionary mapping days in different languages to standard order (0-6)
    day_mappings = {
        # Spanish
        'lunes': 0, 'martes': 1, 'miércoles': 2, 'miercoles': 2, 
        'jueves': 3, 'viernes': 4, 'sábado': 5, 'sabado': 5, 'domingo': 6,
        # Catalan
        'dilluns': 0, 'dimarts': 1, 'dimecres': 2, 
        'dijous': 3, 'divendres': 4, 'dissabte': 5, 'diumenge': 6,
        # English
        'monday': 0, 'tuesday': 1, 'wednesday': 2,
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }
    return day_mappings.get(day.lower(), 7)  # Unknown days go to the end

def print_schedule(items):
    if not items:
        print("No schedule available.")
        return

    # Extract unique days and times, sort days by standard order
    days = sorted(set(item['day'] for item in items), key=get_day_order)
    times = sorted(set(item['time'] for item in items))

    # Rest of the function remains the same
    schedule_map = {(item['day'], item['time']): item['code'] for item in items}
    
    day_width = max(len(day) for day in days)
    time_width = max(len(time) for time in times)
    code_width = max(len(item['code']) for item in items)
    col_width = max(day_width, code_width)

    print('Time'.ljust(time_width), end=' | ')
    print(' | '.join(day.ljust(col_width) for day in days))
    
    print('-' * time_width, end=' | ')
    print(' | '.join('-' * col_width for _ in days))

    for time in times:
        print(time.ljust(time_width), end=' | ')
        row = []
        for day in days:
            code = schedule_map.get((day, time), '')
            row.append(code.ljust(col_width))
        print(' | '.join(row))

def calc_time(i, id):
    minutes_per_slot = 15
    slots_per_hour = 60 // minutes_per_slot  # 4 slots per hour
    total_slots_per_day = 14 * slots_per_hour  # 56 slots per day
    day = ((id - 1) // total_slots_per_day) % len(days)
    time_slot = (id - 1) % total_slots_per_day
    start_minutes = 7 * 60 + time_slot * minutes_per_slot
    end_minutes = start_minutes + minutes_per_slot
    start_hour = start_minutes // 60
    start_minute = start_minutes % 60
    end_hour = end_minutes // 60
    end_minute = end_minutes % 60
    time = "%02d:%02d-%02d:%02d" % (start_hour, start_minute, end_hour, end_minute)
    print("[+] %s : %s : %s" % (days[day], time, i))
    return [days[day], time]

############################################
########### Reservation handlers ###########
############################################
def reservar(item):
    r = s.get(url)
    if "tanca sessió" not in r.text:
        print("Session expired or invalid. Please login again.")
        return False

    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Find all td elements with the specific class
    tds = soup.find_all('td', class_='IAOL_BGColorGrpLibre')
    
    link = None
    # Check each td for the exact code match inside its anchor tag
    for td in tds:
        a_tag = td.find('a', class_='upv_enlacelista')
        if a_tag and item in a_tag.text.split('<br>')[0]:  # Check first part before <br>
            link = a_tag
            break

    if not link:
        print(f"No reservation link found for {item}")
        return False

    try:
        href = link.get('href')
        if not href:
            print(f"Invalid href for {item}")
            return False

        # Convert HTML entities and build full URL
        reservation_url = "https://intranet.upv.es/pls/soalu/" + href.replace('&amp;', '&')
        print(f"Attempting reservation at: {reservation_url}")
        
        response = s.get(reservation_url)
        if response.status_code == 200:
            print(f"{item} --> RESERVADO!")
            return True
        else:
            print(f"Reservation failed with status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error during reservation: {str(e)}")
        return False

def loop_reserva(item):
    completed = False
    while completed == False:
        completed = reservar(item)
        if completed == False:
            time.sleep(5)

############################################
#### Multithreaded reservation handlers ####
############################################
def holy_func(preferences):
    def reserve_item(preference):
        reservar(preference)

    threads = []
    for i in preferences:
        t = threading.Thread(target=reserve_item, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

def holy_func_looping(preferences):
    def reserve_item(preference):
        loop_reserva(preference)
                
    threads = []
    for i in preferences:
        t = threading.Thread(target=reserve_item, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

############################################
########### User input handlers ############
############################################
def display_options_table(options):
    """Display options in a formatted table"""
    if not options:
        print("No options available")
        return

    cleaned_options = []
    for code, name in options:
        # Basic cleanup
        clean_name = name.replace('\n', ' ').strip()
        
        # Only split if the name contains multiple distinct activities
        if ' / ' in clean_name or ' - ' in clean_name:
            clean_name = clean_name.split(' / ')[0].split(' - ')[0].strip()
        # Don't split multi-word activity names
        elif any(word in clean_name.upper() for word in ['CÀRDIO', 'FITNES', 'GAP', 'IOGA']):
            clean_name = ' '.join(clean_name.split())  # Just normalize spaces
            
        cleaned_options.append((code, clean_name))

    # Format table (rest remains the same)
    max_code_len = max(len(opt[0]) for opt in cleaned_options)
    max_name_len = max(len(opt[1]) for opt in cleaned_options)
    
    header = f"| {'Code'.ljust(max_code_len)} | {'Name'.ljust(max_name_len)} |"
    separator = f"|{'-' * (max_code_len + 2)}|{'-' * (max_name_len + 2)}|"
    
    print(separator)
    print(header)
    print(separator)
    for code, name in cleaned_options:
        print(f"| {code.ljust(max_code_len)} | {name.ljust(max_name_len)} |")
    print(separator)

def get_url():
    global campus, tipoact, codacti, url, s

    # Get campus selection
    print(r"""
Campus:
    A: Alcoi
    G: Gandía
    V: Vera
    """)
    campus = input("\nIntroduzca el campus (A, G, V): ").upper()
    while campus not in ['A', 'G', 'V']:
        print("Campus inválido. Debe ser A, G, o V")
        campus = input("Introduzca el campus (A, G, V): ").upper()

    # Get tipoact options
    base_url = f"https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus={campus}&p_vista=intranet&p_idioma=c&p_solo_matricula_sn=&p_anc=filtro_campus"
    r = s.get(base_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Extract tipoact options
    tipoact_select = soup.find('select', {'name': 'tipoact'})
    if tipoact_select:
        tipoact_options = []
        for opt in tipoact_select.find_all('option'):
            value = opt['value']
            # Take only the first line and clean whitespace
            name = opt.text.split('\n')[0].strip()
            tipoact_options.append((value, name))
        
        print("\nTipos de actividad disponibles:")
        display_options_table(tipoact_options)
        
        tipoact = input("\nSeleccione el código de actividad: ")
        while tipoact not in [opt[0] for opt in tipoact_options]:
            print("Código inválido")
            tipoact = input("\nSeleccione el código de actividad: ")

    # Get codacti options
    activities_url = f"https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus={campus}&p_tipoact={tipoact}&p_vista=intranet&p_idioma=c&p_solo_matricula_sn=&p_anc=filtro_programa"
    r = s.get(activities_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Extract activity options
    acti_select = soup.find('select', {'name': 'acti'})
    if acti_select:
        acti_options = []
        for opt in acti_select.find_all('option'):
            value = opt['value']
            # Take only the first line and clean whitespace
            name = opt.text.split('\n')[0].strip()
            acti_options.append((value, name))
        
        print("\nActividades disponibles:")
        display_options_table(acti_options)
        
        codacti = input("\nSeleccione el código de la actividad: ")
        while codacti not in [opt[0] for opt in acti_options]:
            print("Código inválido")
            codacti = input("\nSeleccione el código de la actividad: ")
    
    # Update URL
    url = f"https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus={campus}&p_tipoact={tipoact}&p_codacti={codacti}&p_vista=intranet&p_idioma=c&p_solo_matricula_sn=&p_anc=filtro_actividad"

def check_args(args):
    return all(v is None for v in vars(args).values())

def set_url():
    global url
    url = input("\nIntroduzca la url de la actividad deseada: ")

def options():
    print(r"""
Opciones:
    l : Mostrar lista de la actividad (list)
    b: Brute force hasta conseguir las actividad (brute / bruteforce)
    r: reservar simple (reserve)
    c: elegir actividad (choose)
    u: cambiar url (url)
    e: salir (exit)
              """)
    
def get_user_choice():
    while True:
        options()
        choice = input("Introduzca tu opción: ").lower()
        if choice in ['l', 'b', 'r', 'e', 'u', 'c', 'exit', 'brute', 'bruteforce', 'reserve', 'list', 'url', 'choose']:
            return choice
        print("Opción no válida, inténtalo de nuevo.")

def get_user_preferences():
    print("\nIntroduzca opciones (separado por coma y sin espacios, e.g. MS1002,MS1015):")
    prefs = input("> ").strip()
    return prefs.split(",") if prefs else []

def handle_options():
    while True:
        choice = get_user_choice()
        
        if choice in ['e', 'exit']:
            print("Exiting...")
            break
        elif choice in ['l', 'list']:
            schedule = get_schedule()
            items = get_time(schedule)
            print_schedule(items)
        elif choice in ['b', 'brute', 'bruteforce']:
            # Handle bruteforce option
            preferences = get_user_preferences()
            if preferences:
                holy_func_looping(preferences)
            else:
                print("No preferences specified")
        elif choice in ['r', 'reserve']:
            # Handle simple reserve
            preferences = get_user_preferences()
            if preferences:
                holy_func(preferences)
            else:
                print("No preferences specified")
        elif choice in ['u', 'url']:
            set_url()
        elif choice in ['c', 'change']:
            get_url()

############################################
########### Main execution logic ###########
############################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--user', help='Username')
    parser.add_argument('-p','--password', help='Password to login')
    parser.add_argument('-l','--list', help='List available schedule (Y/N)')
    parser.add_argument('-x','--preferencias', help='"MU002,MU003,MU025,MU026,MU053,MU054"')
    parser.add_argument('-b','--loop', help='Intentarlo hasta que esté disponible (Y/N)')
    parser.add_argument('-a','--activity', help='URL de la actividad que deseas Reservar')
    args = parser.parse_args()
    user = args.user
    passwd = args.password
    list = args.list
    pref = args.preferencias
    loop = args.loop
    url = args.activity

    hw()
    
    if check_args(args):
        print("No args passed, entered manual mode\n")

        user = input("Introduzca el usuario: ")
        passwd = getpass("Introduzca la contraseña: ")

        print("\nIniciando sesión...")
        login(user, passwd)

        print("\nSesión iniciada con éxito.")

        print("""
¿Cómo desea seleccionar la actividad?
1. Seleccionar por menú (S)
2. Introducir URL directamente (U)
        """)
        ask = input("Introduzca su elección (S/U): ").upper()
        while ask not in ['S', 'U']:
            print("Opción inválida. Inténtalo de nuevo.")
            ask = input("Introduzca su elección (S/U): ").upper()

        if ask == 'S':
            get_url()
        else:
            set_url()

        handle_options()

    else:
        if(user == "" or passwd == ""):
            print("No user passed, exiting...")
            sys.exit(1)

        login(user, passwd)

        if (list == "Y" ):
            print_schedule(get_time(get_schedule()))

        if pref:
            preferences = pref.split(",")
        else:
            preferences = []

        if loop:
            holy_func_looping(preferences)
        else:
            holy_func(preferences)