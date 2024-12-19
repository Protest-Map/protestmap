from sqlalchemy import (
    Column, Integer, String, Text, Float, Date, ForeignKey, DateTime, Boolean, Table, JSON, UniqueConstraint, Enum
)
from sqlalchemy.orm import relationship, declarative_base, backref
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base, db
from flask_sqlalchemy import SQLAlchemy
from phonenumbers import parse, is_valid_number, NumberParseException
from werkzeug.security import generate_password_hash, check_password_hash


# Initialize the SQLAlchemy instance
db = SQLAlchemy()

# Association Tables with Named Constraints
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE', name='fk_role_permissions_role_id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE', name='fk_role_permissions_permission_id'), primary_key=True)
)

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE', name='fk_user_roles_user_id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE', name='fk_user_roles_role_id'), primary_key=True)
)

marker_tags = Table(
    'marker_tags',
    Base.metadata,
    Column('marker_id', Integer, ForeignKey('markers.id', ondelete='CASCADE', name='fk_marker_tags_marker_id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='SET NULL', name='fk_marker_tags_tag_id'), primary_key=True)
)

marker_organizations = Table(
    'marker_organizations',
    Base.metadata,
    Column('marker_id', Integer, ForeignKey('markers.id', ondelete='CASCADE', name='fk_marker_organizations_marker_id'), primary_key=True),
    Column('organization_id', Integer, ForeignKey('organizations.id', ondelete='CASCADE', name='fk_marker_organizations_organization_id'), primary_key=True)
)

class DeletedMarker(Base):
    __tablename__ = 'deleted_markers'
    id = Column(Integer, ForeignKey('markers.id'), primary_key=True)
    deleted_at = Column(DateTime, default=datetime.utcnow)
    marker = relationship("Marker", back_populates="deleted_marker")


# Models

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)  # Added username field
    phone_number = Column(String(20), unique=True, nullable=True)
    country_code = Column(String(5), nullable=True)  # For storing country codes
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan", uselist=True)
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="changed_by")

    def set_phone_number(self, phone, country_code=None):
        """Helper method to validate and set phone number."""
        try:
            parsed = parse(phone, country_code)
            if is_valid_number(parsed):
                self.phone_number = phone
                self.country_code = country_code
            else:
                raise ValueError("Invalid phone number.")
        except NumberParseException as e:
            raise ValueError(f"Phone validation failed: {str(e)}")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, name={self.name}, email={self.email}, role={self.role})>"


class Profile(Base):
    __tablename__ = 'profiles'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL', name='fk_profiles_user_id'), primary_key=True)
    bio = Column(Text, nullable=True)
    profile_picture = Column(Text)
    social_links = Column(JSON)

    user = relationship("User", back_populates="profiles", uselist=False, single_parent=True)

    def __repr__(self):
        return f"<Profile(user_id={self.user_id}, bio={self.bio})>"

class OAuthAccount(Base):
    """Stores information about linked OAuth accounts."""
    __tablename__ = 'oauth_accounts'

    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False)  # e.g., google, facebook
    provider_user_id = Column(String(255), nullable=False)  # Unique user ID from provider
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(JSON, nullable=False)  # OAuth token data

    user = relationship("User", back_populates="oauth_accounts")

    def __repr__(self):
        return f"<OAuthAccount(provider={self.provider}, provider_user_id={self.provider_user_id})>"

# Roles, Permissions, and Other Models...

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name})>"



class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    city = Column(String(255))
    state = Column(String(255))
    country = Column(String(255))

    __table_args__ = (UniqueConstraint('city', 'state', 'country', name='uq_locations_city_state_country'),)

    def __repr__(self):
        return f"<Location(id={self.id}, city={self.city}, state={self.state}, country={self.country})>"


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    markers = relationship("Marker", secondary=marker_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    markers = relationship("Marker", secondary=marker_organizations, back_populates="organizations")


class RecurrenceRule(Base):
    __tablename__ = 'recurrence_rules'
    id = Column(Integer, primary_key=True)
    marker_id = Column(Integer, ForeignKey('markers.id', ondelete='CASCADE'), nullable=False)
    frequency = Column(String(50))  # daily, weekly, monthly, yearly
    interval = Column(Integer, default=1)  # e.g., every 2 weeks
    days_of_week = Column(JSON)  # e.g., ["Monday", "Wednesday"]
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)


class MarkerTranslation(Base):
    __tablename__ = 'marker_translations'
    id = Column(Integer, primary_key=True)
    marker_id = Column(Integer, ForeignKey('markers.id', ondelete='CASCADE'))
    language = Column(String(10))
    title = Column(String(255))
    description = Column(Text)


class Marker(Base):
    __tablename__ = 'markers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL', name='fk_markers_category_id'), nullable=True)
    location_id = Column(Integer, ForeignKey('locations.id', ondelete='SET NULL', name='fk_markers_location_id'), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    event_date = Column(DateTime, nullable=True)
    event_end_date = Column(DateTime, nullable=True)
    is_recurrent = Column(Boolean, default=False)
    recurrence_frequency = Column(String(20), nullable=True)
    recurrence_end_date = Column(DateTime, nullable=True)
    timezone = Column(String(50), nullable=True)  # Add this
    photo_links = Column(JSON, nullable=True)
    photo_files = Column(JSON, nullable=True)
    video_links = Column(JSON, nullable=True)
    video_files = Column(JSON, nullable=True)
    status = Column(Enum("pending", "approved", "rejected", name="marker_status"), default="pending", nullable=False)
    submitted_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL', name='fk_markers_submitted_by'), nullable=True)
    edited_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL', name='fk_markers_edited_by'), nullable=True)
    approved_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL', name='fk_markers_approved_by'), nullable=True)  # New field
    approval_date = Column(DateTime, nullable=True)  # Track the approval date
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    language = Column(String(10), default='en')
    previous_data = Column(JSON, nullable=True)  # Add here for tracking changes

    tags = relationship("Tag", secondary=marker_tags, back_populates="markers", passive_deletes=True)  # Use passive_deletes=True to prevent automatic deletion of markers
    organizations = relationship("Organization", secondary=marker_organizations, back_populates="markers")
    location = relationship("Location")
    category = relationship("Category")
    comments = relationship("Comment", back_populates="marker")
    recurrence_rules = relationship("RecurrenceRule", backref="marker")
    translations = relationship("MarkerTranslation", backref="marker")
    audit_logs = relationship('MarkerAuditLog', back_populates='marker')
    deleted_marker = relationship("DeletedMarker", uselist=False, back_populates="marker")

    def __repr__(self):
        return f"<Marker(id={self.id}, title={self.title}, status={self.status})>"


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    marker_id = Column(Integer, ForeignKey('markers.id', ondelete='SET NULL', name='fk_comments_marker_id'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL', name='fk_comments_user_id'), nullable=True)
    text = Column(Text, nullable=False)
    photo_link = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())

    marker = relationship("Marker", back_populates="comments")
    user = relationship("User")

    def __repr__(self):
        return f"<Comment(id={self.id}, marker_id={self.marker_id}, text={self.text[:20]})>"


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    marker_id = Column(Integer, ForeignKey('markers.id', ondelete='CASCADE', name='fk_media_marker_id'), nullable=False)
    file_path = Column(Text, nullable=False)
    media_type = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)
    original_resolution = Column(String(50), nullable=True)
    optimized_resolution = Column(String(50), nullable=True)
    optimized_format = Column(String(50), nullable=True)
    uploaded_at = Column(DateTime, default=func.current_timestamp())
    is_optimized = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Media(id={self.id}, file_path={self.file_path})>"

class AuditLog(Base):
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True)
    table_name = Column(String(255), nullable=False)
    record_id = Column(Integer, nullable=False)
    operation = Column(String(50), nullable=False)
    changed_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL', name='fk_audit_log_changed_by_id'), nullable=True)
    change_description = Column(Text)
    previous_data = Column(JSON, nullable=True)  # Add here for tracking previous state
    changed_at = Column(DateTime, default=func.current_timestamp())

    changed_by = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, table_name={self.table_name}, operation={self.operation})>"

class MarkerAuditLog(Base):
    __tablename__ = 'marker_audit_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    marker_id = Column(Integer, ForeignKey('markers.id', ondelete='CASCADE'), nullable=False)
    action = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    additional_info = Column(JSON, nullable=True)
    
    marker = relationship('Marker', back_populates='audit_logs')
    user = relationship('User')

    def __repr__(self):
        return f"<MarkerAuditLog(id={self.id}, marker_id={self.marker_id}, action={self.action}, user_id={self.user_id}, timestamp={self.timestamp})>"

# app/models.py
__all__ = [
    "User", "Profile", "OAuthAccount", "Role", "Permission", "Marker", 
    "Comment", "Media", "AuditLog", "MarkerAuditLog", "Location", "Category", "Tag", 
    "Organization", "RecurrenceRule", "MarkerTranslation", "DeletedMarker"
]
