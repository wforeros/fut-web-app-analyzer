from options import get_search_filter, get_target_filter
from src.modules.login.login import login
from src.scraper.web_app.web_app import WebApp



def main_menu():
    web_app = WebApp()
    
    while True:
        print("\nMenu de opciones:")
        print("1. Login")
        print("2. Mercado de Transferencias")
        print("3. Objetivos")
        print("4. Buscar jugadores")
        print("5. Buscar jugadores y agregar a objetivos (usando options.py)")
        print("6. Salir")

        option = input("Seleccione una opción: ")

        if option == "1":
            email = input("Ingrese su correo electrónico: ")
            password = input("Ingrese su contraseña: ")
            login(web_app.driver, { "email": email, "password": password})
        elif option == "2":
            web_app.go_to_transfer_market(True)
            web_app.go_to_targets()
        elif option == "3":
            web_app.go_to_targets()
        elif option == "4":
            web_app.search_players()
        elif option == "5":
            for i in range(1,20):
              print('Iteración: ', i)
              web_app.go_to_transfer_market(True, filters=get_search_filter())
              web_app.go_to_targets(filters=get_target_filter())
              web_app.sleep_approx(200)
        elif option == "6":
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")



main_menu()