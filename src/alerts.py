import smtplib
from email.mime.text import MIMEText

def send_alert(threat, risk_score):
    """
    Sends an email alert for high-risk threats with a Risk Score > 20.

    Args:
        threat (str): The detected threat (e.g., "SQL Injection Attack").
        risk_score (int): The risk score associated with the threat.
    """
    # Check if the risk score is above the threshold
    if risk_score > 20:
        # Create the email message
        msg = MIMEText(f"High-Risk Threat Detected: {threat} with Risk Score {risk_score}")
        msg["Subject"] = "Critical Cybersecurity Alert"
        msg["From"] = "alerts@shopsmart.com"
        msg["To"] = "admin@shopsmart.com"

        # Send the email
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  # Upgrade the connection to secure
                server.login("sssalerts@gmail.com", "sss_Pass123")  # Replace with your email credentials
                server.sendmail("alerts@shopsmart.com", "admin@shopsmart.com", msg.as_string())
            print(f"Alert sent for threat: {threat} with Risk Score {risk_score}")
        except Exception as e:
            print(f"Failed to send alert: {e}")
    else:
        print(f"No alert sent. Risk Score {risk_score} is below the threshold.")

# Example Usage
# if __name__ == "__main__":
#    send_alert("SQL Injection Attack", 25)
