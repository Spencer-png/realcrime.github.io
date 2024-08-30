# app.py
from flask import Flask, redirect, request, jsonify
import os
import requests

app = Flask(__name__)

CLIENT_ID = os.getenv('1275241931412082761')
CLIENT_SECRET = os.getenv('-Zc7GqW_BWJ7D77ZPmOLc3qm1Suwqp1U')
REDIRECT_URI = 'https://discord.com/oauth2/authorize?client_id=1275241931412082761&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fcallback&scope=identify+applications.builds.read+applications.entitlements+role_connections.write'

@app.route('/auth')
def auth():
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify guilds"
    )
    return redirect(discord_auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    try:
        # Exchange code for access token
        token_response = requests.post(
            'https://discord.com/api/oauth2/token',
            data={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': REDIRECT_URI,
                'scope': 'identify guilds',
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        token_response.raise_for_status()
        access_token = token_response.json().get('access_token')

        # Fetch user data
        user_response = requests.get(
            'https://discord.com/api/users/@me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_response.raise_for_status()

        # Fetch user's guilds
        guilds_response = requests.get(
            'https://discord.com/api/users/@me/guilds',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        guilds_response.raise_for_status()

        return jsonify({
            'user': user_response.json(),
            'guilds': guilds_response.json(),
        })

    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if e.response:
            error_message = e.response.json()
        print(f"Error: {error_message}")
        return jsonify({"error": "An error occurred during authentication"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
