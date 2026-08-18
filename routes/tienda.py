from flask import Blueprint, render_template, request, abort
from database import Producto, Categoria

tienda_bp = Blueprint('tienda', __name__)


@tienda_bp.route('/')
def index():
    destacados = Producto.query.filter_by(activo=True, destacado=True).limit(8).all()
    categorias = Categoria.query.order_by(Categoria.orden).all()
    return render_template('index.html', destacados=destacados, categorias=categorias)


@tienda_bp.route('/catalogo')
def catalogo():
    categorias = Categoria.query.filter(Categoria.slug != 'bijouterie').order_by(Categoria.orden).all()
    cat_slug = request.args.get('cat', '')
    q = request.args.get('q', '').strip()

    bijouterie = Categoria.query.filter_by(slug='bijouterie').first()
    query = Producto.query.filter_by(activo=True)
    if bijouterie:
        query = query.filter(Producto.categoria_id != bijouterie.id)

    if cat_slug:
        cat = Categoria.query.filter_by(slug=cat_slug).first()
        if cat:
            query = query.filter_by(categoria_id=cat.id)

    if q:
        query = query.filter(Producto.nombre.ilike(f'%{q}%'))

    precio = request.args.get('precio', '')
    if precio == '0-5000':
        query = query.filter(Producto.precio <= 5000)
    elif precio == '5000-10000':
        query = query.filter(Producto.precio > 5000, Producto.precio <= 10000)
    elif precio == '10000+':
        query = query.filter(Producto.precio > 10000)

    productos = query.order_by(Producto.destacado.desc(), Producto.nombre).all()
    cat_activa = cat_slug

    return render_template('catalogo.html', productos=productos, categorias=categorias,
                           cat_activa=cat_activa, q=q)


PALETA_COLORES = [
    {'nombre': 'Rosa pálido',         'hex': '#F0AAAA'},
    {'nombre': 'Rojo coral',           'hex': '#DC5248'},
    {'nombre': 'Naranja quemado',      'hex': '#C85820'},
    {'nombre': 'Beige',                'hex': '#D4C0A0'},
    {'nombre': 'Amarillo limón',       'hex': '#E8EC40'},
    {'nombre': 'Amarillo medio',       'hex': '#ECC020'},
    {'nombre': 'Ocre / vainilla',      'hex': '#EDD8A8'},
    {'nombre': 'Berenjena oscuro',     'hex': '#481428'},
    {'nombre': 'Rosa viejo',           'hex': '#C89090'},
    {'nombre': 'Azul cobalto',         'hex': '#3870C0'},
    {'nombre': 'Verde pistacho',       'hex': '#9EC888'},
    {'nombre': 'Gris pálido',          'hex': '#C8CED8'},
    {'nombre': 'Turquesa fuerte',      'hex': '#28B8C8'},
]


@tienda_bp.route('/producto/<int:id>')
def producto(id):
    p = Producto.query.filter_by(id=id, activo=True).first_or_404()
    relacionados = Producto.query.filter(
        Producto.categoria_id == p.categoria_id,
        Producto.id != p.id,
        Producto.activo == True
    ).limit(4).all()
    complementarios = Producto.query.filter(
        Producto.categoria_id != p.categoria_id,
        Producto.activo == True
    ).limit(3).all()
    return render_template('producto.html', producto=p, relacionados=relacionados,
                           complementarios=complementarios)


@tienda_bp.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')


@tienda_bp.route('/guia-de-compras')
def guia_compras():
    return render_template('guia-compras.html')


@tienda_bp.route('/preguntas-frecuentes')
def preguntas_frecuentes():
    return render_template('preguntas-frecuentes.html')


@tienda_bp.route('/metodos-de-pago')
def metodos_pago():
    return render_template('metodos-pago.html')


@tienda_bp.route('/politicas-de-devolucion')
def politicas_devolucion():
    return render_template('politicas-devolucion.html')
