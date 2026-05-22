"""
Servicio de negocio — Catálogo de marcas y modelos.

Reemplaza el catálogo hardcodeado. La validación de combos marca/modelo
para vehículos se delega aquí (lookup en DB).
"""
from sqlalchemy.orm import Session

from app.exceptions import (
    MarcaModeloInexistenteError,
    MarcaNoEncontradaError,
    MarcaYaExistenteError,
    ModeloYaExistenteError,
)
from app.models.marca import Marca, Modelo


def listar_marcas(db: Session) -> list[Marca]:
    """Lista todas las marcas con sus modelos cargados (ordenadas por nombre)."""
    return db.query(Marca).order_by(Marca.nombre).all()


def crear_marca(db: Session, nombre: str) -> Marca:
    """Crea una marca. Falla si ya existe."""
    existente = db.query(Marca).filter(Marca.nombre == nombre).first()
    if existente is not None:
        raise MarcaYaExistenteError()

    marca = Marca(nombre=nombre)
    db.add(marca)
    db.commit()
    db.refresh(marca)
    return marca


def obtener_marca(db: Session, marca_id: int) -> Marca:
    """Obtiene una marca por id o lanza MarcaNoEncontradaError."""
    marca = db.query(Marca).filter(Marca.id == marca_id).first()
    if marca is None:
        raise MarcaNoEncontradaError()
    return marca


def crear_modelo(db: Session, marca_id: int, nombre: str) -> Modelo:
    """Crea un modelo bajo una marca. Falla si la marca no existe o el modelo ya existe."""
    obtener_marca(db, marca_id)  # 404 si no existe

    ya_existe = (
        db.query(Modelo)
        .filter(Modelo.marca_id == marca_id, Modelo.nombre == nombre)
        .first()
    )
    if ya_existe is not None:
        raise ModeloYaExistenteError()

    modelo = Modelo(marca_id=marca_id, nombre=nombre)
    db.add(modelo)
    db.commit()
    db.refresh(modelo)
    return modelo


def validar_combo_marca_modelo(db: Session, marca: str, modelo: str) -> None:
    """
    Verifica que la combinación marca/modelo exista en el catálogo.

    Reemplaza al model_validator del schema RegistroVehiculoSchema.
    """
    encontrado = (
        db.query(Modelo)
        .join(Marca, Marca.id == Modelo.marca_id)
        .filter(Marca.nombre == marca, Modelo.nombre == modelo)
        .first()
    )
    if encontrado is None:
        raise MarcaModeloInexistenteError()
