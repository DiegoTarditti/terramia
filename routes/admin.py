import os
import secrets
from datetime import datetime, date
from flask import (Blueprint, render_template, session, redirect, url_for,
                   request, flash, current_app)
from werkzeug.utils import secure_filename
import cloudinary.uploader
from database import db, Producto, Categoria, Insumo, Formula, FormulaLinea, ManoDeObra, Rubro, Configuracion

def _get_rubros():
    return Rubro.query.filter_by(activo=True).order_by(Rubro.orden, Rubro.nombre).all()

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@_login_required
def dashboard():
    total_productos = Producto.query.filter_by(activo=True).count()
    total_categorias = Categoria.query.count()
    sin_stock = Producto.query.filter(Producto.activo == True, Producto.stock == 0).count()
    destacados = Producto.query.filter_by(activo=True, destacado=True).count()
    return render_template('admin/dashboard.html', total_productos=total_productos,
                           total_categorias=total_categorias, sin_stock=sin_stock,
                           destacados=destacados)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    error = None
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if secrets.compare_digest(pwd, current_app.config['ADMIN_PASSWORD']):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        error = 'Contraseña incorrecta'
    return render_template('admin/login.html', error=error)


@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))


@admin_bp.route('/productos')
@_login_required
def productos():
    cat_id = request.args.get('cat', type=int)
    q = request.args.get('q', '').strip()
    query = Producto.query
    if cat_id:
        query = query.filter_by(categoria_id=cat_id)
    if q:
        query = query.filter(Producto.nombre.ilike(f'%{q}%'))
    prods = query.order_by(Producto.activo.desc(), Producto.nombre).all()
    categorias = Categoria.query.order_by(Categoria.orden).all()
    return render_template('admin/productos.html', productos=prods, categorias=categorias,
                           cat_id=cat_id, q=q)


@admin_bp.route('/productos/nuevo', methods=['GET', 'POST'])
@_login_required
def producto_nuevo():
    categorias = Categoria.query.order_by(Categoria.orden).all()
    if request.method == 'POST':
        p = _producto_desde_form(Producto())
        if p:
            db.session.add(p)
            db.session.commit()
            flash('Producto creado correctamente.', 'ok')
            return redirect(url_for('admin.productos'))
    return render_template('admin/producto_form.html', producto=None, categorias=categorias, titulo='Nuevo producto')


@admin_bp.route('/productos/<int:id>/editar', methods=['GET', 'POST'])
@_login_required
def producto_editar(id):
    p = Producto.query.get_or_404(id)
    categorias = Categoria.query.order_by(Categoria.orden).all()
    if request.method == 'POST':
        p = _producto_desde_form(p)
        if p:
            db.session.commit()
            flash('Producto actualizado.', 'ok')
            return redirect(url_for('admin.productos'))
    return render_template('admin/producto_form.html', producto=p, categorias=categorias, titulo='Editar producto')


@admin_bp.route('/productos/<int:id>/toggle', methods=['POST'])
@_login_required
def producto_toggle(id):
    p = Producto.query.get_or_404(id)
    p.activo = not p.activo
    db.session.commit()
    estado = 'activado' if p.activo else 'desactivado'
    flash(f'"{p.nombre}" {estado}.', 'ok')
    return redirect(url_for('admin.productos'))


@admin_bp.route('/productos/<int:id>/eliminar', methods=['POST'])
@_login_required
def producto_eliminar(id):
    p = Producto.query.get_or_404(id)
    nombre = p.nombre
    db.session.delete(p)
    db.session.commit()
    flash(f'"{nombre}" eliminado.', 'ok')
    return redirect(url_for('admin.productos'))


@admin_bp.route('/categorias', methods=['GET', 'POST'])
@_login_required
def categorias():
    if request.method == 'POST':
        accion = request.form.get('accion')
        if accion == 'crear':
            nombre = request.form.get('nombre', '').strip()
            if nombre:
                slug = nombre.lower().replace(' ', '-').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
                if not Categoria.query.filter_by(slug=slug).first():
                    c = Categoria(nombre=nombre, slug=slug)
                    db.session.add(c)
                    db.session.commit()
                    flash(f'Categoría "{nombre}" creada.', 'ok')
        elif accion == 'eliminar':
            cid = request.form.get('id', type=int)
            cat = Categoria.query.get(cid)
            if cat:
                if cat.productos:
                    flash('No se puede eliminar: tiene productos asociados.', 'error')
                else:
                    db.session.delete(cat)
                    db.session.commit()
                    flash('Categoría eliminada.', 'ok')
        return redirect(url_for('admin.categorias'))
    cats = Categoria.query.order_by(Categoria.orden).all()
    return render_template('admin/categorias.html', categorias=cats)


@admin_bp.route('/insumos')
@_login_required
def insumos():
    cat = request.args.get('cat', '')
    q = request.args.get('q', '').strip()
    query = Insumo.query.filter_by(activo=True)
    if cat:
        query = query.filter_by(categoria=cat)
    if q:
        query = query.filter(Insumo.nombre.ilike(f'%{q}%'))
    items = query.order_by(Insumo.categoria, Insumo.nombre).all()
    return render_template('admin/insumos.html', insumos=items, cat=cat, q=q,
                           categorias=_get_rubros())


@admin_bp.route('/insumos/nuevo', methods=['POST'])
@_login_required
def insumo_nuevo():
    ins = _insumo_desde_form(Insumo())
    if ins:
        db.session.add(ins)
        db.session.commit()
        flash(f'"{ins.nombre}" agregado.', 'ok')
    return redirect(url_for('admin.insumos'))


@admin_bp.route('/insumos/<int:id>/editar', methods=['GET', 'POST'])
@_login_required
def insumo_editar(id):
    ins = Insumo.query.get_or_404(id)
    if request.method == 'POST':
        updated = _insumo_desde_form(ins)
        if updated:
            updated.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f'"{updated.nombre}" actualizado.', 'ok')
            return redirect(url_for('admin.insumos'))
    return render_template('admin/insumo_form.html', insumo=ins,
                           categorias=_get_rubros())


@admin_bp.route('/insumos/<int:id>/eliminar', methods=['POST'])
@_login_required
def insumo_eliminar(id):
    ins = Insumo.query.get_or_404(id)
    nombre = ins.nombre
    ins.activo = False
    db.session.commit()
    flash(f'"{nombre}" eliminado.', 'ok')
    return redirect(url_for('admin.insumos'))


@admin_bp.route('/rubros', methods=['GET', 'POST'])
@_login_required
def rubros():
    if request.method == 'POST':
        accion = request.form.get('accion')
        if accion == 'crear':
            nombre = request.form.get('nombre', '').strip().lower()
            if nombre:
                if Rubro.query.filter_by(nombre=nombre).first():
                    flash(f'Ya existe el rubro "{nombre}".', 'error')
                else:
                    orden = Rubro.query.count()
                    db.session.add(Rubro(nombre=nombre, orden=orden))
                    db.session.commit()
                    flash(f'Rubro "{nombre}" creado.', 'ok')
        elif accion == 'eliminar':
            rid = request.form.get('id', type=int)
            r = Rubro.query.get(rid)
            if r:
                usos = Insumo.query.filter_by(categoria=r.nombre, activo=True).count()
                if usos:
                    flash(f'No se puede eliminar: {usos} insumo(s) lo usan.', 'error')
                else:
                    r.activo = False
                    db.session.commit()
                    flash(f'"{r.nombre}" eliminado.', 'ok')
        elif accion == 'editar':
            rid = request.form.get('id', type=int)
            r = Rubro.query.get(rid)
            nombre_nuevo = request.form.get('nombre_nuevo', '').strip().lower()
            if r and nombre_nuevo:
                r.nombre = nombre_nuevo
                db.session.commit()
                flash('Rubro actualizado.', 'ok')
        return redirect(url_for('admin.rubros'))
    items = _get_rubros()
    conteos = {r.nombre: Insumo.query.filter_by(categoria=r.nombre, activo=True).count()
               for r in items}
    return render_template('admin/rubros.html', rubros=items, conteos=conteos)


@admin_bp.route('/mano-de-obra')
@_login_required
def mano_de_obra():
    items = ManoDeObra.query.filter_by(activo=True).order_by(ManoDeObra.nombre).all()
    return render_template('admin/mano_obra.html', items=items)


@admin_bp.route('/mano-de-obra/nueva', methods=['POST'])
@_login_required
def mano_de_obra_nueva():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'error')
        return redirect(url_for('admin.mano_de_obra'))
    try:
        tarifa = float(request.form.get('tarifa_hora', '0').replace(',', '.'))
    except ValueError:
        flash('La tarifa debe ser un número.', 'error')
        return redirect(url_for('admin.mano_de_obra'))
    mdo = ManoDeObra(nombre=nombre, tarifa_hora=tarifa,
                     notas=request.form.get('notas', '').strip() or None)
    db.session.add(mdo)
    db.session.commit()
    flash(f'"{mdo.nombre}" agregado.', 'ok')
    return redirect(url_for('admin.mano_de_obra'))


@admin_bp.route('/mano-de-obra/<int:id>/editar', methods=['GET', 'POST'])
@_login_required
def mano_de_obra_editar(id):
    mdo = ManoDeObra.query.get_or_404(id)
    if request.method == 'POST':
        mdo.nombre = request.form.get('nombre', '').strip()
        try:
            mdo.tarifa_hora = float(request.form.get('tarifa_hora', '0').replace(',', '.'))
        except ValueError:
            flash('La tarifa debe ser un número.', 'error')
            return redirect(url_for('admin.mano_de_obra'))
        mdo.notas = request.form.get('notas', '').strip() or None
        db.session.commit()
        flash(f'"{mdo.nombre}" actualizado.', 'ok')
        return redirect(url_for('admin.mano_de_obra'))
    return render_template('admin/mano_obra_form.html', mdo=mdo)


@admin_bp.route('/mano-de-obra/<int:id>/eliminar', methods=['POST'])
@_login_required
def mano_de_obra_eliminar(id):
    mdo = ManoDeObra.query.get_or_404(id)
    nombre = mdo.nombre
    mdo.activo = False
    db.session.commit()
    flash(f'"{nombre}" eliminado.', 'ok')
    return redirect(url_for('admin.mano_de_obra'))


@admin_bp.route('/formulas')
@_login_required
def formulas():
    fmls = Formula.query.filter_by(activo=True).order_by(Formula.nombre).all()
    resumen = [{'f': f, 'c': f.calcular()} for f in fmls]
    return render_template('admin/formulas.html', resumen=resumen)


@admin_bp.route('/configuracion', methods=['GET', 'POST'])
@_login_required
def configuracion():
    CLAVES = [
        ('ajuste_inflacion',    'Reserva por inflación (%)',     'Porcentaje que se suma sobre materiales para cubrir inflación entre compra y venta'),
        ('amort_herramientas',  'Amortización de herramientas (%)', 'Porcentaje sobre materiales para reponer/mantener herramientas'),
        ('margen_default',      'Margen de ganancia (%)',        'Margen sobre el costo total para llegar al PVP'),
        ('mp_comision_default', 'Comisión MercadoPago (%)',      'Porcentaje de comisión aplicado al precio final'),
        ('descuento_default',   'Descuento efectivo (%)',        'Descuento que ofrecés en efectivo/transferencia'),
    ]
    if request.method == 'POST':
        for clave, _, _ in CLAVES:
            val = request.form.get(clave, '').replace(',', '.').strip()
            try:
                float(val)
                Configuracion.set(clave, val)
            except ValueError:
                flash(f'Valor inválido para {clave}.', 'error')
                return redirect(url_for('admin.configuracion'))
        db.session.commit()
        flash('Configuración guardada.', 'ok')
        return redirect(url_for('admin.configuracion'))
    valores = {clave: Configuracion.get(clave, '0') for clave, _, _ in CLAVES}
    return render_template('admin/configuracion.html', claves=CLAVES, valores=valores)


@admin_bp.route('/formulas/nueva', methods=['GET', 'POST'])
@_login_required
def formula_nueva():
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()
    if request.method == 'POST':
        f = _formula_desde_form(Formula())
        if f:
            db.session.add(f)
            db.session.commit()
            flash(f'"{f.nombre}" creada.', 'ok')
            return redirect(url_for('admin.formula_detalle', id=f.id))
    defaults = {
        'amort_pct':       Configuracion.get('amort_herramientas', '6'),
        'reserva_pct':     Configuracion.get('ajuste_inflacion', '15'),
        'margen_pct':      Configuracion.get('margen_default', '40'),
        'mp_comision_pct': Configuracion.get('mp_comision_default', '5'),
        'descuento_pct':   Configuracion.get('descuento_default', '10'),
    }
    return render_template('admin/formula_form.html', formula=None, productos=productos,
                           titulo='Nueva fórmula', defaults=defaults)


@admin_bp.route('/formulas/<int:id>')
@_login_required
def formula_detalle(id):
    f = Formula.query.get_or_404(id)
    c = f.calcular()
    insumos = Insumo.query.filter_by(activo=True).order_by(Insumo.categoria, Insumo.nombre).all()
    manos = ManoDeObra.query.filter_by(activo=True).order_by(ManoDeObra.nombre).all()
    return render_template('admin/formula_detalle.html', formula=f, c=c,
                           insumos=insumos, manos=manos)


@admin_bp.route('/formulas/<int:id>/editar', methods=['GET', 'POST'])
@_login_required
def formula_editar(id):
    f = Formula.query.get_or_404(id)
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()
    if request.method == 'POST':
        updated = _formula_desde_form(f)
        if updated:
            db.session.commit()
            flash('Configuración actualizada.', 'ok')
            return redirect(url_for('admin.formula_detalle', id=f.id))
    return render_template('admin/formula_form.html', formula=f, productos=productos,
                           titulo='Editar fórmula')


@admin_bp.route('/formulas/<int:id>/eliminar', methods=['POST'])
@_login_required
def formula_eliminar(id):
    f = Formula.query.get_or_404(id)
    nombre = f.nombre
    f.activo = False
    db.session.commit()
    flash(f'"{nombre}" eliminada.', 'ok')
    return redirect(url_for('admin.formulas'))


@admin_bp.route('/formulas/<int:id>/pvp', methods=['POST'])
@_login_required
def formula_pvp(id):
    f = Formula.query.get_or_404(id)
    pvp_str = request.form.get('pvp_override', '').replace(',', '.').strip()
    if pvp_str:
        try:
            f.pvp_override = float(pvp_str)
        except ValueError:
            flash('PVP inválido.', 'error')
            return redirect(url_for('admin.formula_detalle', id=id))
    else:
        f.pvp_override = None
    db.session.commit()
    flash('PVP actualizado.', 'ok')
    return redirect(url_for('admin.formula_detalle', id=id))


@admin_bp.route('/formulas/<int:id>/linea', methods=['POST'])
@_login_required
def formula_linea_nueva(id):
    f = Formula.query.get_or_404(id)
    tipo = request.form.get('tipo', '')
    try:
        cantidad = float(request.form.get('cantidad', '0').replace(',', '.'))
    except ValueError:
        flash('Cantidad inválida.', 'error')
        return redirect(url_for('admin.formula_detalle', id=id))
    if cantidad <= 0:
        flash('La cantidad debe ser mayor a 0.', 'error')
        return redirect(url_for('admin.formula_detalle', id=id))

    linea = FormulaLinea(formula_id=id, tipo=tipo, cantidad=cantidad,
                         orden=len([l for l in f.lineas if l.tipo == tipo]))

    item_ref = request.form.get('item_ref', '')
    if item_ref.startswith('i_'):
        linea.tipo = 'insumo'
        linea.insumo_id = int(item_ref[2:])
    elif item_ref.startswith('m_'):
        linea.tipo = 'mano_obra'
        mdo_id = int(item_ref[2:])
        linea.mano_obra_id = mdo_id
        mdo = ManoDeObra.query.get(mdo_id)
        linea.concepto = mdo.nombre if mdo else 'Mano de obra'
    else:
        flash('Seleccioná un ítem.', 'error')
        return redirect(url_for('admin.formula_detalle', id=id))

    db.session.add(linea)
    db.session.commit()
    return redirect(url_for('admin.formula_detalle', id=id))


@admin_bp.route('/formulas/<int:fid>/linea/<int:lid>/eliminar', methods=['POST'])
@_login_required
def formula_linea_eliminar(fid, lid):
    linea = FormulaLinea.query.get_or_404(lid)
    if linea.formula_id != fid:
        flash('Error.', 'error')
        return redirect(url_for('admin.formulas'))
    db.session.delete(linea)
    db.session.commit()
    return redirect(url_for('admin.formula_detalle', id=fid))


def _formula_desde_form(f):
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'error')
        return None

    def pct(name, default):
        try:
            return float(request.form.get(name, str(default)).replace(',', '.'))
        except ValueError:
            return default

    f.nombre = nombre
    f.producto_id = request.form.get('producto_id', type=int) or None
    f.amort_pct = pct('amort_pct', 6)
    f.reserva_pct = pct('reserva_pct', 15)
    f.margen_pct = pct('margen_pct', 40)
    f.tarifa_taller = pct('tarifa_taller', 2200)
    f.mp_comision_pct = pct('mp_comision_pct', 5)
    f.descuento_pct = pct('descuento_pct', 10)
    return f


def _insumo_desde_form(ins):
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'error')
        return None
    try:
        precio = float(request.form.get('precio_compra', '0').replace(',', '.'))
        cantidad = float(request.form.get('cantidad_compra', '0').replace(',', '.'))
    except ValueError:
        flash('Precio y cantidad deben ser números.', 'error')
        return None
    if precio <= 0 or cantidad <= 0:
        flash('Precio y cantidad deben ser mayores a 0.', 'error')
        return None
    ins.nombre = nombre
    ins.categoria = request.form.get('categoria', 'otro')
    ins.proveedor = request.form.get('proveedor', '').strip() or None
    ins.unidad = request.form.get('unidad', 'unidad').strip()
    ins.precio_compra = precio
    ins.cantidad_compra = cantidad
    fecha_str = request.form.get('fecha_compra', '').strip()
    try:
        ins.fecha_compra = date.fromisoformat(fecha_str) if fecha_str else None
    except ValueError:
        ins.fecha_compra = None
    ins.notas = request.form.get('notas', '').strip() or None
    return ins


def _producto_desde_form(p):
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'error')
        return None
    precio_str = request.form.get('precio', '').replace(',', '.').strip()
    try:
        precio = float(precio_str)
    except ValueError:
        flash('El precio debe ser un número.', 'error')
        return None

    p.nombre = nombre
    p.descripcion = request.form.get('descripcion', '').strip()
    p.precio = precio
    stock_str = request.form.get('stock', '').strip()
    p.stock = int(stock_str) if stock_str.isdigit() else None
    cat_id = request.form.get('categoria_id', type=int)
    p.categoria_id = cat_id if cat_id else None
    p.destacado = bool(request.form.get('destacado'))
    p.activo = bool(request.form.get('activo', True))

    file = request.files.get('imagen')
    if file and file.filename and _allowed_file(file.filename):
        result = cloudinary.uploader.upload(
            file,
            folder='terramia',
            transformation={'quality': 'auto', 'fetch_format': 'auto'},
        )
        p.imagen = result['secure_url']
    elif request.form.get('imagen_url', '').strip():
        p.imagen = request.form.get('imagen_url').strip()

    return p
