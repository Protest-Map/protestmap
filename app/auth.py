from flask import Blueprint, request, jsonify, session, redirect, url_for
from app.models import db, User, OAuthAccount, Profile
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from phonenumbers import parse, is_valid_number, NumberParseException
from datetime import datetime
from app.utils.utils import send_verification_code, verify_code  # <-- Add this import

auth_bp = Blueprint('auth', __name__)

# Flask-Dance Google OAuth Setup
google_bp = make_google_blueprint(client_id='GOOGLE_CONSUMER_KEY',
                                  client_secret='GOOGLE_CONSUMER_SECRET',
                                  redirect_to='auth.google_authorized',
                                  scope=['profile', 'email'])
auth_bp.register_blueprint(google_bp, url_prefix='/google')

# User Registration Route (Email/Password)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    phone_number = data.get('phone_number')
    country_code = data.get('country_code', None)

    if not email or not password or not name:
        return jsonify({"message": "Missing required fields"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "User with this email already exists."}), 400

    # Create new user
    user = User(email=email, name=name, role="visitor")
    user.set_phone_number(phone_number, country_code)
    user.password = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)  # Automatically log the user in
    return jsonify({"message": "Registration successful", "user": user.id}), 201

# User Login Route (Email/Password)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"message": "Login successful", "user": user.id}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# OAuth login route (e.g., Google login)
@auth_bp.route('/login/google', methods=['GET'])
def google_login():
    return google.authorize(callback=url_for('auth.google_authorized', _external=True))

@auth_bp.route('/login/google/authorized', methods=['GET'])
def google_authorized():
    if not google.authorized:
        return jsonify({'message': 'Authorization failed'}), 400

    # Get user info from Google
    google_info = google.get('/plus/v1/people/me')
    user_data = google_info.json()
    user_email = user_data.get('emails')[0]['value']

    # Check if the user exists, or create a new user
    user = User.query.filter_by(email=user_email).first()
    if not user:
        user = User(email=user_email, name=user_data.get('displayName'))
        db.session.add(user)
        db.session.commit()

    # Log the user in
    login_user(user)
    return jsonify({"message": "Login successful", "user": user.id}), 200

# Logout Route
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

# Profile Route (view profile details)
@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    user = current_user
    profile = Profile.query.filter_by(user_id=user.id).first()
    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "phone_number": user.phone_number,
        "country_code": user.country_code,
        "bio": profile.bio if profile else None,
        "profile_picture": profile.profile_picture if profile else None
    })

# Update Profile Route
@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.json
    bio = data.get('bio')
    profile_picture = data.get('profile_picture')

    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)

    if bio:
        profile.bio = bio
    if profile_picture:
        profile.profile_picture = profile_picture

    db.session.add(profile)
    db.session.commit()

    return jsonify({"message": "Profile updated successfully"}), 200

# Phone Number Validation Route
@auth_bp.route('/profile/phone', methods=['PUT'])
@login_required
def update_phone_number():
    data = request.json
    phone_number = data.get('phone_number')
    country_code = data.get('country_code')

    if not phone_number:
        return jsonify({"message": "Phone number is required"}), 400

    # Validate phone number
    try:
        parsed = parse(phone_number, country_code)
        if is_valid_number(parsed):
            current_user.set_phone_number(phone_number, country_code)
            db.session.commit()
            return jsonify({"message": "Phone number updated successfully"}), 200
        else:
            return jsonify({"message": "Invalid phone number"}), 400
    except NumberParseException as e:
        return jsonify({"message": f"Phone validation failed: {str(e)}"}), 400

# Forgot Password Route (Optional)
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"message": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Send email/SMS with reset link
    send_verification_code(user.email)  # Example function to send reset code
    return jsonify({"message": "Password reset link sent"}), 200

# Verify Phone Number Route (Optional, if needed for phone number verification)
@auth_bp.route('/verify-phone', methods=['POST'])
@login_required
def verify_phone():
    data = request.json
    code = data.get('verification_code')

    if not code:
        return jsonify({"message": "Verification code is required"}), 400

    # Assume there's a verification function that checks the code
    if verify_code(current_user.email, code):  # Now using the verify_code function
        return jsonify({"message": "Phone number verified successfully"}), 200
    else:
        return jsonify({"message": "Invalid verification code"}), 400
