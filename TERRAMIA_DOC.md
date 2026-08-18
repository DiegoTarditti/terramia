# Terramia — Documentación del sitio web

## ¿De qué se trata?

**Terramia** es una tienda online de cerámica artesanal. El sitio permite a los clientes explorar y comprar piezas únicas hechas a mano: tazas, platos, macetas, decoración y bijouterie. El proceso de compra culmina con un pedido por **WhatsApp**, sin pasarela de pago tradicional.

---

## Páginas públicas

### Inicio (`/`)
La página de bienvenida del sitio. Muestra:
- Sección hero con identidad de marca
- Grilla de **productos destacados** (hasta 8 piezas marcadas como destacadas)
- Listado de categorías disponibles con acceso directo al catálogo filtrado

---

### Catálogo (`/catalogo`)
El catálogo completo de productos con tres filtros combinables:

| Filtro | Opciones |
|---|---|
| Categoría | Tazas y Pocillos / Platos y Fuentes / Macetas / Decoración / Bijouterie |
| Búsqueda | Por nombre de producto (texto libre) |
| Rango de precio | Hasta $5.000 / $5.000–$10.000 / Más de $10.000 |

Los productos se ordenan mostrando primero los destacados. Solo aparecen productos activos.

---

### Detalle de producto (`/producto/<id>`)
Página individual de cada pieza. Muestra:
- Imagen del producto
- Nombre, descripción completa, precio formateado
- Stock disponible (o sin límite si no tiene stock configurado)
- Botón para agregar al carrito (con AJAX, sin recargar la página)
- **Productos relacionados** de la misma categoría (hasta 4)

---

### Nosotros (`/nosotros`)
Página institucional con la historia y filosofía del emprendimiento.

---

### Carrito (`/carrito`)
Vista del carrito de compras. Incluye:
- Lista de productos agregados con imagen, nombre, precio unitario y subtotal
- Control de cantidad por ítem (se puede editar y actualizar)
- Botón para quitar productos individuales
- Total del pedido
- **Botón de checkout por WhatsApp**: genera un mensaje formateado automáticamente con el detalle del pedido y lo abre en WhatsApp con el número configurado

Ejemplo del mensaje generado:
```
Hola Terramia! 🏺 Quiero hacer el siguiente pedido:

• 2 × Taza Espiral ($4.500 c/u) → $9.000
• 1 × Maceta Texturada ($7.500 c/u) → $7.500

*Total: $16.500*

¿Tienen disponibilidad? ¡Muchas gracias! 😊
```

---

## Panel de administración (`/admin`)

Acceso con contraseña. Permite gestionar todo el contenido del sitio.

### Dashboard (`/admin/`)
Resumen con 4 indicadores:
- Total de productos activos
- Total de categorías
- Productos sin stock
- Productos destacados

### Gestión de productos (`/admin/productos`)
- Listado de todos los productos con filtro por categoría y búsqueda
- Crear nuevo producto
- Editar producto existente
- Activar / desactivar producto (sin eliminarlo)
- Eliminar producto definitivamente

Campos de cada producto:

| Campo | Descripción |
|---|---|
| Nombre | Nombre de la pieza |
| Descripción | Texto libre |
| Precio | En pesos argentinos |
| Stock | Número de unidades disponibles (vacío = sin límite) |
| Categoría | Clasificación de la pieza |
| Imagen | Subida de archivo (PNG, JPG, WEBP, GIF) o URL externa |
| Destacado | Aparece en la sección hero del inicio |
| Activo | Visible en la tienda o no |

### Gestión de categorías (`/admin/categorias`)
- Ver todas las categorías con cantidad de productos asociados
- Crear nueva categoría (genera slug automáticamente)
- Eliminar categoría (solo si no tiene productos)

---

## Productos de demo (datos iniciales)

Al iniciar por primera vez la base de datos se cargan automáticamente:

### Tazas y Pocillos
| Producto | Precio | Destacado |
|---|---|---|
| Taza Espiral | $4.500 | ✓ |
| Pocillo Café | $3.200 | ✓ |
| Taza Bollo | $5.000 | — |

### Platos y Fuentes
| Producto | Precio | Destacado |
|---|---|---|
| Plato Cactus | $6.200 | ✓ |
| Fuente Oval | $9.800 | — |
| Platito Manteca | $3.800 | — |

### Macetas
| Producto | Precio | Destacado |
|---|---|---|
| Maceta Texturada | $7.500 | ✓ |
| Maceta Colgante | $8.200 | — |

### Decoración
| Producto | Precio |
|---|---|
| Jarrón Espiga | $11.500 |
| Cuenco Luna | $5.500 |

### Bijouterie
| Producto | Precio |
|---|---|
| Aretes Espiral | $4.200 |
| Collar Medallón | $5.800 |

---

## Tecnología

| Capa | Tecnología |
|---|---|
| Backend | Python + Flask |
| Base de datos | SQLite (SQLAlchemy) |
| Frontend | HTML + CSS + JavaScript vanilla |
| Plantillas | Jinja2 |
| Servidor | Gunicorn (producción) |
| Checkout | WhatsApp (`wa.me`) |

### Variables de entorno configurables

| Variable | Descripción | Default |
|---|---|---|
| `SECRET_KEY` | Clave de sesión Flask | `terramia-dev-secret-2024` |
| `ADMIN_PASSWORD` | Contraseña del panel admin | `terramia2024` |
| `WHATSAPP_NUMBER` | Número de WhatsApp del negocio | `5491100000000` |
| `DATABASE_URL` | Ruta de la base de datos | `sqlite:///terramia.db` |

---

## Estructura de carpetas

```
Terramia/
├── app.py                  # Punto de entrada
├── database.py             # Modelos y datos iniciales
├── routes/
│   ├── tienda.py           # Páginas públicas
│   ├── carrito.py          # Carrito y checkout
│   └── admin.py            # Panel de administración
├── templates/
│   ├── base.html           # Layout principal
│   ├── index.html          # Inicio
│   ├── catalogo.html       # Catálogo
│   ├── producto.html       # Detalle de producto
│   ├── carrito.html        # Carrito
│   ├── nosotros.html       # Nosotros
│   └── admin/              # Templates del panel admin
├── static/
│   ├── css/style.css       # Estilos (paleta cerámica)
│   ├── js/main.js          # Interactividad (menú, AJAX)
│   └── uploads/            # Imágenes subidas
└── fonts/                  # Fuentes Cocomat Pro + Halimun
```
