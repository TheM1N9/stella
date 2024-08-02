import datetime
from credentials.google_credentials import calendar_service
from features.self_response import answer_yourself

def get_calendar_events():
    """Get upcoming calendar events."""

    response = "No upcoming events found."
    
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = calendar_service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        response = 'No upcoming events found.'
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"Event: {event['summary']} at {start}")
        response += f"Event: {event['summary']} at {start},\n"

    return response

if __name__ == "__main__":
    # Example usage
    get_calendar_events()
