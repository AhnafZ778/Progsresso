"""
Authentication service for Progspresso - Supabase Auth wrapper
"""

from database.supabase_db import get_supabase
from flask import session


class AuthService:
    @staticmethod
    def sign_up(email: str, password: str):
        """Register a new user and auto-login"""
        supabase = get_supabase()
        try:
            # Sign up the user
            response = supabase.auth.sign_up({"email": email, "password": password})

            if response.user:
                # If we got a session, user is auto-confirmed (email confirmation disabled)
                if response.session:
                    session["user_id"] = response.user.id
                    session["user_email"] = response.user.email
                    session["access_token"] = response.session.access_token
                    session["refresh_token"] = response.session.refresh_token
                    session.permanent = True  # Stay logged in by default
                    return {
                        "success": True,
                        "user": response.user,
                        "session": response.session,
                        "auto_login": True,
                    }
                else:
                    # Email confirmation is enabled in Supabase - try to sign in anyway
                    # This will work if user confirms later, or fail gracefully
                    return {
                        "success": True,
                        "user": response.user,
                        "session": None,
                        "auto_login": False,
                        "message": "Account created! You can now log in.",
                    }
            return {"success": False, "error": "Registration failed"}
        except Exception as e:
            error_msg = str(e)
            if "User already registered" in error_msg:
                return {
                    "success": False,
                    "error": "An account with this email already exists",
                }
            return {"success": False, "error": error_msg}

    @staticmethod
    def sign_in(email: str, password: str, remember_me: bool = False):
        """Sign in an existing user"""
        supabase = get_supabase()
        try:
            response = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if response.user and response.session:
                # Store session info
                session["user_id"] = response.user.id
                session["user_email"] = response.user.email
                session["access_token"] = response.session.access_token
                session["refresh_token"] = response.session.refresh_token

                # Set session permanence based on "Stay logged in"
                session.permanent = remember_me

                return {"success": True, "user": response.user}
            return {"success": False, "error": "Invalid credentials"}
        except Exception as e:
            error_msg = str(e)
            if "Invalid login credentials" in error_msg:
                return {"success": False, "error": "Invalid email or password"}
            return {"success": False, "error": error_msg}

    @staticmethod
    def sign_out():
        """Sign out the current user"""
        try:
            supabase = get_supabase()
            supabase.auth.sign_out()
        except Exception:
            pass
        # Clear Flask session
        session.clear()
        return {"success": True}

    @staticmethod
    def get_current_user():
        """Get the current logged-in user from session"""
        if "user_id" in session:
            return {"id": session.get("user_id"), "email": session.get("user_email")}
        return None

    @staticmethod
    def is_authenticated():
        """Check if user is authenticated"""
        return "user_id" in session and session.get("access_token")

    @staticmethod
    def refresh_session():
        """Refresh the session token if needed"""
        refresh_token = session.get("refresh_token")
        if not refresh_token:
            return False

        try:
            supabase = get_supabase()
            response = supabase.auth.refresh_session(refresh_token)
            if response.session:
                session["access_token"] = response.session.access_token
                session["refresh_token"] = response.session.refresh_token
                return True
        except Exception:
            pass
        return False
