from config import Config
from database.database import Database

tellybots = Database(Config.DATABASE_URL, Config.SESSION_NAME)

