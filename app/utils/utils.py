from sqlalchemy.orm import Session, aliased  # For type hinting and managing database sessions
from sqlalchemy import not_
from app.models import User, Marker, Location, Category, Tag, Organization, marker_tags, MarkerAuditLog, DeletedMarker
from app.utils.db_utils import SessionLocal, commit_session  # For session commit and error handling
from flask_login import current_user  # Ensure you import current_user if using Flask-Login
from datetime import datetime, timedelta
import logging
import random
import string

# Initialize logger
logger = logging.getLogger(__name__)

# Store verification codes temporarily (for simplicity, this can be in-memory or a cache like Redis in production)
verification_codes = {}

def generate_verification_code(length=6):
    """
    Generate a random verification code.
    """
    return ''.join(random.choices(string.digits, k=length))

def send_verification_code(user_email):
    """
    Send a verification code to the user's email or phone.
    This is a placeholder function; you would integrate with a service like SMS/email.
    """
    # Generate a verification code
    code = generate_verification_code()

    # Here we simply print the code to simulate sending it via email or SMS
    # In production, you would integrate with an email/SMS service.
    logger.info(f"Sending verification code to {user_email}: {code}")

    # Store the verification code temporarily with an expiration time (e.g., 10 minutes)
    verification_codes[user_email] = {
        'code': code,
        'expiry': datetime.utcnow() + timedelta(minutes=10)
    }

def verify_code(user_email, code):
    """
    Verify the code provided by the user against the stored code.
    """
    if user_email not in verification_codes:
        return False

    stored = verification_codes[user_email]
    
    # Check if the code is expired
    if stored['expiry'] < datetime.utcnow():
        logger.warning(f"Verification code for {user_email} has expired.")
        del verification_codes[user_email]  # Clean up expired code
        return False
    
    # Check if the code matches
    if stored['code'] == code:
        logger.info(f"Verification code for {user_email} verified successfully.")
        del verification_codes[user_email]  # Clean up after successful verification
        return True
    
    return False

def serialize_location(location):
    """
    Serialize location details.
    """
    return {
        "city": location.city if location else None,
        "state": location.state if location else None,
        "country": location.country if location else None,
    }

def get_or_create_location(session, city, state, country):
    logger.debug(f"get_or_create_location called with: city={city}, state={state}, country={country}")
    try:
        if not (city or state or country):
            logger.debug("No city/state/country provided, returning None.")
            return None

        location = session.query(Location).filter_by(city=city, state=state, country=country).first()
        if location:
            logger.debug(f"Existing location found: {location}")
        else:
            location = Location(city=city, state=state, country=country)
            session.add(location)
            logger.debug("New location instance created, committing to DB...")
            commit_session(session)
            logger.debug(f"Location committed with id: {location.id}")

        return location
    except Exception as e:
        logger.error(f"Error in get_or_create_location: {e}")
        return None
    
def get_or_create_tag(session, tag_name):
    """
    Retrieve or create a tag entry in the database.
    """
    try:
        tag = session.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            session.add(tag)
            commit_session(session)
        return tag
    except Exception as e:
        logger.error(f"Error fetching or creating tag: {e}")
        return None
    
def get_or_create_organization(session: Session, org_name: str):
    """
    Retrieve or create an organization entry in the database.
    """
    try:
        org = session.query(Organization).filter_by(name=org_name).first()
        if not org:
            org = Organization(name=org_name)
            session.add(org)
            commit_session(session)
        return org
    except Exception as e:
        logger.error(f"Error fetching or creating organization: {e}")
        return None

def fetch_markers(session: Session):
    """
    Fetch all approved markers from the database.
    """
    try:
        markers = session.query(Marker).filter(Marker.status == "approved").all()
        return [
            {
                "id": marker.id,
                "title": marker.title,
                "description": marker.description,
                "latitude": marker.latitude,
                "longitude": marker.longitude,
                "category": marker.category.name if marker.category else None,
                "location": serialize_location(marker.location),
                "tags": [tag.name for tag in marker.tags],
            }
            for marker in markers
        ]
    except Exception as e:
        logger.error(f"Error fetching markers: {e}")
        return []

def fetch_pending_markers(session: Session):
    """
    Fetch all pending markers from the database.
    """
    try:
        markers = session.query(Marker).filter(Marker.status == "pending").all()
        return [
            {
                "id": marker.id,
                "title": marker.title,
                "description": marker.description,
                "latitude": marker.latitude,
                "longitude": marker.longitude,
                "category": marker.category.name if marker.category else None,
                "tags": [tag.name for tag in marker.tags],
                "submitted_by": marker.submitted_by,
                "status": marker.status,
            }
            for marker in markers
        ]
    except Exception as e:
        logger.error(f"Error fetching pending markers: {e}")
        return []


def fetch_approved_items(session: Session, model, filter_conditions=None):
    """
    Fetch approved items from the database for a given model.
    
    Args:
        session: SQLAlchemy session.
        model: SQLAlchemy model to query.
        filter_conditions: Optional conditions to apply.

    Returns:
        List of serialized items.
    """
    query = session.query(model)
    if filter_conditions:
        query = query.filter_by(**filter_conditions)
    
    return query.all()

def get_marker_audit_log(session: Session, marker_id: int):
    """
    Retrieve the audit log for a marker.
    """
    audit_logs = session.query(MarkerAuditLog).filter_by(marker_id=marker_id).all()
    return [
        {
            "action": log.action,
            "timestamp": log.timestamp,
            "user_id": log.user_id,
        }
        for log in audit_logs
    ]


def log_audit_action(session: Session, action: str, marker_id: int):
    """
    Log an audit action for a marker.
    """
    try:
        audit_log = MarkerAuditLog(
            action=action,
            timestamp=datetime.utcnow(),
            user_id=current_user.id,
            marker_id=marker_id
        )
        session.add(audit_log)
        commit_session(session)
    except Exception as e:
        logger.error(f"Error logging audit action: {e}")

def edit_marker(session: Session, marker_id: int, updated_data: dict):
    """
    Edit a marker's details.
    """
    marker = session.query(Marker).filter_by(id=marker_id).first()
    if marker:
        for key, value in updated_data.items():
            if hasattr(marker, key):
                setattr(marker, key, value)

        commit_session(session)

        # Log the audit action
        log_audit_action(session, f"Marker '{marker.title}' edited by {current_user.id}", marker.id)

        return {"success": True, "message": "Marker updated successfully"}
    return {"success": False, "message": "Marker not found"}

def approve_or_reject_marker(session, marker_id, action):
    """
    Approve or reject a marker.
    """
    marker = session.query(Marker).filter_by(id=marker_id).first()
    if marker:
        marker.status = action  # Expected values: 'approved', 'rejected'
        commit_session(session)
        return True
    return False

def create_item(session, model, data):
    """
    Create a new database entry.
    """
    try:
        item = model(**data)
        session.add(item)
        session.commit()
        return item
    except Exception as e:
        session.rollback()
        raise e
    
def soft_delete_marker(session: Session, marker_id: int):
    # Check if the marker exists
    marker = session.query(Marker).filter_by(id=marker_id).first()
    if not marker:
        raise ValueError("Marker not found")

    # Check if already soft deleted
    if marker.deleted_marker:
        raise ValueError("Marker is already deleted")

    # Create a DeletedMarker entry
    deleted_marker = DeletedMarker(id=marker_id)
    session.add(deleted_marker)
    session.commit()

def restore_marker(session: Session, marker_id: int):
    # Check if the marker exists
    deleted_marker = session.query(DeletedMarker).filter_by(id=marker_id).first()
    if not deleted_marker:
        raise ValueError("Deleted marker not found")

    # Remove the DeletedMarker entry to restore the marker
    session.delete(deleted_marker)
    session.commit()

def get_active_markers(session: Session):
    deleted_marker_alias = aliased(DeletedMarker)
    return session.query(Marker).outerjoin(deleted_marker_alias).filter(deleted_marker_alias.id == None).all()

def fetch_all_users(session):
    """
    Fetch all users from the database.
    """
    return session.query(User).all()


def update_user_role(session, user_id, new_role):
    """
    Update the role of a user.
    """
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        user.role = new_role
        commit_session(session)
        return True
    return False