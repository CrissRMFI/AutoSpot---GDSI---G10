from app.database import SessionLocal
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.models.reserva import Reserva
from app.models.checkout_vehiculo import CheckoutVehiculo
from app.models.checkin_vehiculo import CheckinVehiculo
from app.models.reporte import Reporte
from app.models.reporte_foto import ReporteFoto
from app.models.foto_vehiculo import FotoVehiculo

db = SessionLocal()

# find a vehicle that is HABILITADO and disponible=True
v = db.query(Vehiculo).filter(Vehiculo.estado_registro=="HABILITADO", Vehiculo.disponible==True).first()
if v:
    print(f"Testing on vehicle {v.id}")
    print(f"estado_registro={v.estado_registro}")
    print(f"disponible={v.disponible}")
    print(f"precio_por_dia={v.precio_por_dia}")
    print(f"estacion={v.estacion}")
    
    # Run the exact if statement from crear_reserva_con_codigo
    is_error = (
        v.estado_registro != "HABILITADO"
        or not v.disponible
        or v.precio_por_dia is None
        or v.precio_por_dia <= 0
        or not v.estacion
    )
    print(f"Raises VehiculoNoDisponibleParaReservaError? {is_error}")
else:
    print("No available vehicle found")
