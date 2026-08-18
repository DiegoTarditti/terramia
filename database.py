from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    orden = db.Column(db.Integer, default=0)
    productos = db.relationship('Producto', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'


class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer)  # None = sin límite
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    imagen = db.Column(db.String(500))
    destacado = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def imagen_url(self):
        if not self.imagen:
            return None
        if self.imagen.startswith('http'):
            return self.imagen
        return f'/static/uploads/{self.imagen}'

    @property
    def precio_fmt(self):
        return f"${int(self.precio):,}".replace(',', '.')

    def __repr__(self):
        return f'<Producto {self.nombre}>'


class Insumo(db.Model):
    __tablename__ = 'insumos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50), default='otro')
    proveedor = db.Column(db.String(200))
    unidad = db.Column(db.String(20), nullable=False, default='unidad')
    precio_compra = db.Column(db.Numeric(12, 2), nullable=False)
    cantidad_compra = db.Column(db.Numeric(12, 4), nullable=False)
    fecha_compra = db.Column(db.Date)
    notas = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def precio_por_unidad(self):
        try:
            return float(self.precio_compra) / float(self.cantidad_compra)
        except (TypeError, ZeroDivisionError):
            return 0

    @property
    def precio_unidad_fmt(self):
        p = self.precio_por_unidad
        if p == 0:
            return '—'
        if p < 1:
            return f"${p:.4f}"
        if p < 100:
            return f"${p:.2f}"
        return f"${p:,.0f}".replace(',', '.')

    @property
    def precio_compra_fmt(self):
        try:
            return f"${int(self.precio_compra):,}".replace(',', '.')
        except Exception:
            return '—'

    @property
    def cantidad_fmt(self):
        c = float(self.cantidad_compra)
        return str(int(c)) if c == int(c) else f"{c:g}"

    def __repr__(self):
        return f'<Insumo {self.nombre}>'


class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    clave = db.Column(db.String(100), primary_key=True)
    valor = db.Column(db.String(500), nullable=False)

    @staticmethod
    def get(clave, default=''):
        row = Configuracion.query.get(clave)
        return row.valor if row else default

    @staticmethod
    def set(clave, valor):
        row = Configuracion.query.get(clave)
        if row:
            row.valor = str(valor)
        else:
            db.session.add(Configuracion(clave=clave, valor=str(valor)))


class Rubro(db.Model):
    __tablename__ = 'rubros'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    orden = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Rubro {self.nombre}>'


class ManoDeObra(db.Model):
    __tablename__ = 'mano_de_obra'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    tarifa_hora = db.Column(db.Numeric(10, 2), nullable=False)
    notas = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)

    @property
    def tarifa_fmt(self):
        try:
            return f"${int(self.tarifa_hora):,}".replace(',', '.')
        except Exception:
            return '—'

    def __repr__(self):
        return f'<ManoDeObra {self.nombre}>'


class Formula(db.Model):
    __tablename__ = 'formulas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=True)
    amort_pct = db.Column(db.Numeric(5, 2), default=6)
    reserva_pct = db.Column(db.Numeric(5, 2), default=15)
    margen_pct = db.Column(db.Numeric(5, 2), default=40)
    tarifa_taller = db.Column(db.Numeric(10, 2), default=2200)
    mp_comision_pct = db.Column(db.Numeric(5, 2), default=5)
    descuento_pct = db.Column(db.Numeric(5, 2), default=10)
    pvp_override = db.Column(db.Numeric(12, 2), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lineas = db.relationship('FormulaLinea', backref='formula', lazy=True,
                             cascade='all, delete-orphan', order_by='FormulaLinea.orden')
    producto = db.relationship('Producto', backref='formula', lazy=True)

    def calcular(self):
        items = []
        sub_insumos = 0.0
        sub_mo = 0.0

        for l in self.lineas:
            if l.tipo == 'mano_obra':
                tarifa = float(l.mano_obra.tarifa_hora) if (l.mano_obra_id and l.mano_obra) else float(l.tarifa or 0)
                nombre = l.mano_obra.nombre if (l.mano_obra_id and l.mano_obra) else (l.concepto or 'Mano de obra')
                unidad = 'hs'
                precio_u = tarifa
                costo = float(l.cantidad) * tarifa
                sub_mo += costo
            elif l.tipo == 'taller':
                precio_u = float(self.tarifa_taller)
                nombre = 'Servicio taller'
                unidad = 'cubo'
                costo = float(l.cantidad) * precio_u
                sub_insumos += costo
            elif l.insumo_id and l.insumo:
                precio_u = l.insumo.precio_por_unidad
                nombre = l.insumo.nombre
                unidad = l.insumo.unidad
                costo = float(l.cantidad) * precio_u
                sub_insumos += costo
            else:
                precio_u = float(l.tarifa or 0)
                nombre = l.concepto or '—'
                unidad = ''
                costo = precio_u
                sub_insumos += costo
            items.append({'l': l, 'nombre': nombre, 'precio_u': precio_u,
                          'unidad': unidad, 'costo': costo})

        sub_herr = sub_insumos * float(self.amort_pct) / 100
        reserva = sub_insumos * float(self.reserva_pct) / 100
        subtotal = sub_insumos + sub_mo + sub_herr
        costo_total = subtotal + reserva

        m = float(self.margen_pct) / 100
        pvp_calc = costo_total / (1 - m) if m < 1 else costo_total * 2
        pvp_final = float(self.pvp_override) if self.pvp_override else pvp_calc
        mp_div = 1 - float(self.mp_comision_pct) / 100
        pvp_mp = pvp_final / mp_div if mp_div > 0 else pvp_final
        pvp_desc = pvp_final * (1 - float(self.descuento_pct) / 100)
        ganancia = pvp_final - costo_total
        margen_real = ganancia / pvp_final * 100 if pvp_final > 0 else 0

        return {
            'lineas': items,
            'sub_insumos': sub_insumos, 'sub_mo': sub_mo, 'sub_herr': sub_herr,
            'subtotal': subtotal, 'reserva': reserva, 'costo_total': costo_total,
            'pvp_calc': pvp_calc, 'pvp_final': pvp_final,
            'pvp_mp': pvp_mp, 'pvp_desc': pvp_desc,
            'ganancia': ganancia, 'margen_real': margen_real,
        }

    def __repr__(self):
        return f'<Formula {self.nombre}>'


class FormulaLinea(db.Model):
    __tablename__ = 'formula_lineas'
    id = db.Column(db.Integer, primary_key=True)
    formula_id = db.Column(db.Integer, db.ForeignKey('formulas.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey('insumos.id'), nullable=True)
    mano_obra_id = db.Column(db.Integer, db.ForeignKey('mano_de_obra.id'), nullable=True)
    concepto = db.Column(db.String(200))
    cantidad = db.Column(db.Numeric(12, 4), nullable=False, default=1)
    tarifa = db.Column(db.Numeric(12, 2), nullable=True)
    orden = db.Column(db.Integer, default=0)
    insumo = db.relationship('Insumo', lazy=True)
    mano_obra = db.relationship('ManoDeObra', lazy=True)

    def __repr__(self):
        return f'<FormulaLinea {self.tipo}>'


def init_db():
    db.create_all()
    _seed_categorias()
    _seed_rubros()
    _seed_config()
    _seed_productos()


def _seed_config():
    defaults = {
        'ajuste_inflacion': '15',
        'amort_herramientas': '6',
        'margen_default': '40',
        'mp_comision_default': '5',
        'descuento_default': '10',
    }
    for clave, valor in defaults.items():
        if not Configuracion.query.get(clave):
            db.session.add(Configuracion(clave=clave, valor=valor))
    db.session.commit()


def _seed_rubros():
    if Rubro.query.count() > 0:
        return
    rubros = ['arcilla', 'engobe', 'packaging', 'taller', 'herramientas', 'otro']
    for i, nombre in enumerate(rubros):
        db.session.add(Rubro(nombre=nombre, orden=i))
    db.session.commit()


def _seed_categorias():
    if Categoria.query.count() > 0:
        return
    cats = [
        Categoria(nombre='Tazas y Pocillos', slug='tazas', orden=1),
        Categoria(nombre='Platos y Fuentes', slug='platos', orden=2),
        Categoria(nombre='Macetas', slug='macetas', orden=3),
        Categoria(nombre='Decoración', slug='decoracion', orden=4),
        Categoria(nombre='Bijouterie', slug='bijouterie', orden=5),
    ]
    db.session.add_all(cats)
    db.session.commit()


def _seed_productos():
    if Producto.query.count() > 0:
        return
    cat_map = {c.slug: c.id for c in Categoria.query.all()}
    demos = [
        Producto(nombre='Taza Espiral', descripcion='Taza artesanal con diseño en espiral, perfecta para el café de la mañana. Cada pieza es única, hecha a mano con arcilla de alta calidad.', precio=4500, categoria_id=cat_map.get('tazas'), destacado=True),
        Producto(nombre='Pocillo Café', descripcion='Pocillo de café pequeño con esmalte satinado. Capacidad 80ml. Resistente al lavavajillas.', precio=3200, categoria_id=cat_map.get('tazas'), destacado=True),
        Producto(nombre='Taza Bollo', descripcion='Taza grande tipo bollo para mate cocido o té. 350ml. Acabado rústico con textura a la vista.', precio=5000, categoria_id=cat_map.get('tazas')),
        Producto(nombre='Plato Cactus', descripcion='Plato decorativo pintado a mano con motivos de cactus. Apto uso en mesa, ideal también como centro de mesa.', precio=6200, categoria_id=cat_map.get('platos'), destacado=True),
        Producto(nombre='Fuente Oval', descripcion='Fuente oval para ensaladas o pastas. Tamaño mediano (30cm). Esmalte verde salvia interior, terracota exterior.', precio=9800, categoria_id=cat_map.get('platos')),
        Producto(nombre='Platito Manteca', descripcion='Platito individual para manteca o dips. Set de 2 unidades.', precio=3800, categoria_id=cat_map.get('platos')),
        Producto(nombre='Maceta Texturada', descripcion='Maceta con textura de rafia prensada. Ideal para suculentas y cactus. Con plato incluido.', precio=7500, categoria_id=cat_map.get('macetas'), destacado=True),
        Producto(nombre='Maceta Colgante', descripcion='Maceta colgante para plantas de interior. Con correa de cuero natural. Diámetro 12cm.', precio=8200, categoria_id=cat_map.get('macetas')),
        Producto(nombre='Jarrón Espiga', descripcion='Jarrón decorativo alto (25cm) con relieve de espigas. Perfecto para flores secas o ramas.', precio=11500, categoria_id=cat_map.get('decoracion')),
        Producto(nombre='Cuenco Luna', descripcion='Cuenco en forma de luna creciente. Ideal para joyería, llaves o como decoración.', precio=5500, categoria_id=cat_map.get('decoracion')),
        Producto(nombre='Aretes Espiral', descripcion='Aretes colgantes con diseño de espiral. Peso muy liviano, arcilla de alta cocción. Incluye ganchos de acero inoxidable.', precio=4200, categoria_id=cat_map.get('bijouterie')),
        Producto(nombre='Collar Medallón', descripcion='Collar con medallón redondo pintado a mano. Cordón de cuero ajustable. Diámetro 3cm.', precio=5800, categoria_id=cat_map.get('bijouterie')),
    ]
    db.session.add_all(demos)
    db.session.commit()
