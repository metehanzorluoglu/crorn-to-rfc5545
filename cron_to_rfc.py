from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def cron_to_rfc5545(cron_expression):
    """
    Converts a CRON expression to an RFC 5545 iCalendar recurrence rule.

    :param cron_expression: CRON expression as a string (e.g., "0 15 10 * * ?")
    :return: RFC 5545 iCalendar RRULE string
    """
    cron_parts = cron_expression.split()

    if len(cron_parts) != 5 and len(cron_parts) != 6:
        raise ValueError("Invalid CRON expression format")

    minute, hour, day_of_month, month, day_of_week = cron_parts[:5]
    if len(cron_parts) == 6:
        day_of_week = cron_parts[5]

    rrule = ["FREQ="]
    byday = None
    bymonth = None
    byhour = None
    byminute = None

    if minute != "*":
        if "*/" in minute:
            step = int(minute.split("/")[1])
            byminute = ",".join(str(i) for i in range(0, 60, step))
        else:
            byminute = minute

    if hour != "*":
        byhour = hour

    if day_of_week != "*" and day_of_week != "?":
        days_map = {
            "0": "SU", "1": "MO", "2": "TU", "3": "WE", "4": "TH", "5": "FR", "6": "SA"
        }
        days = [days_map.get(day.strip(), "") for day in day_of_week.split(",") if day.strip()]
        byday = ",".join(days)
        rrule[0] = "FREQ=WEEKLY"

    if month != "*":
        bymonth = month
        rrule[0] = "FREQ=YEARLY"

    if day_of_month != "*" and day_of_week == "?":
        rrule[0] = "FREQ=MONTHLY"
        rrule.append(f"BYMONTHDAY={day_of_month}")

    if byminute:
        rrule.append(f"BYMINUTE={byminute}")
    if byhour:
        rrule.append(f"BYHOUR={byhour}")
    if byday:
        rrule.append(f"BYDAY={byday}")
    if bymonth:
        rrule.append(f"BYMONTH={bymonth}")

    return "RRULE:" + ";".join(rrule)

@app.route('/convert-cron', methods=['POST'])
def convert_cron():
    data = request.get_json()
    if not data or 'cron_expression' not in data:
        return jsonify({"error": "Missing 'cron_expression' in request body"}), 400

    cron_expression = data['cron_expression']

    try:
        rfc5545_rule = cron_to_rfc5545(cron_expression)
        return jsonify({"rfc5545_rule": rfc5545_rule})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
