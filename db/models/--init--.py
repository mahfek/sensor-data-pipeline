from db.base import Base
from db.models.lidar import Lidar


# این باعث می‌شه وقتی Alembic یا Base.metadata.create_all صدا زده بشه
# همه مدل‌ها شناخته بشن
__all__ = [
    "Base",
    "Lidar",
    
]
