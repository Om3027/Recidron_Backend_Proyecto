from app.database import engine, Base, SessionLocal
from .sqlalchemy_models import Role, TipoResiduo, Material, ZonaCampus, Tamano

def init_db():
    """
    Crea todas las tablas si no existen usando SQLAlchemy.
    """
    print("[ INFO ] Inicializando base de datos con SQLAlchemy...")
    Base.metadata.create_all(bind=engine)
    print("[ INFO ] Tablas verificadas/creadas exitosamente.")

    # SEED — Datos iniciales
    db = SessionLocal()
    try:
        _seed(db, Role, "nombre_rol", ['Administrador', 'Invitado'])
        _seed(db, TipoResiduo, "nombre_tipo", ['Aprovechable', 'No Aprovechable', 'Orgánico', 'Peligroso'])
        _seed(db, Material, "nombre_material", ['Plástico', 'Icopor', 'Metal', 'Papel/Cartón', 'Vidrio'])
        _seed(db, ZonaCampus, "nombre_zona", ['Entrada Principal', 'Bloque A', 'Bloque B', 'Canchas', 'Cafetería', 'Parqueadero'])
        _seed(db, Tamano, "nombre_tamano", ['Pequeño', 'Mediano', 'Grande'])
        db.commit()
        print("[ INFO ] Datos iniciales insertados exitosamente.")
    except Exception as e:
        print(f"[ ERROR ] Error al insertar datos iniciales: {e}")
        db.rollback()
    finally:
        db.close()
        
    print('[ OK ] Base de datos lista.')

def _seed(db, model, field, values):
    """Inserta valores iniciales solo si la tabla está vacía."""
    if db.query(model).count() == 0:
        for valor in values:
            obj = model(**{field: valor})
            db.add(obj)

