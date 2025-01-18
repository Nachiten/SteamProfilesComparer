import requests
import json

# Replace this with your Steam Web API key
STEAM_API_KEY = "<steam_api_key>"

# Base URL for the Steam Web API
STEAM_API_BASE_URL = "https://api.steampowered.com"

def get_steam_user_info(steam_id):
    """Retrieve public profile information for a Steam user."""
    url = f"{STEAM_API_BASE_URL}/ISteamUser/GetPlayerSummaries/v2/"
    params = {
        "key": STEAM_API_KEY,
        "steamids": steam_id,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "response" in data and "players" in data["response"] and len(data["response"]["players"]) > 0:
            return data["response"]["players"][0]
        else:
            return "No public profile found for the provided Steam ID."
    else:
        return f"Error: {response.status_code} - {response.text}"

def get_steam_user_games(steam_id):
    """Retrieve a list of all games owned by a Steam user, ordered by hours played."""
    url = f"{STEAM_API_BASE_URL}/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "response" in data and "games" in data["response"]:
            games = data["response"]["games"]
            # Sort games by playtime_forever (hours played)
            sorted_games = sorted(games, key=lambda x: x["playtime_forever"], reverse=True)
            for game in sorted_games:
                game["playtime_hours"] = game["playtime_forever"] // 60
            return sorted_games
        else:
            return "No games found for the provided Steam ID or the profile is private."
    else:
        return f"Error: {response.status_code} - {response.text}"

def request_steam_user_games():
    while True:
        steam_id = input("Enter the Steam ID or Steam64 ID of the user: ('stop' to end) ").strip()

        # If, steam_id is "stop", then return None
        if steam_id.lower() == "stop":
            return None

        try:
            # Fetch and display user's games
            print("\nFetching owned games...")
            games = get_steam_user_games(steam_id)

            if isinstance(games, list):
                # Print the username found
                user_info = get_steam_user_info(steam_id)

                username = user_info['personaname']

                print(f"Found user {username}");

                return username, games
            else:
                print(f"Could not find this user.")

        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    print("Steam games comparer")

    users = []
    usersGames = []

    while True:
        userAndGame = request_steam_user_games()

        if userAndGame is None:
            break

        users.append(userAndGame[0])
        usersGames.append(userAndGame[1])

    # Create a new list, which contains all games, filtering by 'appid', where they are the present in all the lists inside usersGames
    common_game_ids = set(game['appid'] for game in usersGames[0])
    for userGames in usersGames[1:]:
        common_game_ids.intersection_update(game['appid'] for game in userGames)

    # Create a list of common games using the intersected `appid`s
    common_games = [game for game in usersGames[0] if game['appid'] in common_game_ids]

    # Print the common games
    print("\nCommon Games between users: " + ", ".join(users))
    print()
    for game in common_games:
        print(f"{game['name']} - {game['playtime_hours']} hours")


if __name__ == "__main__":
    main()
