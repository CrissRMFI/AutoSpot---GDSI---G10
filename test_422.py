import requests

url = "http://localhost:8000/usuarios/6028bb66-2a71-4017-bcfc-386839efe378/vehiculos"
payload = {
    "marca": "Toyota",
    "modelo": "Etios",
    "anio": 2023,
    "tipo_transmision": "MANUAL",
    "capacidad": 5,
    "categoria": "SEDAN",
    "tipo_combustible": "NAFTA",
    "pets_friendly": True,
    "patente": " ",
    "chasis": " ",
    "motor": " ",
    "titular": " ",
    "cedula": " ",
    "poliza": " ",
    "vtv": " ",
    "estacion": " ",
    "telefono": " ",
    "descripcion": " ",
    "fotos": [
        {"lado": "FRENTE", "url": "uploads/vehiculos/mock/1.jpg", "formato": "jpg", "tamanio_bytes": 500000},
        {"lado": "TRASERA", "url": "uploads/vehiculos/mock/2.jpg", "formato": "jpg", "tamanio_bytes": 500000},
        {"lado": "LATERAL_IZQUIERDO", "url": "uploads/vehiculos/mock/3.jpg", "formato": "jpg", "tamanio_bytes": 500000},
        {"lado": "LATERAL_DERECHO", "url": "uploads/vehiculos/mock/4.jpg", "formato": "jpg", "tamanio_bytes": 500000}
    ]
}
response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())
