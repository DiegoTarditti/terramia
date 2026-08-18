"""Agrega mano_obra_id a formula_lineas y crea tabla mano_de_obra."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from database import db

app = create_app()
with app.app_context():
    db.create_all()  # crea mano_de_obra si no existe
    # agrega columna a formula_lineas si no existe
    with db.engine.connect() as conn:
        cols = [row[1] for row in conn.execute(
            db.text("PRAGMA table_info(formula_lineas)")
        )]
        if 'mano_obra_id' not in cols:
            conn.execute(db.text(
                "ALTER TABLE formula_lineas ADD COLUMN mano_obra_id INTEGER REFERENCES mano_de_obra(id)"
            ))
            conn.commit()
            print("Columna mano_obra_id agregada.")
        else:
            print("Ya existe, nada que hacer.")
