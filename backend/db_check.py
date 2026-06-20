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

reservas = db.query(Reserva).filter(Reserva.estado == "FINALIZADA").all()
if not reservas:
    print("No finalized reservations found")
else:
    for r in reservas:
        v = db.query(Vehiculo).filter(Vehiculo.id == r.vehiculo_id).first()
        print(f"Vehiculo {v.id}: estado_registro={v.estado_registro}, disponible={v.disponible}, precio={v.precio_por_dia}, estacion={v.estacion}")
        
        from app.services.alquiler_service import ESTADOS_RESERVA_ACTIVA
        active = db.query(Reserva).filter(Reserva.vehiculo_id == v.id, Reserva.estado.in_(ESTADOS_RESERVA_ACTIVA)).all()
        if active:
            print(f"  ACTIVE RESERVATIONS FOUND: {[a.estado for a in active]}")
        else:
            print("  No active reservations.")
            
