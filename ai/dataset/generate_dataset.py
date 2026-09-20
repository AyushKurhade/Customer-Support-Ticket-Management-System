"""
Customer Support Ticket Dataset Generator
----------------------------------------
Generates a realistic, domain-specific dataset for training lightweight
text classification models (TF-IDF + Naive Bayes / Logistic Regression).
Outputs to: ai/dataset/ticket_data.csv
"""

import os
import random
import csv
from pathlib import Path

# Seed for absolute reproducibility
random.seed(42)

HARDWARE_TEMPLATES = [
    ("Laptop display flickering violently", "The built-in screen on my Dell Latitude keeps flickering whenever I adjust the hinge. It goes completely black for a few seconds. Need a replacement or cable check.", "High"),
    ("External monitor not detected via HDMI", "Connected an LG 27-inch monitor to my workstation using HDMI cable. Display settings show 'No Signal detected'. Tried another cable but issue persists.", "Medium"),
    ("Mechanical keyboard keys repeating and sticking", "The spacebar and Enter key on my office keyboard are sticking physically and registering double keystrokes. Cleaning with compressed air did not fix it.", "Low"),
    ("Wireless mouse cursor jumping erratically", "The Logitech wireless mouse cursor stutters across the screen and skips pixels even with fresh AA batteries. Mousepad is clean.", "Low"),
    ("Laser printer paper jam in tray 2", "The HP LaserJet printer on the 3rd floor has a continuous paper jam error. Opened tray 2 and cleared paper, but roller error indicator remains red.", "Medium"),
    ("Workstation overheating and shutting down", "My desktop PC fans are spinning at maximum RPM and making loud grinding noises. System shut down abruptly twice during rendering with CPU temp at 95C.", "Critical"),
    ("Laptop battery swelling and trackpad lifting", "Noticeable bulge beneath the trackpad on my ThinkPad. The touchpad is physically displaced. Battery is dangerously swollen and won't hold charge.", "Critical"),
    ("USB-C docking station ethernet port dead", "My Dell docking station powers the laptop and displays to dual monitors, but the RJ45 ethernet port has no link lights and network is disconnected.", "Medium"),
    ("Hard drive clicking noise and I/O error", "Secondary internal 1TB Seagate drive is producing rhythmic clicking noises. Windows Explorer freezes and throws 'The request failed due to a fatal device hardware error'.", "High"),
    ("Headset microphone not picking up audio", "Jabra USB headset audio output works fine, but teammates cannot hear me in Zoom or Teams meetings. Tested mic on Windows Sound settings with 0% input level.", "Low"),
    ("RAM memory failure causing BSOD", "Computer crashed three times today with MEMORY_MANAGEMENT blue screen. Windows Memory Diagnostic tool reported hardware memory problems detected.", "High"),
    ("Webcam hardware disconnected error", "Built-in laptop webcam gives error 0xA00F4244 NoCamerasAreAttached in Windows Camera app. Driver is missing in Device Manager.", "Medium"),
    ("Power supply unit burning smell", "Desktop PC suddenly lost power and emitted a faint electrical burning odor. System refuses to turn on when power button is pressed. No motherboard LEDs lit.", "Critical"),
    ("Touchscreen digitizer ghost touches", "Surface tablet screen is registering touches in the upper right corner on its own, making it impossible to click anywhere else.", "Medium"),
    ("Conference room TV display color distortion", "Main wall display in Conference Room B shows severe purple and green tint over HDMI input. Resetting display settings did not resolve.", "Low")
]

SOFTWARE_TEMPLATES = [
    ("Excel crashes when opening large pivot table", "Microsoft Excel 365 freezes and abruptly crashes whenever I open our quarterly sales workbook containing 80,000 rows. Event Viewer logs faulting module ntdll.dll.", "High"),
    ("Outlook desktop stuck on loading profile", "Opening Microsoft Outlook hangs indefinitely at the splash screen saying 'Loading Profile'. Tried starting in Safe Mode (outlook.exe /safe) with no success.", "High"),
    ("Missing VCRUNTIME140.dll error on launch", "Unable to run corporate ERP application. System error pop-up states: 'The code execution cannot proceed because VCRUNTIME140.dll was not found'.", "Medium"),
    ("Windows 11 update stuck at 78% loop", "Cumulative update KB5034441 has been stuck at 78% for 4 hours. Rebooting causes the system to attempt rollback and install again in an endless loop.", "High"),
    ("Adobe Acrobat Reader crashing on PDF sign", "Whenever I attempt to place a digital certificate signature on contract documents, Adobe Acrobat DC closes immediately without an error message.", "Medium"),
    ("Slack desktop client white blank screen", "Slack application opens to a solid blank white window. Ctrl+R to reload does not render UI. Browser version works fine.", "Low"),
    ("Antivirus blocking legitimate internal tool", "Windows Defender / CrowdStrike flagged our internal deployment script as Trojan:Win32/Wacatac and quarantined the binary file.", "High"),
    ("Zoom meeting video freezes after 5 minutes", "During video calls Zoom client freezes video feed while audio continues. Graphic driver is up to date, but hardware acceleration setting crashes app.", "Medium"),
    ("Software license activation key invalid", "Reinstalled AutoCAD on my new machine, but the company serial number produces error 'Registration-Activation Error (0015.111)'. Need license reactivation.", "Medium"),
    ("Google Chrome memory leak consuming 14GB RAM", "Chrome browser consumes all available system RAM after 3 hours of usage with only 6 tabs open, slowing the entire operating system to a crawl.", "Medium"),
    ("File compression utility producing corrupted archives", "7-Zip creates archives that fail CRC checksum validation when extracted on recipient workstations. Error: 'Data error in encrypted file'.", "Low"),
    ("Font rendering corrupted in presentation software", "PowerPoint slides are displaying garbled glyphs and overlapping letters instead of standard Arial fonts after the latest OS patch.", "Low"),
    ("Blue screen of death SYSTEM_SERVICE_EXCEPTION", "Receiving random BSODs twice daily pointing to win32kfull.sys during normal web browsing and word processing.", "Critical"),
    ("VPN client software fails to initialize virtual adapter", "GlobalProtect / OpenVPN agent displays 'Failed to create virtual network adapter' during startup sequence. Reinstalling network drivers did not help.", "High"),
    ("Text editor formatting tool breaks indentation", "VS Code auto-formatter replaces tabs with corrupted null characters in YAML configuration files, preventing deployment pipelines from running.", "Low")
]

NETWORK_TEMPLATES = [
    ("Corporate VPN disconnecting every 10 minutes", "Connected to the office VPN through Cisco AnyConnect, but the tunnel drops intermittently every 10 to 15 minutes with error: 'Connection terminated locally'.", "High"),
    ("Office WiFi connected but no internet access", "Laptops on the 4th floor connect to 'Corp-Secure-WiFi' with strong signal, but browser displays 'No Internet Access, DNS server not responding'.", "High"),
    ("DNS resolution failure for internal domains", "Cannot resolve internal domain portal.internal.company.com. Nslookup returns SERVFAIL from primary DNS server 10.0.0.2.", "High"),
    ("Slow network bandwidth and high packet loss", "Upload and download speeds on wired ethernet are capped under 2 Mbps instead of the Gigabit link. Ping tests show 35% packet loss to local gateway.", "High"),
    ("Firewall blocking outbound port 443 to cloud storage", "Requests to AWS S3 buckets and GitHub are timing out from our subnet. Security policy appears to be dropping outbound TCP traffic on port 443.", "Critical"),
    ("IP address conflict error on workstation", "Windows notification warning: 'Another computer on this network has the same IP address as this computer'. Network adapter disabled itself.", "Medium"),
    ("Cannot access shared network drive Z:", "File Explorer reports 'The network path was not found' when trying to open mapped network drive \\\\fileserver01\\finance. Other users can access it.", "Medium"),
    ("SSL certificate error visiting company intranet", "Web browsers display NET::ERR_CERT_COMMON_NAME_INVALID when accessing internal wiki. Certificate appears expired as of yesterday.", "High"),
    ("VoIP desk phone unregistered from PBX", "Cisco IP phone on desk 14 shows 'Registration Failed'. No dial tone and cannot receive incoming transfers from receptionist.", "Medium"),
    ("Guest WiFi captive portal not loading", "Visitors connecting to 'Guest-WiFi' do not get redirected to the terms & conditions login page, leaving them without web connectivity.", "Low"),
    ("Frequent dropped calls on Microsoft Teams", "Teams voice and video calls consistently stutter and disconnect with warning 'Your network is causing poor call quality'.", "Medium"),
    ("Router gateway unreachable on subnet 192.168.10.0", "Workstations on VLAN 10 cannot ping default gateway 192.168.10.1. Local switch interface shows orange amber blinking LED.", "Critical"),
    ("Proxy server authentication pop-up loop", "Browser continuously prompts for proxy credentials every time a new website is navigated, rejecting valid domain credentials.", "Medium"),
    ("High latency spike to Europe branch office", "Site-to-site IPsec VPN tunnel between US and EU offices experiencing 450ms latency, causing database replication delays.", "High"),
    ("Ethernet wall jack physically damaged", "RJ-45 wall port at cubicle 42 has broken pins inside. Patch cable will not click securely into place and link light does not turn on.", "Low")
]

ACCOUNT_TEMPLATES = [
    ("User account locked out after failed password attempts", "Entered incorrect password on Monday morning and now my domain account is locked out. Need admin to unlock in Active Directory so I can login.", "High"),
    ("Password reset link expired before use", "Requested a self-service password reset email, but clicking the token link gives error 'Reset token has expired'. Please send a fresh reset link.", "Medium"),
    ("Lost smartphone cannot receive MFA 2FA code", "Replaced my mobile phone over the weekend and no longer have access to Microsoft Authenticator app. Cannot complete 2FA verification to log in.", "High"),
    ("Unauthorized login attempt detected from foreign IP", "Received security alert email indicating a successful login attempt from an unknown device in Romania. Need immediate password reset and session purge.", "Critical"),
    ("Access denied permission required for marketing share", "Transferred to the Brand Marketing team but receive 'You do not have permission to view this directory' when opening the Marketing Google Drive / SharePoint.", "Medium"),
    ("Single Sign-On SSO authentication loop on Okta", "Clicking on Jira or Confluence through Okta dashboard redirects in an infinite loop back to the login portal without signing in.", "High"),
    ("Update official primary email address and alias", "My last name has legally changed. Please update my primary email address in Google Workspace / Exchange and create an alias for my previous name.", "Low"),
    ("New employee onboarding credentials not received", "New software engineer starts today but has not received their initial login credentials or temporary password for company email.", "High"),
    ("Role-based access escalation for database analyst", "Need read-only SELECT permissions granted on the production analytics replica database for quarterly compliance audit.", "Medium"),
    ("Account deactivated following departmental transfer", "My Active Directory account was accidentally marked as disabled during my transfer from Support to Engineering. Cannot access workstation.", "Critical"),
    ("Cannot update security challenge questions", "Account settings page throws error 500 when saving new security verification questions for password self-recovery.", "Low"),
    ("Guest contractor account extension required", "Contractor engagement for vendor QA has been extended by 30 days. Need their account expiration date extended in Active Directory.", "Medium"),
    ("Shared mailbox permission missing in Outlook", "Need 'Send As' and 'Read and Manage' permissions granted for shared mailbox info@company.com.", "Low"),
    ("Remove access for departing employee immediately", "Employee has resigned effective immediately today. Please disable AD account, revoke OAuth tokens, and forward emails to manager.", "Critical"),
    ("Session timeout too aggressive kicking out every 5 minutes", "Web portal logs me out every 5 minutes with 'Session Expired', forcing constant MFA re-authentication while working.", "Low")
]

PAYMENT_TEMPLATES = [
    ("Credit card charged twice for annual subscription", "Our company credit card was charged $1,200 twice on September 15th for the annual enterprise license. Please reverse the duplicate transaction.", "High"),
    ("Requesting official VAT invoice for tax filing", "Need an itemized PDF tax invoice containing our European VAT registration number (DE123456789) for our August subscription payment.", "Low"),
    ("Subscription renewal failed due to expired corporate card", "Received notification that our monthly SaaS subscription failed to renew because card ending in 4012 is expired. Need to update payment method.", "High"),
    ("Prorated refund request after seat reduction", "We downgraded our team plan from 50 seats to 25 seats at the beginning of the billing cycle. Requesting prorated credit or refund for unused seats.", "Medium"),
    ("Invoice shows incorrect billing address and company name", "The billing address on invoice INV-2026-0889 lists our old office address in London instead of our new headquarters in Manchester. Please reissue.", "Low"),
    ("Stripe checkout payment gateway throwing error 402", "When attempting to pay invoice online, checkout modal throws error 'Payment Required: card_declined'. Bank confirms no block on our end.", "High"),
    ("Unexpected price increase on monthly statement", "Our monthly subscription billed at $450 instead of our contracted rate of $350. Please review pricing tier agreement and adjust the balance.", "Medium"),
    ("Requesting W-9 vendor tax form for accounts payable", "Our accounting department requires a signed W-9 form and bank ACH direct deposit details before processing the outstanding purchase order.", "Low"),
    ("Subscription auto-renewed after cancellation notice", "Submitted cancellation request 10 days before renewal date, but our credit card was still charged $299 this morning. Requesting full cancellation and refund.", "High"),
    ("Billing currency incorrect charged in EUR instead of USD", "Our master services agreement stipulates USD billing, but latest charge came through as 499 EUR with high foreign exchange fees.", "Medium"),
    ("Purchase order PO number missing on invoice", "Our accounts payable system rejects invoices without PO-98432 printed on the document. Please add PO number and re-send PDF invoice.", "Low"),
    ("Bank wire transfer payment not reflected in account balance", "Wire transfer of $5,000 sent on Thursday with reference WT-4481. Account still shows overdue status and service suspension warning.", "Critical"),
    ("Failed charge penalty fee charged in error", "Account statement includes a $25 late payment penalty fee, but our automatic debit was authorized before the due date. Please waive fee.", "Low"),
    ("Need annual prepayment invoice for bulk discount", "We would like to switch from monthly billing to annual prepayment to take advantage of the 20% discount. Please generate the invoice.", "Medium"),
    ("Payment receipt not emailed after successful transaction", "Credit card was successfully charged yesterday but confirmation receipt and license key were not delivered to billing@company.com.", "Low")
]

TECHNICAL_ISSUE_TEMPLATES = [
    ("REST API returning HTTP 500 Internal Server Error", "Calls to endpoint /api/v2/orders/batch are consistently failing with HTTP 500 Internal Server Error. Response payload contains uncaught NullPointerException.", "Critical"),
    ("Database query connection timeout during peak hours", "Database connection pool exhausted on master MySQL cluster. Client applications receive 'OperationalError 2006: MySQL server has gone away'.", "Critical"),
    ("Webhook delivery failing with HTTP 404 response", "Webhook notifications for event 'ticket.resolved' fail with status 404 to our endpoint https://crm.company.com/webhook. Headers show missing HMAC signature.", "High"),
    ("Data export CSV corrupted with incomplete rows", "Exporting historical ticket reports with >10,000 rows generates truncated CSV file stopping midway at row 3,420 with trailing commas.", "Medium"),
    ("Background worker queue stalled and backlog growing", "Celery / Redis background task queue is not processing asynchronous email notification jobs. 15,000 tasks stuck in pending state.", "High"),
    ("Intermittent WebSocket connection drops in dashboard", "Real-time updates in admin portal disconnect with code 1006 every few minutes, requiring manual page refresh to see new tickets.", "Medium"),
    ("File upload API failing for files larger than 10MB", "Attempting to attach 15MB diagnostic logs throws '413 Request Entity Too Large' from reverse proxy Nginx configuration.", "Medium"),
    ("Database deadlock detected in transaction execution", "Deadlock found when trying to get lock on table Ticket_Comments during concurrent status update. Transaction was aborted by database engine.", "High"),
    ("Search query elasticsearch index synchronization lag", "Newly created tickets do not appear in search results for up to 45 minutes. Full-text search indexer seems to be lagging behind database binlog.", "Medium"),
    ("Automated nightly backup script exited with error code 1", "Scheduled mysqldump backup job failed at 02:00 AM due to disk space shortage on mount /var/backups. Backup archive is incomplete.", "Critical"),
    ("API rate limiting triggered incorrectly on internal services", "Internal microservice is receiving HTTP 429 Too Many Requests when communicating with the auth service on the local network.", "High"),
    ("Garbled UTF-8 character encoding in exported reports", "Exported customer names with accents or non-ASCII characters display as 'Ã©' instead of 'é' due to missing charset header in API response.", "Low"),
    ("Memory consumption on API container growing continuously", "Docker container memory usage rises from 200MB to 3.8GB over 48 hours without releasing, indicating a memory leak in the connection pool.", "High"),
    ("SSL handshake failure between microservices", "Service mesh communication failed with 'SSL: CERTIFICATE_VERIFY_FAILED: certificate has expired' between billing and user services.", "Critical"),
    ("Cron job for SLA breach calculation not triggering", "Scheduled cron task responsible for marking overdue tickets as 'SLA BREACHED' failed to execute for the last 6 hours.", "High")
]

# Variations to expand templates into diverse samples
CONTEXT_MODIFIERS = [
    "",
    " This issue started occurring after the system maintenance yesterday.",
    " Several other team members in our department are facing the exact same problem.",
    " We have already attempted rebooting the system, but the problem persists.",
    " This is severely impacting our daily operations and client deliverable deadlines.",
    " Please advise on immediate troubleshooting steps or dispatch a technician.",
    " We noticed this error intermittently over the past week, but now it occurs constantly.",
    " Urgent assistance required as this is blocking our production workflow.",
    " Logs and system diagnostic details have been captured and can be provided upon request.",
    " Tested across multiple workstations and the behavior is completely reproducible."
]

def generate_dataset(target_total=720):
    dataset_dir = Path(__file__).resolve().parent
    dataset_dir.mkdir(parents=True, exist_ok=True)
    csv_file = dataset_dir / "ticket_data.csv"

    categories = [
        ("Hardware", HARDWARE_TEMPLATES),
        ("Software", SOFTWARE_TEMPLATES),
        ("Network", NETWORK_TEMPLATES),
        ("Account", ACCOUNT_TEMPLATES),
        ("Payment", PAYMENT_TEMPLATES),
        ("Technical Issue", TECHNICAL_ISSUE_TEMPLATES)
    ]

    samples_per_category = target_total // len(categories)
    rows = []
    ticket_id = 1

    for cat_name, templates in categories:
        count = 0
        while count < samples_per_category:
            base_subj, base_desc, base_prio = random.choice(templates)
            modifier = random.choice(CONTEXT_MODIFIERS)

            # Slight subject variation
            subj_variants = [
                base_subj,
                f"Urgent: {base_subj}",
                f"[Issue] {base_subj}",
                f"Help needed: {base_subj}",
                f"{base_subj} - Request assistance"
            ]
            subj = random.choice(subj_variants)
            desc = base_desc + modifier

            # Priority jittering (mostly keep base priority, occasionally adjust slightly)
            prio = base_prio
            if "Critical" in desc or "dangerously" in desc or "burning" in desc or "deadlock" in desc:
                prio = "Critical"
            elif "immediately" in desc or "abruptly" in desc or "blocking" in desc:
                prio = "High" if prio != "Critical" else "Critical"

            combined_text = f"{subj}. {desc}"

            rows.append({
                'ticket_id': ticket_id,
                'subject': subj,
                'description': desc,
                'ticket_text': combined_text,
                'category': cat_name,
                'priority': prio
            })
            ticket_id += 1
            count += 1

    # Shuffle dataset
    random.shuffle(rows)
    for idx, r in enumerate(rows, start=1):
        r['ticket_id'] = idx

    # Write to CSV
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['ticket_id', 'subject', 'description', 'ticket_text', 'category', 'priority'])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} support tickets across {len(categories)} categories.")
    print(f"Dataset successfully saved to: {csv_file}")
    return csv_file

if __name__ == '__main__':
    generate_dataset()

