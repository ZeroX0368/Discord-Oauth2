
# Discord OAuth2 Dashboard

A Flask-based web application that implements Discord OAuth2 authentication, allowing users to log in with their Discord account and view their profile information and server list.

## Features

- 🔐 **Discord OAuth2 Authentication** - Secure login using Discord's OAuth2 protocol
- 👤 **User Profile Display** - Shows Discord username, avatar, and email
- 🖥️ **Server List** - Displays all Discord servers the user is a member of
- 🤖 **Auto-Join Server** - Automatically adds authenticated users to a specified Discord server
- 📢 **Webhook Notifications** - Sends notifications via Discord webhook when users authenticate
- 🎨 **Modern UI** - Beautiful glass-morphism design with dark theme

```
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=your_callback_url
DISCORD_GUILD_ID=your_server_id
DISCORD_WEBHOOKS_URI=your_webhook_url
```

## Installation

1. Clone the repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your Discord Application:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Add OAuth2 redirect URL: `http://0.0.0.0:5000/auth/discord/callback`
   - Enable the following scopes: `identify`, `guilds`, `guilds.join`

## Running the Application

### Locally

```bash
python api.py
```

The application will be available at `http://0.0.0.0:5000`

## Application Structure

```
├── api.py              # Main Flask application
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## Routes

- `GET /` - Login page (redirects to dashboard if authenticated)
- `GET /auth/discord` - Initiates Discord OAuth2 flow
- `GET /auth/discord/callback` - OAuth2 callback handler
- `GET /dashboard` - User dashboard (requires authentication)
- `GET /api/user` - Returns authenticated user data as JSON
- `GET /api/guilds` - Returns user's guilds as JSON
- `GET /logout` - Clears session and logs out user

## Features Explained

### OAuth2 Flow

1. User clicks "Login with Discord" on the login page
2. User is redirected to Discord for authorization
3. After approval, Discord redirects back with authorization code
4. Application exchanges code for access token
5. User information is retrieved and stored in session

### Auto-Join Server

When a user completes OAuth2 authentication, the application automatically attempts to add them to the Discord server specified by `DISCORD_GUILD_ID` .

### Webhook Notifications

Each successful login triggers a webhook notification to the configured Discord channel with user details including:
- Username and discriminator
- User ID
- Email
- Avatar thumbnail
