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
# 1. DEFAULT DATA
pattern = '(?i)(?<=<td>)(.*)(?=<br>Solo)'
valid_pattern = '(?i)(?<=celista">)(.*)(?=<br>Solo)'

# Temp URL
global url
url = "https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus=A&p_tipoact=6821&p_codacti=21676&p_vista=intranet&p_idioma=c&p_solo_matricula_sn=&p_anc=filtro_actividad"
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

def print_schedule(items):
    if not items:
        print("No schedule available.")
        return

    # Define header and rows
    header = ['Day', 'Time', 'Code']
    rows = [[item['day'], item['time'], item['code']] for item in items]
    
    # Calculate column widths
    col_widths = [max(len(str(row[i])) for row in rows + [header]) for i in range(len(header))]
    
    # Print formatted table
    header_formatted = ' | '.join(f"{header[i].ljust(col_widths[i])}" for i in range(len(header)))
    separator = '-+-'.join('-' * col_widths[i] for i in range(len(header)))
    print(header_formatted)
    print(separator)
    for row in rows:
        print(' | '.join(f"{str(row[i]).ljust(col_widths[i])}" for i in range(len(row))))

# Python
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
    u: cambiar url (url)
    e: salir (exit)
              """)
    
def get_user_choice():
    while True:
        options()
        choice = input("Introduzca tu opción: ").lower()
        if choice in ['l', 'b', 'r', 'e', 'exit', 'brute', 'bruteforce', 'reserve', 'list']:
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

        login(user, passwd)

        url = input("\nIntroduzca la url de la actividad deseada: ")

        items = get_time(get_schedule())

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