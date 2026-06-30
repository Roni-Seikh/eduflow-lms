"""
LMS Configuration — MySQL on Clever Cloud (DEV/Shared plan: 5 connection limit)
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def _get_db_uri():
    database_url = os.environ.get('DATABASE_URL', '')
    if database_url:
        # Ensure pymysql driver is specified even if pasted without it
        if database_url.startswith('mysql://'):
            database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
        return database_url

    host = os.environ.get('MYSQL_ADDON_HOST') or os.environ.get('DB_HOST')
    if host:
        port = os.environ.get('MYSQL_ADDON_PORT') or os.environ.get('DB_PORT', '3306')
        db   = os.environ.get('MYSQL_ADDON_DB')   or os.environ.get('DB_NAME')
        user = os.environ.get('MYSQL_ADDON_USER') or os.environ.get('DB_USER')
        pwd  = os.environ.get('MYSQL_ADDON_PASSWORD') or os.environ.get('DB_PASSWORD')
        return f'mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}'

    return 'mysql+pymysql://root:@localhost:3306/lms_db'


class Config:
    SECRET_KEY          = os.environ.get('SECRET_KEY') or 'lms-dev-key-CHANGE-in-production'
    WTF_CSRF_ENABLED    = True
    WTF_CSRF_TIME_LIMIT = 3600

    SQLALCHEMY_DATABASE_URI        = _get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Connection pool tuned for Clever Cloud's free DEV plan,
    #    which hard-caps you at 5 simultaneous connections TOTAL
    #    (shared across the Flask dev server's main + reloader process).
    #    Keep this small and recycle connections aggressively.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size':        2,     # only 2 persistent connections
        'max_overflow':     1,     # allow 1 extra burst connection
        'pool_recycle':     280,   # recycle before Clever Cloud's idle timeout
        'pool_pre_ping':    True,  # detect dead connections before using them
        'pool_timeout':     10,    # fail fast instead of hanging if pool is full
    }

    SESSION_PERMANENT          = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_HTTPONLY    = True
    SESSION_COOKIE_SAMESITE    = 'Lax'
    SESSION_COOKIE_NAME        = 'lms_session'

    MAX_CONTENT_LENGTH       = int(os.environ.get('MAX_CONTENT_LENGTH', 52428800))
    UPLOAD_FOLDER            = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
    ALLOWED_PDF_EXTENSIONS   = {'pdf'}

    MAIL_SERVER         = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT           = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS        = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL        = False
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', 'noreply@eduflow-lms.com')
    MAIL_ENABLED        = bool(os.environ.get('MAIL_USERNAME', ''))


class DevelopmentConfig(Config):
    DEBUG = True
    # IMPORTANT: do NOT use the auto-reloader locally with this DB —
    # it spawns a second process with its own connection pool, which
    # can push you over the 5-connection cap by itself. Run with:
    #   app.run(debug=True, use_reloader=False)
    # or set FLASK_DEBUG=0 and restart manually after each code change.


class ProductionConfig(Config):
    DEBUG                 = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
