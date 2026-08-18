import urllib.parse
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, current_app
from database import Producto

carrito_bp = Blueprint('carrito', __name__)


def _get_carrito():
    return session.get('carrito', {})


def _save_carrito(carrito):
    session['carrito'] = carrito
    session.modified = True


def _carrito_items():
    carrito = _get_carrito()
    if not carrito:
        return [], 0, 0
    ids = [int(k) for k in carrito.keys()]
    productos = {str(p.id): p for p in Producto.query.filter(Producto.id.in_(ids)).all()}
    items = []
    total = 0
    cantidad_total = 0
    for pid, qty in carrito.items():
        p = productos.get(pid)
        if p and p.activo:
            subtotal = float(p.precio) * qty
            items.append({'producto': p, 'cantidad': qty, 'subtotal': subtotal})
            total += subtotal
            cantidad_total += qty
    return items, total, cantidad_total


@carrito_bp.route('/carrito')
def ver_carrito():
    items, total, cantidad_total = _carrito_items()
    return render_template('carrito.html', items=items, total=total, cantidad_total=cantidad_total)


@carrito_bp.route('/carrito/agregar/<int:id>', methods=['POST'])
def agregar(id):
    p = Producto.query.filter_by(id=id, activo=True).first_or_404()
    carrito = _get_carrito()
    key = str(id)
    qty_actual = carrito.get(key, 0)
    qty_nueva = qty_actual + int(request.form.get('cantidad', 1))
    # Respetar stock si está definido
    if p.stock is not None:
        qty_nueva = min(qty_nueva, p.stock)
    carrito[key] = qty_nueva
    _save_carrito(carrito)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        _, _, cantidad_total = _carrito_items()
        return jsonify({'ok': True, 'cantidad_total': cantidad_total})
    return redirect(request.referrer or url_for('tienda.catalogo'))


@carrito_bp.route('/carrito/quitar/<int:id>', methods=['POST'])
def quitar(id):
    carrito = _get_carrito()
    key = str(id)
    if key in carrito:
        del carrito[key]
    _save_carrito(carrito)
    return redirect(url_for('carrito.ver_carrito'))


@carrito_bp.route('/carrito/actualizar', methods=['POST'])
def actualizar():
    carrito = _get_carrito()
    for key, val in request.form.items():
        if key.startswith('qty_'):
            pid = key[4:]
            try:
                qty = int(val)
                if qty <= 0:
                    carrito.pop(pid, None)
                else:
                    p = Producto.query.get(int(pid))
                    if p and p.activo:
                        if p.stock is not None:
                            qty = min(qty, p.stock)
                        carrito[pid] = qty
            except (ValueError, TypeError):
                pass
    _save_carrito(carrito)
    return redirect(url_for('carrito.ver_carrito'))


@carrito_bp.route('/carrito/checkout-whatsapp')
def checkout_whatsapp():
    items, total, _ = _carrito_items()
    if not items:
        return redirect(url_for('carrito.ver_carrito'))

    lineas = ['Hola Terramia! 🏺 Quiero hacer el siguiente pedido:\n']
    for item in items:
        p = item['producto']
        lineas.append(f"• {item['cantidad']} × {p.nombre} ({p.precio_fmt} c/u) → ${int(item['subtotal']):,}".replace(',', '.'))

    lineas.append(f'\n*Total: ${int(total):,}*'.replace(',', '.'))
    lineas.append('\n¿Tienen disponibilidad? ¡Muchas gracias! 😊')

    mensaje = '\n'.join(lineas)
    numero = current_app.config['WHATSAPP_NUMBER']
    url = f"https://wa.me/{numero}?text={urllib.parse.quote(mensaje)}"
    return redirect(url)


