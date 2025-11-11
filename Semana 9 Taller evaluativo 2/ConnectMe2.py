class Contacto: 
    def __init__(self, nombre, telefono, correo, cargo):
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo
        self.cargo = cargo

    def mostrar(self):
        return f"Nombre: {self.nombre}, Teléfono: {self.telefono}, Correo: {self.correo}, Cargo: {self.cargo}"
    
class AgendaContactos:
    def __init__(self):
        self.contactos = []

    def registrar_contacto(self, nombre, telefono, correo, cargo):
        if not nombre or not telefono or not correo or not cargo:
            raise ValueError("Todos los campos son obligatorios")

        for contacto in self.contactos:
            if contacto.correo == correo:
                raise ValueError("Ya existe un contacto con ese correo electrónico")

        nuevo = Contacto(nombre, telefono, correo, cargo)
        self.contactos.append(nuevo)
        print("Contacto registrado exitosamente")
        
    def listar_contactos(self):
        if not self.contactos:
            print("No hay contactos registrados")
            return
        
        for contacto in self.contactos:
            print(contacto.mostrar())
    
    def buscar_contacto(self):
        print("1) Buscar por nombre  2) Buscar por correo")
        opcion = input("Opción: ")
        
        if opcion == "1":
            nombre = input("Nombre o parte del nombre: ").lower()
            encontrados = []
            
            for contacto in self.contactos:
                if nombre in contacto.nombre.lower():
                    encontrados.append(contacto)
            
            if encontrados:
                for contacto in encontrados:
                    print(f"- {contacto.mostrar()}")
            else:
                print("No se encontraron contactos con ese nombre")
        
        elif opcion == "2":
            correo = input("Correo exacto: ")
            encontrado = False
            
            for contacto in self.contactos:
                if contacto.correo == correo:
                    print(contacto.mostrar())
                    encontrado = True
                    break
            
            if not encontrado:
                print("No existe un contacto con ese correo")
        
        else:
            print("Opción no válida")

    def eliminar_contacto(self):
        correo = input("Correo del contacto a eliminar: ")
        
        for i, contacto in enumerate(self.contactos):
            if contacto.correo == correo:
                del self.contactos[i]
                print("Contacto eliminado correctamente")
                return
        
        print("No se encontró ningún contacto con ese correo")
    
    def menu(self):
        while True:
            print("\n--- AGENDA DE CONTACTOS ---")
            print("1) Registrar contacto")
            print("2) Buscar contacto")
            print("3) Listar contactos")
            print("4) Eliminar contacto")
            print("5) Salir")
            
            opcion = input("Seleccione una opción: ")
            
            if opcion == "1":
                # Solicitar datos al usuario y registrar contacto
                nombre = input("Nombre: ")
                telefono = input("Teléfono: ")
                correo = input("Correo: ")
                cargo = input("Cargo: ")
                try:
                    self.registrar_contacto(nombre, telefono, correo, cargo)
                except ValueError as e:
                    print(f"Error: {e}")
            elif opcion == "2":
                self.buscar_contacto()
            elif opcion == "3":
                self.listar_contactos()
            elif opcion == "4":
                self.eliminar_contacto()
            elif opcion == "5":
                print("¡Hasta luego!")
                break
            else:
                print("Opción no válida, intente nuevamente")



if __name__ == "__main__":
    agenda = AgendaContactos()
    agenda.menu()