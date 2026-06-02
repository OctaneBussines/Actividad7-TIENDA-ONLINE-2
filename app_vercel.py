from flask import Flask

def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tienda Online</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; background: #f5f5f5; }
                h1 { color: #333; }
                .info { background: white; padding: 20px; border-radius: 5px; max-width: 600px; margin: 0 auto; }
            </style>
        </head>
        <body>
            <div class="info">
                <h1>✅ Tienda Online - Funcionando en Vercel</h1>
                <p><strong>El servidor está activo y corriendo correctamente.</strong></p>
                <p>La versión actual es de prueba sin base de datos.</p>
                <p>Para una versión completa con autenticación y carrito de compras, necesitas migrar a una BD en la nube (MongoDB, PostgreSQL, etc.)</p>
            </div>
        </body>
        </html>
        '''
    
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'Server is running'}, 200

app = create_app()
