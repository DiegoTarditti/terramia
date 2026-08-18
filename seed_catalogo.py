"""
Reemplaza categorías y productos demo por los reales de Terramia.
Ejecutar: python seed_catalogo.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from database import db, Categoria, Producto

with app.app_context():
    # --- Borrar productos y categorías demo ---
    Producto.query.delete()
    Categoria.query.delete()
    db.session.commit()
    print("Demo borrado.")

    # --- Categorías reales ---
    cats = [
        Categoria(nombre='Utilitarios',  slug='utilitarios',  orden=1),
        Categoria(nombre='Accesorios',   slug='accesorios',   orden=2),
        Categoria(nombre='Decoración',   slug='decoracion',   orden=3),
    ]
    db.session.add_all(cats)
    db.session.commit()
    cat_map = {c.slug: c.id for c in Categoria.query.all()}
    print("Categorías creadas:", [c.nombre for c in cats])

    # --- Productos reales ---
    productos = [
        Producto(
            nombre='Lechuza',
            descripcion='Lechuza de cerámica artesanal, modelada y pintada a mano. Pieza decorativa única con detalles en relieve. Cada ejemplar tiene su propia expresión.',
            precio=55000,
            categoria_id=cat_map['decoracion'],
            imagen='lechuza.jpg',
            destacado=True,
            activo=True,
        ),
        Producto(
            nombre='Bandeja Terrazo',
            descripcion='Bandeja artesanal de cerámica con diseño de terrazo, pintada a mano con pigmentos naturales. Ideal para organizar accesorios o servir. Apta para uso diario.',
            precio=45000,
            categoria_id=cat_map['utilitarios'],
            imagen='bandeja-terrazo.png',
            destacado=True,
            activo=True,
        ),
        Producto(
            nombre='Portasahumeros',
            descripcion='Portasahumeros de cerámica hecho a mano. Diseño minimalista con terminación artesanal. Perfecto para crear un ambiente de calma y aromatizar tu espacio.',
            precio=18000,
            categoria_id=cat_map['accesorios'],
            imagen='portasahumerios.png',
            destacado=True,
            activo=True,
        ),
    ]
    db.session.add_all(productos)
    db.session.commit()
    print("Productos creados:")
    for p in productos:
        print(f"  - {p.nombre} → ${int(p.precio):,} ({p.imagen})")

    print("\nListo!")
