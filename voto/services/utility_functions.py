def seconds_to_pretty(seconds):
    total_days = int(seconds / (24 * 60 * 60))
    years = total_days // 365
    days = total_days - (365 * years)
    if years:
        time_str = f"{years} years {days} days"
    else:
        time_str = f"{days} days"
    return time_str
