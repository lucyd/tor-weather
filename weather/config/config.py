"""
Configuration settings.

For vagrant, copy config-vagrant.py over top of this.
For now, I'm leaving the production values in here as-is.

@var authenticator: The authentication key
@var listener_port: The Tor control port for the listener to use. This port
    must be configured in the torrc file.
@var updater_port: The Tor control port for the updater to use. This port
    must be configured in the torrc file.
@var base_url: The root URL for the Tor Weather web application.
"""

# XXX: Make bulletproof
authenticator = open("/home/weather/opt/current/weather/config/auth_token", "r").read().strip()

#The Tor control port to use
control_port = 9051

#The base URL for the Tor Weather web application:
base_url = 'https://weather.torproject.org'
