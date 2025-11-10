from flask import Flask, redirect, request, jsonify, session, render_template_string
from requests_oauthlib import OAuth2Session
import os
import requests
from datetime import timedelta, datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Discord OAuth2 Configuration
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', 'DISCORD_CLIENT_ID here')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', 'DISCORD_CLIENT_secret here')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'https://5ebe15ac-455f-40c9-9315-5ddeaed25f54-00-20b3tt40sqfnj.worf.replit.dev/auth/discord/callback')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', 'discord token')
DISCORD_WEBHOOKS_URL = os.getenv('DISCORD_WEBHOOKS_URI', 'https://discord.com/api/webhooks/1437381142595764367/DAi2IavggL_KLy3vwX4PnSsyoBLWHofyBHmKhPMNrmV1qZQT1yT_04Pvx1iDR0dG450t')

# Allow OAuth to work with HTTP in development (Replit uses HTTPS externally)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

DISCORD_API_BASE_URL = 'https://discord.com/api/v10'
DISCORD_AUTHORIZATION_BASE_URL = f'{DISCORD_API_BASE_URL}/oauth2/authorize'
DISCORD_TOKEN_URL = f'{DISCORD_API_BASE_URL}/oauth2/token'

OAUTH2_SCOPES = ['identify', 'guilds']

# HTML Template
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Login - Bot Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Public+Sans:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0D0B14;
            --primary-color: #C875F9;
            --secondary-color: #6A57E3;
            --text-color: #D8D3F8;
            --text-muted: #8B81B8;
            --card-bg: rgba(23, 21, 36, 0.7);
            --border-color: rgba(140, 101, 255, 0.15);
            --glow-color: rgba(200, 117, 249, 0.1);
        }

        body {
            font-family: 'Public Sans', sans-serif;
            background-color: var(--bg-color);
            background-image:
                radial-gradient(circle at 15% 20%, rgba(68, 7, 148, 0.3), transparent 40%),
                radial-gradient(circle at 85% 70%, rgba(13, 110, 253, 0.2), transparent 40%);
            background-attachment: fixed;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }

        .glass-effect {
            background: rgba(23, 23, 31, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .login-card {
            width: 100%;
            max-width: 450px;
            border-radius: 1rem;
        }
    </style>
</head>
<body>
    <div class="login-card glass-effect p-4 p-sm-5 text-center">
        <i class="bi bi-robot display-1 text-primary mb-3"></i>
        <h2 class="fw-bold text-white">Kythia Dashboard</h2>
        <p class="text-muted mb-4">
            Kelola semua fitur bot canggih Anda dengan mudah melalui panel web yang modern dan intuitif.
        </p>
        <div class="d-grid">
            <a href="/auth/discord" class="btn btn-primary btn-lg fw-semibold">
                <i class="bi bi-discord me-2"></i> Login dengan Discord
            </a>
        </div>
        <p class="small text-muted mt-4">Dengan login, Anda menyetujui Ketentuan Layanan kami.</p>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Dashboard - Kythia</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" />
    <style>
        body {
            background-color: #0D0B14;
            color: #D8D3F8;
            font-family: 'Public Sans', sans-serif;
        }
        .glass-effect {
            background: rgba(23, 23, 31, 0.6);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="glass-effect p-4">
            <h1>Welcome, {{ user.username }}#{{ user.discriminator }}!</h1>
            <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" 
                 class="rounded-circle mb-3" width="100" height="100">
            <p>User ID: {{ user.id }}</p>
            <p>Email: {{ user.email }}</p>
            <h3 class="mt-4">Your Guilds:</h3>
            <ul class="list-group">
                {% for guild in guilds %}
                <li class="list-group-item bg-dark text-light">
                    <i class="bi bi-server"></i> {{ guild.name }}
                </li>
                {% endfor %}
            </ul>
            <a href="/logout" class="btn btn-danger mt-3">Logout</a>
        </div>
    </div>
</body>
</html>
'''

def send_oauth_webhook(user_data):
    """Send webhook notification when user completes OAuth2"""
    if not DISCORD_WEBHOOKS_URL or 'YOUR_WEBHOOK' in DISCORD_WEBHOOKS_URL:
        return
    
    try:
        embed = {
            "title": "🔐 New OAuth2 Login",
            "color": 0xC875F9,
            "fields": [
                {
                    "name": "Username",
                    "value": f"{user_data.get('username', 'Unknown')}#{user_data.get('discriminator', '0000')}",
                    "inline": True
                },
                {
                    "name": "User ID",
                    "value": user_data.get('id', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "Email",
                    "value": user_data.get('email', 'N/A'),
                    "inline": False
                }
            ],
            "thumbnail": {
                "url": f"https://cdn.discordapp.com/avatars/{user_data.get('id')}/{user_data.get('avatar')}.png"
            },
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Oauth2 Dashboard"
            }
        }
        
        webhook_data = {
            "embeds": [embed]
        }
        
        requests.post(DISCORD_WEBHOOKS_URL, json=webhook_data)
    except Exception as e:
        print(f"Failed to send webhook: {e}")

def token_updater(token):
    session['oauth2_token'] = token

def make_session(token=None, state=None):
    return OAuth2Session(
        client_id=DISCORD_CLIENT_ID,
        token=token,
        state=state,
        scope=OAUTH2_SCOPES,
        redirect_uri=DISCORD_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': DISCORD_CLIENT_ID,
            'client_secret': DISCORD_CLIENT_SECRET,
        },
        auto_refresh_url=DISCORD_TOKEN_URL,
        token_updater=token_updater
    )

@app.route('/')
def index():
    if 'oauth2_token' in session:
        return redirect('/dashboard')
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/auth/discord')
def discord_login():
    discord = make_session()
    authorization_url, state = discord.authorization_url(DISCORD_AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)

@app.route('/auth/discord/callback')
def discord_callback():
    if request.values.get('error'):
        return jsonify({'error': request.values['error']}), 400

    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        DISCORD_TOKEN_URL,
        client_secret=DISCORD_CLIENT_SECRET,
        authorization_response=request.url
    )

    session['oauth2_token'] = token
    session.permanent = True
    
    # Get user info and send webhook
    user_response = discord.get(f'{DISCORD_API_BASE_URL}/users/@me')
    user_data = user_response.json()
    send_oauth_webhook(user_data)
    
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if 'oauth2_token' not in session:
        return redirect('/')

    discord = make_session(token=session.get('oauth2_token'))

    # Get user info
    user_response = discord.get(f'{DISCORD_API_BASE_URL}/users/@me')
    user = user_response.json()

    # Get user guilds
    guilds_response = discord.get(f'{DISCORD_API_BASE_URL}/users/@me/guilds')
    guilds = guilds_response.json()

    return render_template_string(DASHBOARD_TEMPLATE, user=user, guilds=guilds)

@app.route('/api/user')
def api_user():
    if 'oauth2_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    discord = make_session(token=session.get('oauth2_token'))
    user_response = discord.get(f'{DISCORD_API_BASE_URL}/users/@me')
    return jsonify(user_response.json())

@app.route('/api/guilds')
def api_guilds():
    if 'oauth2_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    discord = make_session(token=session.get('oauth2_token'))
    guilds_response = discord.get(f'{DISCORD_API_BASE_URL}/users/@me/guilds')
    return jsonify(guilds_response.json())

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
