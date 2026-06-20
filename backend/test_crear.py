import uuid
from app.database import SessionLocal
from app.schemas.alquiler import CrearReservaPayloadSchema
from app.services.alquiler_service import crear_reserva_con_codigo
from app.models.vehiculo import Vehiculo

db = SessionLocal()
# find the available vehicle
v = db.query(Vehiculo).filter(Vehiculo.estado_registro=="HABILITADO", Vehiculo.disponible==True).first()
if v:
    print(f"Testing on vehicle {v.id}")
    schema = CrearReservaPayloadSchema(vehiculo_id=v.id, fecha_fin="2027-01-01T10:00:00Z")
    try:
        reserva = crear_reserva_con_codigo(db, schema, v.propietario_id)
        print("Success!")
    except Exception as e:
        print("Failed:", type(e), e)
else:
    print("No available vehicle found")
