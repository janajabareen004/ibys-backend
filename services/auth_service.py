from services.supabase_client import supabase, get_auth_client
from services.errors import ServiceError
from models.user import User


class AuthService:
    """Authentication and profile logic.

    Preserves the Phase 3 client isolation: user-auth calls (sign_up, sign_in,
    get_user) run on isolated clients, while privileged table/admin operations
    run on the shared admin/data client bound to the sb_secret_ key.
    """

    def _rollback_auth_user(self, user_id):
        """Delete an orphaned Auth user via the privileged admin client.

        Returns True on success, False otherwise. Diagnostics are printed to the
        server log; secrets/tokens are never printed.
        """
        try:
            supabase.auth.admin.delete_user(user_id)
            return True
        except Exception as cleanup_error:
            print(f"[register] Auth user cleanup failed: {cleanup_error}")
            return False

    def get_current_user(self, token):
        """Validate an access token on an isolated client. Returns the auth user or None."""
        try:
            result = get_auth_client().auth.get_user(token)
        except Exception:
            return None
        if not result or not getattr(result, "user", None):
            return None
        return result.user

    def get_role(self, user_id):
        """Return the user's role from public.users, or None if no profile row.

        Reuses the shared privileged (sb_secret_) client, mirroring the role
        lookup already used by login() and get_me(). Does not touch auth state.
        """
        try:
            user_row = (
                supabase.table("users")
                .select("role")
                .eq("user_id", user_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not user_row.data:
            return None
        return user_row.data[0].get("role")

    def register(self, data):
        if not isinstance(data, dict) or not data:
            raise ServiceError("Request body must be a non-empty JSON object.", 400)

        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        if not email or not password or not role:
            raise ServiceError("Missing required field(s): email, password, role.", 400)

        if not User.is_valid_role(role):
            raise ServiceError(
                f"Invalid role. Must be one of: {', '.join(User.VALID_ROLES)}.", 400
            )

        config = User.role_config(role)
        name_field = config["name_field"]
        name_value = data.get(name_field)
        if not name_value:
            raise ServiceError(f"Missing required field: {name_field}.", 400)

        # 1) Create the Supabase Auth user on an ISOLATED client so its session
        # is never attached to the privileged admin/data client.
        try:
            auth_response = get_auth_client().auth.sign_up(
                {"email": email, "password": password}
            )
        except Exception as e:
            raise ServiceError(str(e), 400)

        if not auth_response or not getattr(auth_response, "user", None):
            raise ServiceError("Registration failed. Email may already be in use.", 409)

        user_id = auth_response.user.id

        # 2) Insert the public.users row using the privileged admin/data client.
        try:
            supabase.table("users").insert({"user_id": user_id, "role": role}).execute()
        except Exception as e:
            print(f"[register] public.users insert failed: {e}")
            if not self._rollback_auth_user(user_id):
                raise ServiceError(
                    "Profile creation failed and Auth user cleanup failed. "
                    "An Auth user may remain and require manual removal.",
                    500,
                )
            raise ServiceError(f"Profile creation failed: {str(e)}", 400)

        # 3) Insert the role-specific row. On failure, delete the public.users
        # row first, then the Auth user.
        role_row = {"user_id": user_id, name_field: name_value}
        phone = data.get("phone")
        if phone:
            role_row["phone"] = phone

        try:
            role_result = supabase.table(config["table"]).insert(role_row).execute()
        except Exception as e:
            print(f"[register] {config['table']} insert failed: {e}")
            try:
                supabase.table("users").delete().eq("user_id", user_id).execute()
            except Exception as users_cleanup_error:
                print(f"[register] public.users cleanup failed: {users_cleanup_error}")
            if not self._rollback_auth_user(user_id):
                raise ServiceError(
                    "Profile creation failed and Auth user cleanup failed. "
                    "An Auth user may remain and require manual removal.",
                    500,
                )
            raise ServiceError(f"Profile creation failed: {str(e)}", 400)

        profile = {"user_id": user_id, "role": role}
        if role_result.data:
            profile.update(role_result.data[0])
        return profile

    def login(self, data):
        if not isinstance(data, dict) or not data:
            raise ServiceError("Request body must be a non-empty JSON object.", 400)

        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            raise ServiceError("Missing required field(s): email, password.", 400)

        try:
            auth_response = get_auth_client().auth.sign_in_with_password(
                {"email": email, "password": password}
            )
        except Exception:
            raise ServiceError("Invalid email or password.", 401)

        if not auth_response or not auth_response.session or not auth_response.user:
            raise ServiceError("Invalid email or password.", 401)

        user_id = auth_response.user.id

        try:
            user_row = (
                supabase.table("users").select("*").eq("user_id", user_id).execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)

        role = user_row.data[0]["role"] if user_row.data else None

        return {
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "user_id": user_id,
            "role": role,
        }

    def logout(self, token):
        # Revoke the session on an isolated client so the shared admin/data
        # client is never mutated. Best-effort: the frontend must also discard
        # its tokens.
        try:
            get_auth_client().auth.admin.sign_out(token)
        except Exception as e:
            print(f"[logout] sign_out failed: {e}")
        return {"message": "Logged out successfully."}

    def get_me(self, token):
        user = self.get_current_user(token)
        if not user:
            raise ServiceError("Invalid or expired token.", 401)

        user_id = user.id

        try:
            user_row = (
                supabase.table("users").select("*").eq("user_id", user_id).execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)

        if not user_row.data:
            raise ServiceError("User profile not found.", 404)

        profile = user_row.data[0]
        role = profile.get("role")

        role_profile = None
        config = User.role_config(role)
        if config:
            try:
                role_row = (
                    supabase.table(config["table"])
                    .select("*")
                    .eq("user_id", user_id)
                    .execute()
                )
            except Exception as e:
                raise ServiceError(str(e), 500)
            if role_row.data:
                role_profile = role_row.data[0]

        return {
            "user": profile,
            "role": role,
            "profile": role_profile,
        }
