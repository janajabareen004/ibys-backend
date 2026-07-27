from supabase import create_client, Client, ClientOptions
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Options that stop any auth call from persisting or auto-refreshing a session
# on the privileged client. This guarantees database and admin operations always
# run with the sb_secret_ key authorization and are never downgraded to a user JWT.
_no_session_options = ClientOptions(
    auto_refresh_token=False,
    persist_session=False,
)

# Privileged admin/data client (sb_secret_ key).
# Use ONLY for database table operations and auth.admin.* calls.
# Never call sign_up / sign_in / set_session on this client.
supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options=_no_session_options)


def get_auth_client() -> Client:
    """Return a fresh, isolated Supabase client for user-auth operations
    (sign_up, sign_in, get_user).

    A brand-new instance is returned on every call so that a user's session is
    never attached to the shared admin/data client, keeping privileged
    operations bound to the sb_secret_ key.
    """
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )
