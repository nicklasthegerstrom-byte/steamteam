from services.auth_service import (
    login,
    signup,
    update_steam_id,
    update_username,
    update_email,
    get_user_by_id
)
from services.profile_sync import sync_user_profile
from services.matching_service import match_user_id

# =========================
# User class
# =========================
class User:
    def __init__(self, user_id: int, username: str, email: str, steam_id: str | None = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.steam_id = steam_id

    def set_steam_id(self, steam_id: str):
        update_steam_id(self.user_id, steam_id)
        # Refresh after update
        self.refresh()

    def set_username(self, username: str):
        update_username(self.user_id, username)
        self.refresh()

    def set_email(self, email: str):
        update_email(self.user_id, email)
        self.refresh()

    def refresh(self):
        """Fetch latest user info from backend and update object."""
        data = get_user_by_id(self.user_id)
        self.username = data.get("username", self.username)
        self.email = data.get("email", self.email)
        self.steam_id = data.get("steam_id", self.steam_id)

    def print_details(self):
        self.refresh()
        print(f"user_id: {self.user_id}")
        print(f"username: {self.username}")
        print(f"email: {self.email}")
        print(f"steam_id: {self.steam_id}")

# =========================
# Main window
# =========================
def main_window() -> User:
    print("=================================")
    print(" SteamTeam - Temporary CLI ")
    print("=================================")
    print("1. Login")
    print("2. Signup")
    print("0. Exit")

    choice = input("Select option: ").strip()

    if choice == "1":
        return login_window()
    elif choice == "2":
        return signup_window()
    elif choice == "0":
        print("[i] Exiting...")
        raise SystemExit
    else:
        print("[-] Invalid choice")
        return main_window()

# =========================
# Signup window
# =========================
def signup_window() -> User:
    print("\n----- Signup -----")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    steam_id = input("Enter SteamID / vanity / profile URL: ").strip()
    
    user_id = signup(username=username, email=email, steam_id=steam_id)
    if not user_id:
        print("[-] Signup failed")
        return main_window()

    print("[+] Account created")
    user = User(user_id=user_id, username=username, email=email, steam_id=steam_id)
    user.refresh()
    return user

# =========================
# Login window
# =========================
def login_window() -> User:
    print("\n----- Login -----")
    username = input("Username: ").strip()
    email = input("Email: ").strip()

    user_data = login(username, email)
    if not user_data:
        print("[-] Wrong username or email")
        return main_window()

    print("[+] Login successful")
    user = User(
        user_id=user_data["user_id"],
        username=user_data["username"],
        email=user_data["email"],
        steam_id=user_data["steam_id"]
    )
    user.refresh()
    return user

# =========================
# Profile view
# =========================
def profile_view(user: User) -> None:
    print("\n----- Profile -----")
    user.print_details()
    print("")
    print("1. Sync profile")
    print("2. Continue to matching")
    print("3. Update SteamID")
    print("4. Update username")
    print("5. Update email")
    print("0. Logout")

    choice = input("Select option: ").strip()

    if choice == "1":
        # Sync profile from backend
        print("[i] Syncing profile...")
        sync_user_profile(user_id=user.user_id)
        user.refresh()
        print("[+] Profile synced")
        return profile_view(user)

    elif choice == "2":
        # Continue to matching view
        return match_view(user)

    elif choice == "3":
        # Update SteamID
        steam_input = input("Enter SteamID / vanity / profile URL: ").strip()
        try:
            user.set_steam_id(steam_input)
            print("[+] SteamID updated")
        except ValueError as e:
            print(f"[-] {e}")
        return profile_view(user)

    elif choice == "4":
        # Update username
        new_username = input("Enter new username: ").strip()
        user.set_username(new_username)
        print("[+] Username updated")
        return profile_view(user)

    elif choice == "5":
        # Update email
        new_email = input("Enter new email: ").strip()
        user.set_email(new_email)
        print("[+] Email updated")
        return profile_view(user)

    elif choice == "0":
        # Logout
        print("[i] Logging out...")
        run()

    else:
        print("[-] Invalid choice")
        return profile_view(user)


# =========================
# Match view
# =========================
def match_view(user: User) -> None:
    print("\n----- Match View -----")
    print("1. Find matches")
    print("2. Back to profile")
    print("0. Logout")

    choice = input("Select option: ").strip()

    if choice == "1":
        print("[i] Finding matches...")
        matches = match_user_id(user.user_id)
        print("[+] Done\n")

        print("Best matches:")
        for i, match in enumerate(matches):
            print(
                f"{i+1:>3}. "
                f"Score: {match['score']:<7.2%} | "
                f"ID: {match['user_id']:<6} | "
                f"Username: {match['username']:<20} | "
                f"Steam: {match['steam_id']}"
            )

        return match_view(user)

    elif choice == "2":
        return profile_view(user)

    elif choice == "0":
        print("[i] Logging out...")
        run()

    else:
        print("[-] Invalid choice")
        return match_view(user)

# =========================
# App entrypoint
# =========================
def run() -> None:
    user = main_window()
    profile_view(user)

if __name__ == "__main__":
    run()
