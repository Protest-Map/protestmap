from flask import Blueprint, jsonify, render_template, request
from sqlalchemy.exc import SQLAlchemyError
from app.utils.db_utils import SessionLocal
from app.utils.marker_utils import (
    submit_marker, fetch_markers, fetch_pending_markers, serialize_location,
    get_or_create_location, get_or_create_tag, get_or_create_organization,
    fetch_approved_items, create_item, fetch_all_users, update_user_role,
    approve_or_reject_marker, log_audit_action, get_marker_audit_log, edit_marker
)
from app.models import Category, Tag, Organization, Location, Marker, MarkerTranslation, RecurrenceRule
import logging

# Import the auth blueprint
from app.auth import auth_bp  # This will import the auth blueprint

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR, filename="errors.log")

# Define Blueprint for other routes
routes_bp = Blueprint("routes", __name__)

# Home Route
@routes_bp.route("/")
def home():
    session = SessionLocal()
    try:
        categories = session.query(Category).order_by(Category.id).all()
        tags = session.query(Tag).all()

        serialized_categories = [{"id": cat.id, "name": cat.name} for cat in categories]
        serialized_tags = [{"id": tag.id, "name": tag.name} for tag in tags]

        return render_template("map.html", categories=serialized_categories, tags=serialized_tags)
    except Exception as e:
        logger.error(f"Error loading homepage: {e}")
        return render_template("error.html", message="An error occurred while loading the homepage.")
    finally:
        session.close()

# API: Submit Marker
@routes_bp.route("/api/markers", methods=["POST"])
def submit_marker_api():
    session = SessionLocal()
    try:
        data = request.json
        print("DEBUG: Data received at /api/markers:", data)  # Debug print
        result = submit_marker(data, session)
        print("DEBUG: Result returned from submit_marker:", result)  # Debug print
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error in /api/markers: {e}")
        print("DEBUG: Exception in /api/markers route:", e)
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# API: Get Markers
@routes_bp.route("/api/markers", methods=["GET"])
def get_markers():
    session = SessionLocal()
    try:
        markers = fetch_markers(session)
        return jsonify({"success": True, "markers": markers})
    except Exception as e:
        logger.error(f"Error in GET /api/markers: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# API: Approve or Reject Marker
@routes_bp.route("/api/markers/<int:marker_id>/status", methods=["POST"])
def approve_or_reject_marker_api(marker_id):
    session = SessionLocal()
    try:
        data = request.json
        action = data.get("action")  # "approve" or "reject"
        user_id = data.get("user_id")

        if action not in ["approve", "reject"]:
            return jsonify({"success": False, "message": "Invalid action"}), 400

        result = approve_or_reject_marker(marker_id, action, user_id, session)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error in /api/markers/<marker_id>/status: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# API: Manage Translations
@routes_bp.route("/api/markers/<int:marker_id>/translations", methods=["POST"])
def add_translation(marker_id):
    session = SessionLocal()
    try:
        data = request.json
        language = data.get("language")
        title = data.get("title")
        description = data.get("description")

        if not (language and title and description):
            return jsonify({"success": False, "message": "All fields are required."}), 400

        translation = MarkerTranslation(
            marker_id=marker_id, language=language, title=title, description=description
        )
        session.add(translation)
        session.commit()

        return jsonify({"success": True, "message": "Translation added successfully."}), 201
    except Exception as e:
        logger.error(f"Error adding translation: {e}")
        session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# API: Get Audit Logs
@routes_bp.route("/api/markers/<int:marker_id>/audit_logs", methods=["GET"])
def get_marker_audit_logs(marker_id):
    session = SessionLocal()
    try:
        logs = get_marker_audit_log(marker_id, session)
        return jsonify({"success": True, "logs": logs}), 200
    except Exception as e:
        logger.error(f"Error fetching audit logs: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# API: Get Pending Markers
@routes_bp.route("/api/pending_markers", methods=["GET"])
def get_pending_markers():
    session = SessionLocal()
    try:
        pending_markers = fetch_pending_markers(session)
        return jsonify({"success": True, "markers": pending_markers})
    except Exception as e:
        logger.error(f"Error in GET /api/pending_markers: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# API: Add Category
@routes_bp.route("/api/categories", methods=["POST"])
def add_category():
    session = SessionLocal()
    try:
        data = request.json
        category_name = data.get("name")

        if not category_name:
            return jsonify({"success": False, "message": "Category name is required"}), 400

        new_category = Category(name=category_name)
        session.add(new_category)
        session.commit()

        return jsonify({
            "success": True,
            "category": {"id": new_category.id, "name": new_category.name}
        }), 201
    except Exception as e:
        logger.error(f"Error in POST /api/categories: {e}")
        session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# API: Get Categories
@routes_bp.route("/api/categories", methods=["GET"])
def get_categories():
    session = SessionLocal()
    try:
        categories = session.query(Category).order_by(Category.name).all()
        return jsonify({
            "success": True,
            "categories": [{"id": cat.id, "name": cat.name} for cat in categories]
        })
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return jsonify({"success": False, "message": "Error fetching categories"}), 500
    finally:
        session.close()

# API: Add Tag
@routes_bp.route("/api/tags", methods=["POST"])
def add_tag():
    session = SessionLocal()
    try:
        data = request.json
        tag_name = data.get("name")

        if not tag_name:
            return jsonify({"success": False, "message": "Tag name is required"}), 400

        new_tag = Tag(name=tag_name)
        session.add(new_tag)
        session.commit()

        return jsonify({
            "success": True,
            "tag": {"id": new_tag.id, "name": new_tag.name}
        }), 201
    except Exception as e:
        logger.error(f"Error in POST /api/tags: {e}")
        session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# API: Get Tags
@routes_bp.route("/api/tags", methods=["GET"])
def get_tags():
    session = SessionLocal()
    try:
        tags = session.query(Tag).all()
        return jsonify({"success": True, "tags": [{"id": tag.id, "name": tag.name} for tag in tags]})
    except Exception as e:
        logger.error(f"Error in /api/tags: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# API: Add Organization
@routes_bp.route("/api/organizations", methods=["POST"])
def add_organization():
    session = SessionLocal()
    try:
        data = request.json
        organization_name = data.get("name")

        if not organization_name:
            return jsonify({"success": False, "message": "Organization name is required"}), 400

        new_organization = Organization(name=organization_name)
        session.add(new_organization)
        session.commit()

        return jsonify({
            "success": True,
            "organization": {"id": new_organization.id, "name": new_organization.name}
        }), 201
    except Exception as e:
        logger.error(f"Error in POST /api/organizations: {e}")
        session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# API: Get Organizations
@routes_bp.route("/api/organizations", methods=["GET"])
def get_organizations():
    session = SessionLocal()
    try:
        organizations = session.query(Organization).all()
        return jsonify({
            "success": True,
            "organizations": [{"id": org.id, "name": org.name} for org in organizations]
        })
    except Exception as e:
        logger.error(f"Error fetching organizations: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# API: Search Markers
@routes_bp.route("/api/search", methods=["GET"])
def search_markers():
    session = SessionLocal()
    try:
        markers = fetch_markers(session)
        return jsonify({"success": True, "markers": markers})
    except SQLAlchemyError as e:
        logger.error(f"Database error in /api/search: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    finally:
        session.close()

# ---------------------------------------
# NEW LOCATION ENDPOINTS UNDER /api/location/
# ---------------------------------------

# GET Distinct Cities
@routes_bp.route("/api/location/cities", methods=["GET"])
def get_cities():
    session = SessionLocal()
    try:
        cities = session.query(Location.city).distinct().filter(Location.city.isnot(None)).all()
        city_list = [c[0] for c in cities if c[0]]
        return jsonify({"success": True, "cities": [{"name": city} for city in city_list]})
    except Exception as e:
        logger.error(f"Error fetching cities: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# POST a new location with a given city
@routes_bp.route("/api/location/cities", methods=["POST"])
def add_city():
    session = SessionLocal()
    try:
        data = request.json
        city_name = data.get("city")
        state_name = data.get("state", "")
        country_name = data.get("country", "")

        if not city_name:
            return jsonify({"success": False, "message": "City name is required"}), 400

        existing = session.query(Location).filter(
            Location.city == city_name,
            Location.state == state_name,
            Location.country == country_name
        ).first()
        if existing:
            return jsonify({"success": False, "message": "This city/state/country combination already exists."}), 400

        new_location = Location(city=city_name, state=state_name, country=country_name)
        session.add(new_location)
        session.commit()

        return jsonify({
            "success": True,
            "location": {
                "id": new_location.id,
                "city": new_location.city,
                "state": new_location.state,
                "country": new_location.country
            }
        }), 201
    except Exception as e:
        logger.error(f"Error in POST /api/location/cities: {e}")
        session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()


# GET Distinct States
@routes_bp.route("/api/location/states", methods=["GET"])
def get_states():
    session = SessionLocal()
    try:
        states = session.query(Location.state).distinct().filter(Location.state.isnot(None)).all()
        state_list = [s[0] for s in states if s[0]]
        return jsonify({"success": True, "states": [{"name": state} for state in state_list]})
    except Exception as e:
        logger.error(f"Error fetching states: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# POST a new location with a given state
@routes_bp.route("/api/location/states", methods=["POST"])
def add_state():
    session = SessionLocal()
    try:
        data = request.json
        state_name = data.get("state")
        city_name = data.get("city", "")
        country_name = data.get("country", "")

        if not state_name:
            return jsonify({"success": False, "message": "State name is required"}), 400

        existing = session.query(Location).filter(
            Location.city == city_name,
            Location.state == state_name,
            Location.country == country_name
        ).first()
        if existing:
            return jsonify({"success": False, "message": "This city/state/country combination already exists."}), 400

        new_location = Location(city=city_name, state=state_name, country=country_name)
        session.add(new_location)
        session.commit()

        return jsonify({
            "success": True,
            "location": {
                "id": new_location.id,
                "city": new_location.city,
                "state": new_location.state,
                "country": new_location.country
            }
        }), 201
    except Exception as e:
        logger.error(f"Error in POST /api/location/states: {e}")
        session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()


# GET Distinct Countries
@routes_bp.route("/api/location/countries", methods=["GET"])
def get_countries():
    session = SessionLocal()
    try:
        countries = session.query(Location.country).distinct().filter(Location.country.isnot(None)).all()
        country_list = [co[0] for co in countries if co[0]]
        return jsonify({"success": True, "countries": [{"name": c} for c in country_list]})
    except Exception as e:
        logger.error(f"Error fetching countries: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()

# POST a new location with a given country
@routes_bp.route("/api/location/countries", methods=["POST"])
def add_country():
    session = SessionLocal()
    try:
        data = request.json
        country_name = data.get("country")
        city_name = data.get("city", "")
        state_name = data.get("state", "")

        if not country_name:
            return jsonify({"success": False, "message": "Country name is required"}), 400

        existing = session.query(Location).filter(
            Location.city == city_name,
            Location.state == state_name,
            Location.country == country_name
        ).first()
        if existing:
            return jsonify({"success": False, "message": "This city/state/country combination already exists."}), 400

        new_location = Location(city=city_name, state=state_name, country=country_name)
        session.add(new_location)
        session.commit()

        return jsonify({
            "success": True,
            "location": {
                "id": new_location.id,
                "city": new_location.city,
                "state": new_location.state,
                "country": new_location.country
            }
        }), 201
    except Exception as e:
        logger.error(f"Error in POST /api/location/countries: {e}")
        session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500
    finally:
        session.close()
