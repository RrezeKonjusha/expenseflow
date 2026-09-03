"""MongoDB connection through MongoEngine (audit logs, report snapshots)."""

from urllib.parse import urlparse

import mongoengine
from django.conf import settings


def connect_mongo():
    url = settings.MONGO_URL
    mongoengine.disconnect_all()
    if url.startswith("mongomock://"):
        import mongomock

        db = urlparse(url).path.lstrip("/") or "test"
        mongoengine.connect(db, host="mongodb://localhost", mongo_client_class=mongomock.MongoClient)
    else:
        mongoengine.connect(host=url, uuidRepresentation="standard", serverSelectionTimeoutMS=3000)
