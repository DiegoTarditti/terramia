import os
import cloudinary
from flask import Flask
from database import db, init_db
from routes.tienda import tienda_bp
from routes.carrito import carrito_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'terramia-dev-secret-2024')
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///terramia.db')
    # Driver explícito: SQLAlchemy 2.1 usa psycopg v3 por defecto con "postgresql://",
    # y acá está instalado psycopg2.
    for prefijo in ('postgres://', 'postgresql://'):
        if db_url.startswith(prefijo):
            db_url = 'postgresql+psycopg2://' + db_url[len(prefijo):]
            break
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'terramia2024')
    app.config['WHATSAPP_NUMBER'] = os.environ.get('WHATSAPP_NUMBER', '5493412729325')

    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
        api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET', ''),
    )

    db.init_app(app)
    app.register_blueprint(tienda_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.context_processor
    def inject_carrito():
        from flask import session
        carrito = session.get('carrito', {})
        return {'carrito_cantidad': sum(carrito.values())}

    @app.template_filter('peso')
    def peso_filter(value):
        try:
            return f"${round(float(value)):,}".replace(',', '.')
        except Exception:
            return '—'

    with app.app_context():
        init_db()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5005)
