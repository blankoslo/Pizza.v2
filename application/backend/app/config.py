import os

class Base(object):
  # DATABASE_URL is the environment variable created by heroku during production deployment
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1) if 'DATABASE_URL' in os.environ else f'postgresql://{os.environ.get("DB_USER")}:{os.environ.get("DB_PASSWD")}@{os.environ.get("DB_HOST")}:{os.environ.get("DB_PORT")}/{os.environ.get("DB_NAME")}'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
  GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
  GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
  API_TITLE = "API"
  API_VERSION = "v1"
  # Swagger config
  OPENAPI_VERSION = "3.0.2"
  # Api json docs is available under /doc/openapi.json
  OPENAPI_URL_PREFIX = "/doc"
  # The swagger UI is displayed under /doc/swagger
  OPENAPI_SWAGGER_UI_PATH = "/swagger"
  # The following is equivalent to OPENAPI_SWAGGER_UI_VERSION = '3.19.5'
  OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.19.5/"