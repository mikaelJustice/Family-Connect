import streamlit as st
from datetime import datetime, timedelta
import random
import string
import base64
from io import BytesIO
from PIL import Image
import time

# In-memory storage
class FamilyConnectDB:
    def __init__(self):
        self.families = {}  # family_code: family_data
        self.admin_users = {"admin": "admin123"}  # admin credentials
        self.current_user = None
        self.current_family = None

        # Demo family
        demo_code = "DEMO2025"
        self.families[demo_code] = {
            "name": "Smith Family",
            "code": demo_code,
            "created": datetime.now().isoformat(),
            "users": {
                "dad": {
                    "name": "Dad", "avatar": "👨", "status": "At work",
                    "password": "demo123", "role": "Father", "birthday": "1980-05-15",
                    "profile_pic": None, "bio": "Head of the family", "email": "dad@smith.com"
                },
                "mom": {
                    "name": "Mom", "avatar": "👩", "status": "At home",
                    "password": "demo123", "role": "Mother", "birthday": "1982-08-22",
                    "profile_pic": None, "bio": "Family organizer", "email": "mom@smith.com"
                },
                "sarah": {
                    "name": "Sarah", "avatar": "👧", "status": "School",
                    "password": "demo123", "role": "Daughter", "birthday": "2010-03-10",
                    "profile_pic": None, "bio": "Soccer star ⚽", "email": "sarah@smith.com"
                },
                "tommy": {
                    "name": "Tommy", "avatar": "👦", "status": "At home",
                    "password": "demo123", "role": "Son", "birthday": "2012-11-05",
                    "profile_pic": None, "bio": "Gamer 🎮", "email": "tommy@smith.com"
                }
            },
            "announcements": [
                {
                    "id": 1, "author": "Dad", "role": "Father",
                    "content": "🏠 Family meeting tonight at 7 PM to discuss weekend plans!",
                    "timestamp": datetime.now().isoformat(), "type": "text",
                    "reactions": {"❤️": ["Mom", "Sarah"], "👍": ["Tommy"]},
                    "priority": "high", "comments": []
                }
            ],
            "messages": [
                {"author": "Mom", "role": "Mother", "content": "What does everyone want for dinner? 🍽️",
                 "timestamp": datetime.now().isoformat(), "reactions": {}},
                {"author": "Sarah", "role": "Daughter", "content": "Can we have pizza? 🍕",
                 "timestamp": datetime.now().isoformat(), "reactions": {}},
            ],
            "events": [
                {"id": 1, "title": "Sarah's Soccer Game", "date": "2025-11-02", "time": "15:00",
                 "location": "City Stadium", "creator": "Mom", "attendees": []},
                {"id": 2, "title": "Family Movie Night", "date": "2025-11-05", "time": "19:00",
                 "location": "Home", "creator": "Dad", "attendees": []}
            ],
            "tasks": [
                {"id": 1, "task": "Take out trash", "assigned_to": "Tommy", "status": "pending",
                 "due": "2025-10-31", "created_by": "Mom"},
                {"id": 2, "task": "Buy groceries", "assigned_to": "Mom", "status": "completed",
                 "due": "2025-10-30", "created_by": "Dad"}
            ],
            "photos": [],
            "polls": [],
            "stories": []
        }

# Initialize database in session state
if 'db' not in st.session_state:
    st.session_state.db = FamilyConnectDB()

# Get database from session state
db = st.session_state.db

ROLE_COLORS = {
    "Father": "#3b82f6", "Mother": "#ec4899", "Son": "#10b981",
    "Daughter": "#a855f7", "Grandparent": "#f59e0b", "Other": "#6b7280"
}

def generate_family_code():
    """Generate a unique 8-character family code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if code not in db.families:
            return code

def get_role_color(role):
    return ROLE_COLORS.get(role, ROLE_COLORS["Other"])

def format_timestamp(iso_time):
    try:
        dt = datetime.fromisoformat(iso_time)
        now = datetime.now()
        diff = (now - dt).total_seconds()
        if diff < 60: return "Just now"
        if diff < 3600: return f"{int(diff/60)}m ago"
        if diff < 86400: return f"{int(diff/3600)}h ago"
        return dt.strftime("%b %d, %I:%M %p")
    except:
        return "Just now"

def get_current_family_data():
    """Get current family data"""
    if db.current_family and db.current_family in db.families:
        return db.families[db.current_family]
    return None

def get_user_avatar_html(username):
    """Get user avatar (profile pic or emoji)"""
    family = get_current_family_data()
    if not family:
        return "👤"

    user = family['users'].get(username, {})
    if user.get('profile_pic'):
        return f'<img src="{user["profile_pic"]}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">'
    return user.get('avatar', '👤')

# Admin Panel Functions
def admin_login(username, password):
    if username in db.admin_users and db.admin_users[username] == password:
        st.session_state.admin_logged_in = True
        return True, "✅ Admin access granted!"
    return False, "❌ Invalid admin credentials!"

def create_new_family(family_name):
    if not family_name.strip():
        return False, "❌ Family name required!"

    code = generate_family_code()
    db.families[code] = {
        "name": family_name,
        "code": code,
        "created": datetime.now().isoformat(),
        "users": {},
        "announcements": [],
        "messages": [],
        "events": [],
        "tasks": [],
        "photos": [],
        "polls": [],
        "stories": []
    }

    return True, f"✅ Family '{family_name}' created! Code: {code}"

def delete_family(family_code):
    if family_code in db.families:
        family_name = db.families[family_code]['name']
        del db.families[family_code]
        return True, f"✅ Family '{family_name}' deleted!"
    return False, "❌ Family code not found!"

def get_admin_dashboard_html():
    html = f"""
    <div style='padding: 20px;'>
        <h2 style='color: #111; margin-bottom: 20px;'>👑 Admin Dashboard</h2>

        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 30px; border-radius: 20px; color: white; margin-bottom: 30px;'>
            <div style='font-size: 48px; font-weight: bold; margin-bottom: 10px;'>{len(db.families)}</div>
            <div style='font-size: 18px;'>Total Families Registered</div>
        </div>

        <div style='background: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
            <h3 style='margin-bottom: 20px;'>📋 Registered Families</h3>
    """

    for code, family in db.families.items():
        member_count = len(family['users'])
        created_date = datetime.fromisoformat(family['created']).strftime('%B %d, %Y')

        html += f"""
        <div style='background: #f9fafb; padding: 20px; border-radius: 15px; margin-bottom: 15px;
                    border-left: 5px solid #3b82f6;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <h4 style='margin: 0 0 10px 0; color: #111;'>{family['name']}</h4>
                    <div style='font-size: 14px; color: #666;'>
                        🔑 Code: <strong>{code}</strong> |
                        👥 Members: {member_count} |
                        📅 Created: {created_date}
                    </div>
                </div>
            </div>
        </div>
        """

    html += "</div></div>"
    return html

# Dashboard HTML
def get_dashboard_html():
    family = get_current_family_data()
    if not family:
        return "<div>No family data available</div>"

    total_members = len(family['users'])
    total_announcements = len(family['announcements'])
    total_messages = len(family['messages'])
    upcoming_events = len([e for e in family['events'] if datetime.fromisoformat(e['date']) >= datetime.now()])
    pending_tasks = len([t for t in family['tasks'] if t['status'] == 'pending'])

    upcoming_bday = ""
    for username, user in family['users'].items():
        try:
            bday = datetime.strptime(user.get('birthday', ''), '%Y-%m-%d')
            today = datetime.now()
            next_bday = bday.replace(year=today.year)
            if next_bday < today:
                next_bday = next_bday.replace(year=today.year + 1)
            days_until = (next_bday - today).days
            if 0 <= days_until <= 30:
                upcoming_bday += f"<div style='background: #fef3c7; padding: 10px; border-radius: 10px; margin-top: 10px;'>🎂 {user['name']}'s birthday in {days_until} days!</div>"
        except:
            pass

    return f"""
    <div style='padding: 20px;'>
        <h2 style='color: #111; font-size: 28px; margin-bottom: 10px;'>👋 Welcome to {family['name']}!</h2>
        <p style='color: #666; margin-bottom: 25px;'>Family Code: <strong>{family['code']}</strong></p>

        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;'>
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 20px; color: white; box-shadow: 0 6px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 36px; font-weight: bold;'>{total_members}</div>
                <div style='font-size: 14px; opacity: 0.9;'>Family Members</div>
            </div>

            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 25px; border-radius: 20px; color: white; box-shadow: 0 6px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 36px; font-weight: bold;'>{total_announcements}</div>
                <div style='font-size: 14px; opacity: 0.9;'>Announcements</div>
            </div>

            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 25px; border-radius: 20px; color: white; box-shadow: 0 6px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 36px; font-weight: bold;'>{total_messages}</div>
                <div style='font-size: 14px; opacity: 0.9;'>Chat Messages</div>
            </div>

            <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 25px; border-radius: 20px; color: white; box-shadow: 0 6px 15px rgba(0,0,0,0.1);'>
                <div style='font-size: 36px; font-weight: bold;'>{upcoming_events}</div>
                <div style='font-size: 14px; opacity: 0.9;'>Upcoming Events</div>
            </div>
        </div>

        {upcoming_bday}

        <div style='background: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-top: 20px;'>
            <h3 style='color: #111; margin-bottom: 15px;'>🎯 Quick Stats</h3>
            <div style='color: #666; font-size: 15px; line-height: 2;'>
                ✅ {len([t for t in family['tasks'] if t['status'] == 'completed'])} tasks completed<br>
                ⏳ {pending_tasks} tasks pending<br>
                📅 {upcoming_events} events coming up<br>
                💬 Last message: {format_timestamp(family['messages'][-1]['timestamp']) if family['messages'] else 'No messages yet'}
            </div>
        </div>
    </div>
    """

# Announcements HTML
def get_announcements_html():
    family = get_current_family_data()
    if not family or not family['announcements']:
        return """<div style='text-align: center; padding: 60px; background: white; border-radius: 20px;'>
            <div style='font-size: 64px; margin-bottom: 20px;'>📢</div>
            <h3 style='color: #666; font-size: 20px;'>No announcements yet</h3></div>"""

    html = "<div style='padding: 10px;'>"
    for announcement in reversed(family['announcements']):
        role = announcement.get('role', 'Other')
        color = get_role_color(role)
        priority_badge = ""
        if announcement.get('priority') == 'high':
            priority_badge = "<span style='background: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; margin-left: 10px;'>🔥 HIGH PRIORITY</span>"

        reactions_html = " ".join([f"<span style='background: #f3f4f6; padding: 8px 14px; border-radius: 20px; margin-right: 8px; font-size: 16px;'>{emoji} {len(users)}</span>"
                                   for emoji, users in announcement.get('reactions', {}).items()])

        comments_html = ""
        if announcement.get('comments'):
            comments_html = f"<div style='margin-top: 15px; padding-top: 15px; border-top: 2px solid #e5e7eb;'>"
            for comment in announcement['comments'][:3]:
                comments_html += f"<div style='margin-bottom: 10px; font-size: 14px;'><strong>{comment['author']}:</strong> {comment['content']}</div>"
            if len(announcement['comments']) > 3:
                comments_html += f"<div style='color: #666; font-size: 13px;'>+ {len(announcement['comments']) - 3} more comments</div>"
            comments_html += "</div>"

        html += f"""
        <div style='background: white; border-radius: 20px; padding: 25px; margin-bottom: 20px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid {color};'>
            <div style='display: flex; align-items: start; gap: 20px;'>
                <div style='background: {color}; width: 60px; height: 60px; border-radius: 50%;
                           display: flex; align-items: center; justify-content: center;
                           color: white; font-weight: bold; font-size: 24px; flex-shrink: 0;
                           box-shadow: 0 3px 8px rgba(0,0,0,0.15);'>{announcement['author'][0]}</div>
                <div style='flex: 1; min-width: 0;'>
                    <div style='margin-bottom: 12px;'>
                        <strong style='color: #111; font-size: 18px; display: inline; margin-right: 8px;'>{announcement['author']}</strong>
                        <span style='background: {color}; color: white; padding: 4px 12px; border-radius: 12px;
                                    font-size: 12px; font-weight: 600;'>{role}</span>
                        {priority_badge}
                        <div style='color: #999; font-size: 14px; margin-top: 4px;'>{format_timestamp(announcement['timestamp'])}</div>
                    </div>
                    <div style='background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                               padding: 20px; border-radius: 15px; margin-bottom: 15px; border: 2px solid #e9ecef;'>
                        <p style='color: #111; font-size: 16px; line-height: 1.6; margin: 0; font-weight: 500;'>
                            {announcement['content']}</p>
                    </div>
                    <div style='display: flex; gap: 10px; flex-wrap: wrap;'>{reactions_html}</div>
                    {comments_html}
                </div>
            </div>
        </div>"""
    html += "</div>"
    return html

# Messages HTML with reactions
def get_messages_html():
    family = get_current_family_data()
    if not family or not family['messages']:
        return """<div style='text-align: center; padding: 60px; background: white; border-radius: 20px;'>
            <div style='font-size: 64px; margin-bottom: 20px;'>💬</div>
            <h3 style='color: #666; font-size: 20px;'>No messages yet</h3></div>"""

    html = "<div style='padding: 10px; max-height: 600px; overflow-y: auto;'>"
    for msg in family['messages']:
        role = msg.get('role', 'Other')
        color = get_role_color(role)

        reactions_html = ""
        if msg.get('reactions'):
            reactions_html = "<div style='margin-top: 8px;'>" + " ".join([
                f"<span style='background: #f3f4f6; padding: 4px 10px; border-radius: 12px; font-size: 13px; margin-right: 5px;'>{emoji} {len(users)}</span>"
                for emoji, users in msg['reactions'].items()
            ]) + "</div>"

        html += f"""
        <div style='margin-bottom: 20px; animation: fadeIn 0.3s;'>
            <div style='display: flex; align-items: start; gap: 15px;'>
                <div style='background: {color}; width: 50px; height: 50px; border-radius: 50%;
                           display: flex; align-items: center; justify-content: center;
                           color: white; font-weight: bold; font-size: 20px; flex-shrink: 0;
                           box-shadow: 0 2px 6px rgba(0,0,0,0.15);'>{msg['author'][0]}</div>
                <div style='flex: 1; min-width: 0;'>
                    <div style='margin-bottom: 8px;'>
                        <strong style='color: #111; font-size: 16px; margin-right: 8px;'>{msg['author']}</strong>
                        <span style='background: {color}; color: white; padding: 3px 10px; border-radius: 10px;
                                    font-size: 11px; font-weight: 600; margin-right: 8px;'>{role}</span>
                        <span style='color: #999; font-size: 13px;'>{format_timestamp(msg['timestamp'])}</span>
                    </div>
                    <div style='background: white; padding: 16px 20px; border-radius: 18px;
                               border-top-left-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                               border: 2px solid #f3f4f6;'>
                        <p style='color: #111; font-size: 15px; line-height: 1.5; margin: 0; font-weight: 500;'>{msg['content']}</p>
                        {reactions_html}
                    </div>
                </div>
            </div>
        </div>"""
    html += "</div>"
    return html

# Events HTML
def get_events_html():
    family = get_current_family_data()
    if not family or not family['events']:
        return """<div style='text-align: center; padding: 60px; background: white; border-radius: 20px;'>
            <div style='font-size: 64px; margin-bottom: 20px;'>📅</div>
            <h3 style='color: #666; font-size: 20px;'>No events scheduled</h3></div>"""

    html = "<div style='padding: 10px;'>"
    for event in sorted(family['events'], key=lambda x: x['date']):
        try:
            event_date = datetime.fromisoformat(event['date'])
        except ValueError:
            try:
                event_date = datetime.strptime(event['date'], '%d/%B/%y')
            except ValueError:
                try:
                    event_date = datetime.strptime(event['date'], '%Y-%m-%d')
                except ValueError:
                    continue

        is_today = event_date.date() == datetime.now().date()
        border_color = "#ef4444" if is_today else "#3b82f6"

        attendees_html = ""
        if event.get('attendees'):
            attendees_html = f"<div style='margin-top: 10px;'>👥 Attending: {', '.join(event['attendees'])}</div>"

        html += f"""
        <div style='background: white; border-radius: 20px; padding: 20px; margin-bottom: 15px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid {border_color};'>
            <div style='display: flex; justify-content: space-between; align-items: start;'>
                <div style='flex: 1;'>
                    <h3 style='color: #111; font-size: 18px; margin: 0 0 10px 0; font-weight: bold;'>
                        {event['title']} {'🔴' if is_today else ''}</h3>
                    <div style='color: #666; font-size: 14px; line-height: 1.8;'>
                        📅 {event_date.strftime('%B %d, %Y')}<br>
                        🕐 {event['time']}<br>
                        📍 {event['location']}<br>
                        👤 Created by {event['creator']}
                        {attendees_html}
                    </div>
                </div>
            </div>
        </div>"""
    html += "</div>"
    return html

# Tasks HTML
def get_tasks_html():
    family = get_current_family_data()
    if not family or not family['tasks']:
        return """<div style='text-align: center; padding: 60px; background: white; border-radius: 20px;'>
            <div style='font-size: 64px; margin-bottom: 20px;'>✅</div>
            <h3 style='color: #666; font-size: 20px;'>No tasks assigned</h3></div>"""

    html = "<div style='padding: 10px;'>"
    for task in family['tasks']:
        status_color = "#10b981" if task['status'] == 'completed' else "#f59e0b"
        status_icon = "✅" if task['status'] == 'completed' else "⏳"
        opacity = "0.6" if task['status'] == 'completed' else "1"

        html += f"""
        <div style='background: white; border-radius: 15px; padding: 20px; margin-bottom: 15px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08); opacity: {opacity};
                    border-left: 4px solid {status_color};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='flex: 1;'>
                    <div style='font-size: 16px; font-weight: 600; color: #111; margin-bottom: 8px;'>
                        {status_icon} {task['task']}</div>
                    <div style='font-size: 13px; color: #666;'>
                        👤 Assigned to: <strong>{task['assigned_to']}</strong> |
                        📅 Due: {task['due']} |
                        ✍️ By: {task.get('created_by', 'Unknown')}
                    </div>
                </div>
                <span style='background: {status_color}; color: white; padding: 6px 14px;
                            border-radius: 12px; font-size: 12px; font-weight: 600;'>
                    {task['status'].upper()}</span>
            </div>
        </div>"""
    html += "</div>"
    return html

# Family Members HTML
def get_family_members_html():
    family = get_current_family_data()
    if not family:
        return ""

    html = "<div style='background: white; border-radius: 20px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>"
    html += "<h3 style='margin: 0 0 20px 0; color: #111; font-size: 20px; font-weight: bold;'>👥 Family Members</h3>"

    for username, user in family['users'].items():
        is_current = username == db.current_user
        border = "border: 3px solid #3b82f6; background: #eff6ff;" if is_current else "background: #f9fafb;"
        role = user.get('role', 'Other')
        color = get_role_color(role)

        avatar_content = get_user_avatar_html(username)

        html += f"""
        <div style='display: flex; align-items: center; gap: 15px; padding: 15px;
                    border-radius: 15px; margin-bottom: 12px; {border}
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
            <div style='background: {color}; width: 50px; height: 50px; border-radius: 50%;
                       display: flex; align-items: center; justify-content: center;
                       font-size: 28px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); overflow: hidden;'>{avatar_content}</div>
            <div style='flex: 1; min-width: 0;'>
                <div style='font-weight: bold; color: #111; font-size: 16px; margin-bottom: 4px;'>
                    {user['name']} {'(You)' if is_current else ''}</div>
                <div style='font-size: 13px; margin-bottom: 4px;'>
                    <span style='background: {color}; color: white; padding: 3px 10px;
                                border-radius: 10px; font-weight: 600;'>{role}</span>
                </div>
                <div style='font-size: 12px; color: #666;'>{user['status']}</div>
            </div>
            <div style='width: 12px; height: 12px; background: #10b981; border-radius: 50%;
                       box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);'></div>
        </div>"""
    html += "</div>"
    return html

# Photo Gallery HTML
def get_photos_html():
    family = get_current_family_data()
    if not family or not family.get('photos'):
        return """<div style='text-align: center; padding: 60px; background: white; border-radius: 20px;'>
            <div style='font-size: 64px; margin-bottom: 20px;'>📸</div>
            <h3 style='color: #666; font-size: 20px;'>No photos yet</h3></div>"""

    html = "<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; padding: 10px;'>"
    for photo in reversed(family['photos']):
        html += f"""
        <div style='background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
            <img src="{photo['image']}" style='width: 100%; height: 250px; object-fit: cover;'>
            <div style='padding: 15px;'>
                <div style='font-weight: bold; color: #111; margin-bottom: 5px;'>{photo['caption']}</div>
                <div style='font-size: 13px; color: #666;'>By {photo['author']} • {format_timestamp(photo['timestamp'])}</div>
            </div>
        </div>"""
    html += "</div>"
    return html

# Polls HTML
def get_polls_html():
    family = get_current_family_data()
    if not family or not family.get('polls'):
        return """<div style='text-align: center; padding: 60px; background: white; border-radius: 20px;'>
            <div style='font-size: 64px; margin-bottom: 20px;'>📊</div>
            <h3 style='color: #666; font-size: 20px;'>No polls yet</h3></div>"""

    html = "<div style='padding: 10px;'>"
    for poll in reversed(family['polls']):
        total_votes = sum(len(votes) for votes in poll['votes'].values())
        html += f"""
        <div style='background: white; border-radius: 20px; padding: 25px; margin-bottom: 20px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
            <h3 style='color: #111; margin-bottom: 15px;'>{poll['question']}</h3>
            <div style='font-size: 13px; color: #666; margin-bottom: 15px;'>
                By {poll['creator']} • {format_timestamp(poll['timestamp'])} • {total_votes} votes
            </div>
        """
        for option, voters in poll['votes'].items():
            vote_count = len(voters)
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            html += f"""
            <div style='margin-bottom: 12px;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                    <span style='font-weight: 500;'>{option}</span>
                    <span style='color: #666;'>{vote_count} votes ({percentage:.0f}%)</span>
                </div>
                <div style='background: #e5e7eb; border-radius: 10px; height: 8px; overflow: hidden;'>
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                               height: 100%; width: {percentage}%; transition: width 0.3s;'></div>
                </div>
            </div>"""
        html += "</div>"
    html += "</div>"
    return html

# Stories HTML
def get_stories_html():
    family = get_current_family_data()
    if not family or not family.get('stories'):
        return """<div style='text-align: center; padding: 60px; background: white; border-radius: 20px;'>
            <div style='font-size: 64px; margin-bottom: 20px;'>⭐</div>
            <h3 style='color: #666; font-size: 20px;'>No stories yet</h3></div>"""

    html = "<div style='display: flex; gap: 15px; overflow-x: auto; padding: 10px;'>"
    for story in family['stories']:
        # Check if story is still active (24 hours)
        story_time = datetime.fromisoformat(story['timestamp'])
        if (datetime.now() - story_time).total_seconds() > 86400:
            continue

        role = story.get('role', 'Other')
        color = get_role_color(role)

        html += f"""
        <div style='min-width: 120px; max-width: 120px;'>
            <div style='width: 120px; height: 120px; border-radius: 50%; background: {color};
                       padding: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                <div style='width: 100%; height: 100%; border-radius: 50%; background: white;
                           display: flex; align-items: center; justify-content: center;
                           font-size: 48px; overflow: hidden;'>
                    {story.get('content', '📷')}
                </div>
            </div>
            <div style='text-align: center; margin-top: 8px; font-size: 13px; color: #111; font-weight: 500;'>
                {story['author']}
            </div>
            <div style='text-align: center; font-size: 11px; color: #666;'>
                {format_timestamp(story['timestamp'])}
            </div>
        </div>"""
    html += "</div>"
    return html

# Authentication
def login(family_code, username, password):
    if family_code not in db.families:
        return False, "❌ Invalid family code!"

    family = db.families[family_code]
    if username in family['users'] and family['users'][username]['password'] == password:
        db.current_user = username
        db.current_family = family_code
        st.session_state.logged_in = True
        return True, f"✅ Welcome back, {family['users'][username]['name']}!"
    return False, "❌ Invalid credentials!"

def register(family_code, name, username, password, role, avatar, status, birthday, bio, email):
    if family_code not in db.families:
        return False, "❌ Invalid family code!"

    if not all([name, username, password, role]):
        return False, "❌ Fill all required fields!"

    family = db.families[family_code]
    if username in family['users']:
        return False, "❌ Username exists in this family!"

    family['users'][username] = {
        "name": name, "avatar": avatar or "👤", "status": status or "Available",
        "password": password, "role": role, "birthday": birthday,
        "profile_pic": None, "bio": bio or "", "email": email or ""
    }
    db.current_user = username
    db.current_family = family_code
    st.session_state.logged_in = True
    return True, f"✅ Welcome, {name}!"

def logout():
    db.current_user = None
    db.current_family = None
    st.session_state.logged_in = False
    st.session_state.admin_logged_in = False

# Profile picture update
def update_profile_picture(image):
    if not db.current_user or not db.current_family:
        return False, "❌ You must be logged in"

    if image is None:
        return False, "❌ Please upload an image"

    family = get_current_family_data()
    if family:
        # Convert image to base64
        # Resize and convert image
        img = Image.open(image)
        img = img.resize((200, 200))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        family['users'][db.current_user]['profile_pic'] = f"data:image/png;base64,{img_str}"

        return True, "✅ Profile picture updated!"

    return False, "❌ Error updating profile picture"

# Main functions
def post_announcement(content, priority):
    if not db.current_user or not content.strip():
        return False, "❌ Cannot post empty announcement!"

    family = get_current_family_data()
    if not family:
        return False, "❌ No family selected!"

    user = family['users'][db.current_user]
    family['announcements'].append({
        "id": len(family['announcements']) + 1, "author": user['name'],
        "role": user.get('role', 'Other'), "content": content,
        "timestamp": datetime.now().isoformat(), "type": "text",
        "reactions": {}, "priority": priority, "comments": []
    })
    return True, "✅ Announcement posted!"

def send_message(content):
    if not db.current_user or not content.strip():
        return False, "❌ Cannot send empty message!"

    family = get_current_family_data()
    if not family:
        return False, "❌ No family selected!"

    user = family['users'][db.current_user]
    family['messages'].append({
        "author": user['name'], "role": user.get('role', 'Other'),
        "content": content, "timestamp": datetime.now().isoformat(),
        "reactions": {}
    })
    return True, ""

def add_event(title, date, time, location):
    if not db.current_user or not all([title, date, time]):
        return False, "❌ Fill all fields!"

    family = get_current_family_data()
    if not family:
        return False, "❌ No family selected!"

    try:
        if '/' in date:
            event_date = datetime.strptime(date, '%d/%B/%y')
        else:
            event_date = datetime.strptime(date, '%Y-%m-%d')
        iso_date = event_date.isoformat().split('T')[0]
    except ValueError:
        return False, "❌ Invalid date format! Use YYYY-MM-DD or DD/Month/YY"

    family['events'].append({
        "id": len(family['events']) + 1, "title": title, "date": iso_date,
        "time": time, "location": location or "TBD",
        "creator": family['users'][db.current_user]['name'],
        "attendees": []
    })
    return True, "✅ Event added!"

def add_task(task, assigned_to, due_date):
    if not db.current_user or not all([task, assigned_to, due_date]):
        return False, "❌ Fill all fields!"

    family = get_current_family_data()
    if not family:
        return False, "❌ No family selected!"

    family['tasks'].append({
        "id": len(family['tasks']) + 1, "task": task,
        "assigned_to": assigned_to, "status": "pending", "due": due_date,
        "created_by": family['users'][db.current_user]['name']
    })
    return True, "✅ Task added!"

def upload_photo(image, caption):
    if not db.current_user or not image:
        return False, "❌ Please upload an image!"

    family = get_current_family_data()
    if not family:
        return False, "❌ No family selected!"

    img = Image.open(image)
    img.thumbnail((800, 800))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    family['photos'].append({
        "id": len(family['photos']) + 1,
        "image": f"data:image/png;base64,{img_str}",
        "caption": caption or "Family photo",
        "author": family['users'][db.current_user]['name'],
        "timestamp": datetime.now().isoformat()
    })

    return True, "✅ Photo uploaded!"

def create_poll(question, options):
    if not db.current_user or not question.strip():
        return False, "❌ Enter a question!"

    family = get_current_family_data()
    if not family:
        return False, "❌ No family selected!"

    option_list = [opt.strip() for opt in options.split('\n') if opt.strip()]
    if len(option_list) < 2:
        return False, "❌ Need at least 2 options!"

    family['polls'].append({
        "id": len(family['polls']) + 1,
        "question": question,
        "votes": {opt: [] for opt in option_list},
        "creator": family['users'][db.current_user]['name'],
        "timestamp": datetime.now().isoformat()
    })

    return True, "✅ Poll created!"

def post_story(content):
    if not db.current_user or not content.strip():
        return False, "❌ Story cannot be empty!"

    family = get_current_family_data()
    if not family:
        return False, "❌ No family selected!"

    user = family['users'][db.current_user]
    family['stories'].append({
        "id": len(family['stories']) + 1,
        "author": user['name'],
        "role": user.get('role', 'Other'),
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

    return True, "✅ Story posted!"

# Main app
def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 40px; border-radius: 20px; margin-bottom: 30px;
            text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style='font-size: 48px; margin-bottom: 10px; font-weight: bold;'>👨‍👩‍👧‍👦 FamilyConnect Pro</h1>
        <p style='font-size: 20px; opacity: 0.95;'>Multi-Family Communication Platform</p>
    </div>
    """, unsafe_allow_html=True)

    # Admin Panel
    if st.session_state.admin_logged_in:
        st.markdown("## 👑 Admin Dashboard")
        st.markdown(get_admin_dashboard_html(), unsafe_allow_html=True)
        
        st.markdown("### ➕ Create New Family")
        with st.form("create_family_form"):
            new_family_name = st.text_input("Family Name", placeholder="Enter family name")
            if st.form_submit_button("Create Family"):
                success, message = create_new_family(new_family_name)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        st.markdown("### 🗑️ Delete Family")
        with st.form("delete_family_form"):
            delete_family_code = st.text_input("Family Code", placeholder="Enter code to delete")
            if st.form_submit_button("Delete Family"):
                success, message = delete_family(delete_family_code)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        if st.button("🚪 Logout"):
            logout()
            st.experimental_rerun()
    
    # User Login/Register
    elif not st.session_state.logged_in:
        # Admin Login Section
        st.markdown("## 👑 Admin Panel")
        with st.expander("Admin Login"):
            with st.form("admin_login_form"):
                admin_username = st.text_input("Admin Username", placeholder="admin")
                admin_password = st.text_input("Admin Password", type="password")
                if st.form_submit_button("🔐 Admin Login"):
                    success, message = admin_login(admin_username, admin_password)
                    if success:
                        st.success(message)
                        st.experimental_rerun()
                    else:
                        st.error(message)
        
        # User Login/Register Section
        st.markdown("## 🔐 Family Login or Register")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                login_family_code = st.text_input("Family Code*", placeholder="Enter your family code")
                login_username = st.text_input("Username")
                login_password = st.text_input("Password", type="password")
                if st.form_submit_button("🚀 Login"):
                    success, message = login(login_family_code, login_username, login_password)
                    if success:
                        st.success(message)
                        st.experimental_rerun()
                    else:
                        st.error(message)
            
            st.markdown("""### 👥 Demo Family Code: `DEMO2025` | Users: `dad`/`mom`/`sarah`/`tommy` | Password: `demo123`""")
        
        with tab2:
            with st.form("register_form"):
                reg_family_code = st.text_input("Family Code*", placeholder="Enter your family code")
                reg_name = st.text_input("Full Name*")
                reg_username = st.text_input("Username*")
                reg_password = st.text_input("Password*", type="password")
                reg_role = st.selectbox("Family Role*", ["Father", "Mother", "Son", "Daughter", "Grandparent", "Other"])
                reg_avatar = st.selectbox("Avatar", ["👨", "👩", "👧", "👦", "👴", "👵", "🧑", "👶"], index=7)
                reg_status = st.text_input("Status", value="Available")
                reg_birthday = st.text_input("Birthday (YYYY-MM-DD)", placeholder="1990-01-01")
                reg_bio = st.text_area("Bio", placeholder="Tell us about yourself")
                reg_email = st.text_input("Email", placeholder="your@email.com")
                
                if st.form_submit_button("📝 Create Account"):
                    success, message = register(reg_family_code, reg_name, reg_username, reg_password, reg_role,
                                               reg_avatar, reg_status, reg_birthday, reg_bio, reg_email)
                    if success:
                        st.success(message)
                        st.experimental_rerun()
                    else:
                        st.error(message)
    
    # Main App
    else:
        # Sidebar for navigation
        st.sidebar.markdown(f"## 👋 Welcome, {db.current_user}!")
        st.sidebar.markdown(f"**Family:** {get_current_family_data()['name']}")
        
        if st.sidebar.button("🚪 Logout"):
            logout()
            st.experimental_rerun()
        
        # Main content
        page = st.sidebar.selectbox("Navigation", [
            "🏠 Dashboard", "📢 Announcements", "💬 Family Chat", 
            "📅 Events Calendar", "✅ Family Tasks", "📸 Photo Gallery",
            "📊 Polls", "⭐ Stories (24h)", "👤 My Profile"
        ])
        
        # Dashboard
        if page == "🏠 Dashboard":
            st.markdown(get_dashboard_html(), unsafe_allow_html=True)
        
        # Announcements
        elif page == "📢 Announcements":
            st.markdown(get_announcements_html(), unsafe_allow_html=True)
            
            with st.expander("✍️ New Announcement"):
                with st.form("announcement_form"):
                    announcement_input = st.text_area("Message", placeholder="Share important updates with the family...")
                    announcement_priority = st.radio("Priority", ["normal", "high"])
                    if st.form_submit_button("📣 Post"):
                        success, message = post_announcement(announcement_input, announcement_priority)
                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
        
        # Family Chat
        elif page == "💬 Family Chat":
            st.markdown(get_messages_html(), unsafe_allow_html=True)
            
            with st.form("message_form"):
                message_input = st.text_area("Type message...", key="message_input")
                if st.form_submit_button("📤 Send"):
                    success, message = send_message(message_input)
                    if success:
                        st.experimental_rerun()
                    else:
                        st.error(message)
        
        # Events Calendar
        elif page == "📅 Events Calendar":
            st.markdown(get_events_html(), unsafe_allow_html=True)
            
            with st.expander("➕ Add Event"):
                with st.form("event_form"):
                    event_title = st.text_input("Event Title*")
                    col1, col2 = st.columns(2)
                    with col1:
                        event_date = st.text_input("Date (YYYY-MM-DD)*")
                    with col2:
                        event_time = st.text_input("Time (HH:MM)*")
                    event_location = st.text_input("Location")
                    if st.form_submit_button("📅 Add Event"):
                        success, message = add_event(event_title, event_date, event_time, event_location)
                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
        
        # Family Tasks
        elif page == "✅ Family Tasks":
            st.markdown(get_tasks_html(), unsafe_allow_html=True)
            
            with st.expander("➕ Add Task"):
                with st.form("task_form"):
                    task_input = st.text_input("Task Description*")
                    col1, col2 = st.columns(2)
                    with col1:
                        family = get_current_family_data()
                        if family:
                            user_names = [user['name'] for user in family['users'].values()]
                            task_assigned = st.selectbox("Assign To*", user_names)
                    with col2:
                        task_due = st.text_input("Due Date (YYYY-MM-DD)*")
                    if st.form_submit_button("✅ Add Task"):
                        success, message = add_task(task_input, task_assigned, task_due)
                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
        
        # Photo Gallery
        elif page == "📸 Photo Gallery":
            st.markdown(get_photos_html(), unsafe_allow_html=True)
            
            with st.expander("📤 Upload Photo"):
                with st.form("photo_form"):
                    photo_upload = st.file_uploader("Select Photo", type=["jpg", "jpeg", "png"])
                    photo_caption = st.text_input("Caption", placeholder="Add a caption...")
                    if st.form_submit_button("📸 Upload"):
                        success, message = upload_photo(photo_upload, photo_caption)
                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
        
        # Polls
        elif page == "📊 Polls":
            st.markdown(get_polls_html(), unsafe_allow_html=True)
            
            with st.expander("➕ Create Poll"):
                with st.form("poll_form"):
                    poll_question = st.text_input("Question*", placeholder="What should we do this weekend?")
                    poll_options = st.text_area("Options (one per line)*", 
                                               placeholder="Go to beach\nStay home\nVisit grandparents")
                    if st.form_submit_button("📊 Create Poll"):
                        success, message = create_poll(poll_question, poll_options)
                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
        
        # Stories
        elif page == "⭐ Stories (24h)":
            st.markdown(get_stories_html(), unsafe_allow_html=True)
            
            with st.expander("➕ Post Story"):
                with st.form("story_form"):
                    story_content = st.text_area("Story", placeholder="Share what's happening... (expires in 24h)")
                    if st.form_submit_button("⭐ Post Story"):
                        success, message = post_story(story_content)
                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
        
        # Profile
        elif page == "👤 My Profile":
            st.markdown("## 👤 Profile Settings")
            
            with st.expander("📸 Update Profile Picture"):
                with st.form("profile_pic_form"):
                    profile_pic_upload = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
                    if st.form_submit_button("📸 Update Profile Picture"):
                        success, message = update_profile_picture(profile_pic_upload)
                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
            
            # Display family members
            st.markdown(get_family_members_html(), unsafe_allow_html=True)
            
            # Display features
            st.markdown("""
            ### ✨ Features
            - 🏠 **Multi-Family**: Each family has unique code
            - 📢 **Announcements**: Reach everyone instantly
            - 💬 **Family Chat**: Real-time conversations with reactions
            - 📅 **Calendar**: Track events & activities
            - ✅ **Tasks**: Assign & manage chores
            - 📸 **Photo Gallery**: Share family moments
            - 📊 **Polls**: Make decisions together
            - ⭐ **Stories**: 24-hour updates
            - 🎂 **Birthdays**: Never miss celebrations
            - 👤 **Profile Pics**: Personalize your account
            - 🔒 **Secure**: Protected family spaces
            - 👑 **Admin Panel**: Manage families
            """)

if __name__ == "__main__":
    main()
