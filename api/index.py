from app import create_app

app = create_app()

# Vercel serverless handler
def handler(request, context):
    return app(request)