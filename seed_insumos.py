# -*- coding: utf-8 -*-
"""Lee el Excel de insumos e inserta en la DB de Terramia."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from database import db, Insumo
from datetime import date

INSUMOS = [
    # (nombre, categoria, proveedor, unidad, precio_compra, cantidad_compra, fecha, notas)
    ('Arcilla pasta cerámica x1kg',             'arcilla',      'Cider Rosario',          'gr',      3039,   1000,   date(2026, 1, 1),   'precio/gr'),
    ('Engobes x25gr (precio promedio)',          'engobe',       'Mil2Colores Santa Fe',   'gr',      1931,   25,     date(2025, 5, 22),  'precio/gr'),
    ('Kit herramientas x8 piezas',              'herramientas', 'Artística Dibu',          'uso',     14621,  200,    date(2025, 1, 1),   'amort. ×200 usos'),
    ('Papel seda blanco 50×70cm',               'packaging',    'Muresco',                'hoja',    5430,   50,     date(2026, 1, 1),   'x50 hojas'),
    ('Virutas kraft por kg',                    'packaging',    'Mercado Libre',           'gr',      7500,   1000,   date(2026, 1, 1),   None),
    ('Caja Triulzi Cubo 8 (8×8×8cm)',           'packaging',    'Triulzi Rosario',         'unidad',  5286,   10,     date(2026, 1, 1),   'x10 unidades'),
    ('Caja Triulzi Torpedo Micro (28×21×6.5cm)','packaging',    'Triulzi Rosario',         'unidad',  2960,   10,     date(2026, 1, 1),   'x10 unidades'),
    ('Etiquetas autoadhesivas',                 'packaging',    'Shein',                   'unidad',  4000,   500,    date(2026, 1, 1),   'x500'),
    ('Tarjeta gracias A5 (148×105mm)',          'packaging',    'Imprenta (3 x A4)',       'unidad',  3000,   3,      date(2026, 1, 1),   'impresión'),
    ('Tarjeta gracias 7×7cm',                   'packaging',    'Imprenta (12 x A4)',      'unidad',  3000,   12,     date(2026, 1, 1),   'impresión'),
    ('Hilo encerado 70m',                       'packaging',    'Rosario',                 'cm',      3500,   7000,   date(2026, 1, 1),   '70 metros'),
    ('Hilo yute 100m',                          'packaging',    'DQTG',                    'cm',      8000,   10000,  date(2024, 1, 1),   '100 metros'),
    ('Argollas medianas 4.3cm',                 'packaging',    'DQTG',                    'unidad',  6990,   10,     date(2024, 1, 1),   'x10 unidades'),
    ('Sello personalizado 7×7cm',               'herramientas', 'El Camaleón',             'uso',     14390,  12,     date(2026, 1, 1),   'x12 usos estimados'),
    ('Sello personalizado 9×11cm',              'herramientas', 'El Camaleón',             'uso',     26730,  12,     date(2026, 1, 1),   'x12 usos estimados'),
    ('Almohadilla 8×12cm',                      'herramientas', 'El Camaleón',             'uso',     11540,  12,     date(2026, 1, 1),   None),
    ('Tinta 25cc',                              'herramientas', 'El Camaleón',             'unidad',  4180,   6,      date(2026, 1, 1),   None),
]

app = create_app()
with app.app_context():
    ya_hay = Insumo.query.count()
    if ya_hay > 0:
        print(f'Ya hay {ya_hay} insumos. Saltando seed.')
    else:
        for nombre, cat, proveedor, unidad, precio, cantidad, fecha, notas in INSUMOS:
            ins = Insumo(
                nombre=nombre,
                categoria=cat,
                proveedor=proveedor,
                unidad=unidad,
                precio_compra=precio,
                cantidad_compra=cantidad,
                fecha_compra=fecha,
                notas=notas,
            )
            db.session.add(ins)
        db.session.commit()
        print(f'Insertados {len(INSUMOS)} insumos correctamente.')
