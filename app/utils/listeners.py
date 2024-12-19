from sqlalchemy import event
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Tag, MarkerAuditLog

# Listen for the delete event on the Tag model
@event.listens_for(Tag, 'before_delete')
def log_tag_deletion(mapper, connection, target):
    tag = target  # The deleted Tag instance
    
    # Get all markers that are associated with this tag
    markers = tag.markers

    # Log the deletion in an audit log or marker audit log
    for marker in markers:
        # Create a custom log entry for each marker with the removed tag
        audit_log_entry = MarkerAuditLog(
            marker_id=marker.id,
            action="tag_deleted",
            user_id=None,  # Optionally, track the user who performed the action
            timestamp=datetime.utcnow(),
            additional_info={"deleted_tag_id": tag.id, "deleted_tag_name": tag.name}
        )
        
        # Assuming you have a session, add the audit log
        session = Session.object_session(marker)
        session.add(audit_log_entry)
    
    # Continue with the delete operation (automatic handling by SQLAlchemy)
