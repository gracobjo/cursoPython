import json


fichero = open('informacion.json')

objeto_json = json.load(fichero)

fichero.close()

print(objeto_json)