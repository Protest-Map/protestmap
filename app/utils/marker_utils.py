from sqlalchemy.orm import Session
from app.models import Marker, Location, Category, Tag, Organization
from app.utils.db_utils import commit_session
from app.utils.utils import (
    fetch_markers, fetch_pending_markers, serialize_location, get_or_create_location,
    get_or_create_tag, get_or_create_organization, fetch_approved_items, create_item,
    fetch_all_users, update_user_role, approve_or_reject_marker, log_audit_action,
    get_marker_audit_log, edit_marker
)
from datetime import datetime
from flask_login import current_user
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def submit_marker(data, session: Session):
    try:
        print("DEBUG: submit_marker received data:", data)  # Debug print

        # Retrieve the necessary fields from the input data
        title = data.get("title")
        description = data.get("description")
        category_id = int(data.get("category_id")) if data.get("category_id") else None
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        # Print the required fields to ensure they're not None or empty
        print("DEBUG: Required fields:",
              f"title={title}, description={description}, category_id={category_id}, lat={latitude}, lng={longitude}")

        city = data.get("city")
        state = data.get("state")
        country = data.get("country")

        print("DEBUG: Location fields:", city, state, country)

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        print("DEBUG: Dates:", start_date, end_date)

        is_recurrent = data.get("is_recurrent", False)  # Default to False if not provided
        recurrence_frequency = data.get("recurrence_frequency")
        recurrence_end_date = data.get("recurrence_end_date")
        timezone = data.get("timezone")
        language = data.get("language", "en")  # Default to 'en' if not provided
        organizations = data.get("organizations", [])  # New field for organization names

        # Ensure all required fields are present
        if not all([title, description, category_id, latitude, longitude]):
            print("DEBUG: Missing required fields")  # Debug print
            return {"success": False, "message": "Missing required fields"}

        # Get or create the location
        location = get_or_create_location(session, city, state, country)
        print("DEBUG: location returned:", location)

        if not location:
            return {"success": False, "message": "Error creating or retrieving location"}

        # Determine submitted_by
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            submitted_by = current_user.id
            print("DEBUG: Submitted by user_id:", submitted_by)
        else:
            submitted_by = None
            print("DEBUG: Submitted anonymously")

        # Create the Marker instance
        marker = Marker(
            title=title,
            description=description,
            category_id=category_id,
            latitude=float(latitude),
            longitude=float(longitude),
            status="pending",  # Default status is 'pending'
            location_id=location.id,  # Linking the marker to the location
            event_date=start_date and datetime.fromisoformat(start_date),  # Ensure correct format
            event_end_date=end_date and datetime.fromisoformat(end_date),
            is_recurrent=is_recurrent,
            recurrence_frequency=recurrence_frequency,
            recurrence_end_date=recurrence_end_date and datetime.fromisoformat(recurrence_end_date),
            timezone=timezone,
            language=language,
            submitted_by=submitted_by,
            previous_data={},  # Set to an empty dictionary or None if no previous data exists
        )
        print("DEBUG: Marker instance created:", marker)
        session.add(marker)

        # Handle tags
        for tag_name in data.get("tags", []):
            print(f"DEBUG: Processing tag: {tag_name}")
            tag = session.query(Tag).filter_by(name=tag_name.strip()).first()
            if not tag:
                print(f"DEBUG: Creating new tag: {tag_name.strip()}")
                tag = Tag(name=tag_name.strip())
                session.add(tag)
            marker.tags.append(tag)

        # Handle organizations
        for org_name in organizations:
            print(f"DEBUG: Processing organization: {org_name}")
            org = session.query(Organization).filter_by(name=org_name.strip()).first()
            if not org:
                print(f"DEBUG: Creating new organization: {org_name.strip()}")
                org = Organization(name=org_name.strip())
                session.add(org)
            marker.organizations.append(org)

        # Commit the session
        try:
            session.commit()
            print("DEBUG: Session committed successfully")
            return {"success": True, "message": "Marker submitted successfully"}
        except Exception as commit_error:
            print("DEBUG: Commit failed:", commit_error)
            session.rollback()
            return {"success": False, "message": "Database commit failed"}

    except Exception as e:
        session.rollback()
        logger.error(f"Error submitting marker: {e}", exc_info=True)
        print("DEBUG: Exception during marker submission:", e)
        return {"success": False, "message": "An error occurred while submitting the marker"}
