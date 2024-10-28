from app import create_app
from app.extensions import db, migrate
from dotenv import load_dotenv

load_dotenv()

app = create_app()

@app.cli.command("db_create")
def db_create():
    """Create the database tables."""
    from compliance_lib_models import Base as ComplianceBase
    ComplianceBase.metadata.create_all(bind=db.engine)

@app.cli.command("db_init")
def db_init():
    """Initialize the database."""
    from flask_migrate import init
    init()

@app.cli.command("db_upgrade")
def db_upgrade():
    """Apply database migrations."""
    from flask_migrate import upgrade
    upgrade()

@app.cli.command("db_downgrade")
def db_downgrade():
    """Downgrade database migrations."""
    from flask_migrate import downgrade
    downgrade()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
