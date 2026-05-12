"""
Servicio de negocio: Usuario.

Responsabilidades de esta capa:
    1. Verificar unicidad del email antes de persistir (CA 5).
    2. Delegar el hashing al módulo de seguridad (CA 4 - hashing).
    3. Persistir el nuevo Usuario y retornarlo hidratado con su id.

Esta capa NO valida formato de email ni longitud de contraseña;
esa responsabilidad pertenece al schema Pydantic (RegistroUsuarioSchema).
"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import MailExistenteError, MailInexistenteError, ContraseniaIncorrectaError
from app.models.usuario import Usuario
from app.schemas.usuario import RegistroUsuarioSchema, UsuarioLogin
from app.utils.security import hash_password, verify_password


def crear_usuario(db: Session, schema: RegistroUsuarioSchema) -> Usuario:
    """
    Crea un nuevo Usuario en la base de datos.

    Flujo:
        1. Consulta si el email ya existe → lanza MailExistenteError (CA 5).
        2. Hashea la contraseña con bcrypt (CA 4 - nunca texto plano).
        3. Instancia y persiste el Usuario.
        4. En caso de race condition, el IntegrityError de DB también se
           convierte en MailExistenteError.

    Args:
        db     : Sesión SQLAlchemy activa (inyectada por el controlador o el test).
        schema : Payload ya validado por RegistroUsuarioSchema
                 (email normalizado a minúsculas, contraseña ≥ 8 chars).

    Returns:
        El objeto Usuario persistido, con `id` y `created_at` poblados.

    Raises:
        MailExistenteError: Si el email ya está registrado en la plataforma.
    """
    # ── CA 5: Verificar unicidad del email ───────────────────────────────────
    email_existente = (
        db.query(Usuario).filter(Usuario.email == schema.email).first()
    )
    if email_existente:
        raise MailExistenteError()

    # ── CA 4 (hashing): Nunca persistir texto plano ──────────────────────────
    nuevo_usuario = Usuario(
        email=schema.email,
        hashed_password=hash_password(schema.password),
    )

    db.add(nuevo_usuario)
    try:
        db.commit()
        db.refresh(nuevo_usuario)  # Hidrata id, created_at, etc.
    except IntegrityError:
        # Safety net para race conditions (dos registros simultáneos del mismo email)
        db.rollback()
        raise MailExistenteError()

    return nuevo_usuario

def autenticar_usuario(db: Session, credenciales: UsuarioLogin) -> Usuario:
    """
    Autentica un usuario verificando su email y contraseña.
    
    Args:
        db: Sesión de la base de datos.
        credenciales: Schema con email y contraseña.
        
    Returns:
        El modelo de Usuario si las credenciales son válidas.
        
    Raises:
        CredencialesInvalidasError: Si el email no existe o la contraseña no coincide.
    """
    usuario = db.query(Usuario).filter(Usuario.email == credenciales.email).first()
    if not usuario:
        raise MailInexistenteError()
        
    if not verify_password(credenciales.password, usuario.hashed_password):
        raise ContraseniaIncorrectaError()
        
    return usuario
