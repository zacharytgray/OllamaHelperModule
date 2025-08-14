from langchain_core.tools import tool
import os
from dotenv import load_dotenv
import spotipy
from spotipy import SpotifyOAuth
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv('keys.env')
scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
auth_manager = SpotifyOAuth(scope=scope, cache_path='.cache')
sp = spotipy.Spotify(auth_manager=auth_manager)

@tool
def play_song_by_search(query: str, limit: int = 5) -> str:
    """
    Search for a song on Spotify and play it.
    
    Parameters:
    - query (str): The search query (song name, artist, or both).
    - limit (int): Maximum number of search results to consider (default: 5).
    
    Returns:
    - str: Success message with song details or error description.
    """
    try:
        # Search for tracks
        results = sp.search(q=query, type='track', limit=limit)
        
        if not results['tracks']['items']:
            return f"No songs found for query: '{query}'"
        
        # Get the first (most relevant) track
        track = results['tracks']['items'][0]
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        track_uri = track['uri']
        
        # Get current playback info to check if there's an active device
        current_playback = sp.current_playback()
        
        if current_playback is None or not current_playback.get('device'):
            # No active device, get available devices
            devices = sp.devices()
            if not devices['devices']:
                return "No active Spotify devices found. Please open Spotify on a device first."
            
            # Use the first available device
            device_id = devices['devices'][0]['id']
            device_name = devices['devices'][0]['name']
            
            # Start playback on the device
            sp.start_playback(device_id=device_id, uris=[track_uri])
            return f"Started playing '{track_name}' by {artist_name} on device '{device_name}'"
        else:
            # There's an active device, play the track
            sp.start_playback(uris=[track_uri])
            return f"Now playing '{track_name}' by {artist_name}"
            
    except Exception as e:
        return f"Error playing song: {str(e)}"


@tool
def get_spotify_playback_info() -> str:
    """
    Get information about the current Spotify playback.
    
    Returns:
    - str: Current playback information or status.
    """
    
    try:
        current_playback = sp.current_playback()
        
        if current_playback is None:
            return "No active Spotify playback found."
        
        if not current_playback.get('is_playing'):
            return "Spotify is paused."
        
        track = current_playback['item']
        if track:
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            album_name = track['album']['name']
            progress_ms = current_playback.get('progress_ms', 0)
            duration_ms = track.get('duration_ms', 0)
            
            # Convert milliseconds to minutes:seconds
            progress_min = progress_ms // 60000
            progress_sec = (progress_ms % 60000) // 1000
            duration_min = duration_ms // 60000
            duration_sec = (duration_ms % 60000) // 1000
            
            return (f"Currently playing: '{track_name}' by {artist_name} "
                   f"from album '{album_name}' "
                   f"({progress_min:02d}:{progress_sec:02d} / {duration_min:02d}:{duration_sec:02d})")
        else:
            return "Spotify is active but no track information available."
            
    except Exception as e:
        return f"Error getting playback info: {str(e)}"


@tool
def control_spotify_playback(action: str) -> str:
    """
    Control Spotify playback (play, pause, next, previous).
    
    Parameters:
    - action (str): The action to perform ('play', 'pause', 'next', 'previous').
    
    Returns:
    - str: Success message or error description.
    """
    try:
        if action.lower() == 'play':
            sp.start_playback()
            return "Playback resumed"
        elif action.lower() == 'pause':
            sp.pause_playback()
            return "Playback paused"
        elif action.lower() == 'next':
            sp.next_track()
            return "Skipped to next track"
        elif action.lower() == 'previous':
            sp.previous_track()
            return "Skipped to previous track"
        else:
            return f"Unknown action: {action}. Use 'play', 'pause', 'next', or 'previous'"
            
    except Exception as e:
        return f"Error controlling playback: {str(e)}"

@tool
def update_user_profile(key: str, value: str):
    """
    Updates the user's profile with a new piece of information. Use this when you learn something new about the user, like their preferences, interests, or personal details.

    Parameters:
    - key (str): The name of the profile attribute to update (e.g., 'favorite_color', 'hometown').
    - value (str): The value to assign to the attribute.
    """
    # The actual logic is handled inside the Agent class to access the user instance.
    # This function's purpose is to be exposed to the LLM.
    return f"Profile update for {key} scheduled."

@tool
def send_email(subject: str, receiver_email: str, content: str):
    """
    Send an HTML email with the specified subject and content.
    
    Parameters:
    - subject (str): The subject of the email.
    - receiver_email (str): The email address of the recipient.
    - content (str): The content of the email.
    """
    sender_email = os.getenv("EMAIL_SENDER")
    password = os.getenv("GOOGLE_APP_PWD")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    part1 = MIMEText(content, "html")
    message.attach(part1)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # Use appropriate server details for your email provider
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit()


# Function to dynamically collect all tools
def get_all_tools():
    """
    Dynamically collect all functions decorated with @tool in this module.
    Returns a list of all tool functions.
    """
    # Use globals() to get all objects in the current module
    tools = []
    for name, obj in globals().items():
        # Check if it's a tool by looking for the specific attributes
        if (hasattr(obj, 'name') and 
            hasattr(obj, 'description') and 
            hasattr(obj, 'func') and
            callable(obj) and
            not name.startswith('_')):
            tools.append(obj)
    
    return tools

# Initialize as None, will be populated when first accessed
_ALL_TOOLS = None

def get_tools():
    """Get all tools, populating the cache if needed."""
    global _ALL_TOOLS
    if _ALL_TOOLS is None:
        _ALL_TOOLS = get_all_tools()
    return _ALL_TOOLS

# For backward compatibility - this will be populated after all tools are defined
ALL_TOOLS = None

# This will be called at the end of the module to populate ALL_TOOLS
def _populate_tools():
    global ALL_TOOLS
    ALL_TOOLS = get_tools()

# Call this at the end of the module
_populate_tools()