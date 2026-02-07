from datetime import datetime

def in_hours(open_t, close_t, requested):
    o = datetime.strptime(open_t, "%H:%M")
    c = datetime.strptime(close_t, "%H:%M")
    r = datetime.strptime(requested, "%H:%M")
    return o <= r <= c

def pick_table(party, slot):
    valid = [int(size) for size, cnt in slot.items() if cnt > 0 and int(size) >= party]
    return min(valid) if valid else None

def suggest_times(schedule, time):
    times = sorted(schedule.keys())
    if time not in times:
        return times[:2]
    i = times.index(time)
    return [t for t in times[max(0, i-1):i+2] if t != time]
