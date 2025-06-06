import pandas as pd

def detect_conflicts(df):
    conflicts = []
    df = df.sort_values(by='timestamp')
    for i in range(len(df)):
        for j in range(i+1, len(df)):
            if abs(df.iloc[i]['altitude'] - df.iloc[j]['altitude']) < 1000:
                if abs(df.iloc[i]['lat'] - df.iloc[j]['lat']) < 0.05 and abs(df.iloc[i]['lon'] - df.iloc[j]['lon']) < 0.05:
                    conflicts.append({
                        'Flight 1': df.iloc[i]['flight_id'],
                        'Flight 2': df.iloc[j]['flight_id'],
                        'Altitudes': (df.iloc[i]['altitude'], df.iloc[j]['altitude']),
                        'Latitudes': (df.iloc[i]['lat'], df.iloc[j]['lat']),
                        'Longitudes': (df.iloc[i]['lon'], df.iloc[j]['lon']),
                        'Timestamps': (df.iloc[i]['timestamp'], df.iloc[j]['timestamp'])
                    })
    return pd.DataFrame(conflicts)
