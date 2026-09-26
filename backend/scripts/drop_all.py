import app.contexts.user.models
import app.contexts.assignment.models
import app.contexts.submission.models
from app.core.database import Base, engine

Base.metadata.drop_all(engine)
print("dropped")
