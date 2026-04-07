"""
NexDesk IT Ticket Dataset - 30 diverse tickets based on real IT helpdesk scenarios.
Each ticket has ground truth for grading all tasks.
"""

TICKETS = [
    {
        "id": "TKT-001",
        "subject": "Cannot connect to the internet",
        "description": (
            "My laptop suddenly stopped connecting to the internet this morning. "
            "I've tried restarting the machine and the router but nothing works. "
            "I have a client presentation in 30 minutes and urgently need access. "
            "All my colleagues on the same floor seem fine."
        ),
        "submitter": "Sarah Johnson",
        "department": "Marketing",
        "submitted_at": "2025-04-07T09:15:00Z",
        "gt_priority": "high",
        "gt_priority_ok": ["critical"],
        "gt_category": "network",
        "gt_category_ok": [],
        "gt_team": "network-ops",
        "gt_team_ok": ["helpdesk"],
        "gt_affected_system": "laptop",
        "gt_sla_hours": 4,
        "gt_keywords_response": ["apologies", "looking into", "priorit", "urgent", "presentation"],
        "gt_keywords_resolution": [
            "wifi",
            "driver",
            "ip",
            "dhcp",
            "network adapter",
            "cable",
            "ethernet",
            "reconnect",
        ],
    },
    {
        "id": "TKT-005",
        "subject": "PRODUCTION SERVER DOWN — all services offline",
        "description": (
            "URGENT: Our primary production web server (prod-web-01) went offline at 09:42. "
            "All customer-facing services are down. 500 errors on all endpoints. "
            "Revenue impact is approximately $12,000 per minute. On-call engineer pinged."
        ),
        "submitter": "Arjun Mehta",
        "department": "Engineering",
        "submitted_at": "2025-04-07T09:45:00Z",
        "gt_priority": "critical",
        "gt_priority_ok": [],
        "gt_category": "network",
        "gt_category_ok": ["software"],
        "gt_team": "network-ops",
        "gt_team_ok": ["sysadmin", "dev"],
        "gt_affected_system": "prod-web-01",
        "gt_sla_hours": 1,
        "gt_keywords_response": [
            "escalat",
            "on-call",
            "incident",
            "war room",
            "immediate",
            "critical",
        ],
        "gt_keywords_resolution": [
            "restart",
            "failover",
            "load balancer",
            "logs",
            "rollback",
            "health check",
            "monitoring",
        ],
    },
    {
        "id": "TKT-010",
        "subject": "VPN disconnects every 5 minutes while working from home",
        "description": (
            "I've been working from home this week and my VPN keeps dropping every 5 minutes. "
            "I have to manually reconnect every time. This is disrupting calls and access to internal tools. "
            "Using OpenVPN on Windows 10. My home internet seems fine for everything else."
        ),
        "submitter": "Fatima Al-Hassan",
        "department": "Legal",
        "submitted_at": "2025-04-07T13:00:00Z",
        "gt_priority": "medium",
        "gt_priority_ok": ["high"],
        "gt_category": "network",
        "gt_category_ok": ["software"],
        "gt_team": "network-ops",
        "gt_team_ok": ["helpdesk", "sysadmin"],
        "gt_affected_system": "VPN",
        "gt_sla_hours": 8,
        "gt_keywords_response": ["looking into", "vpn", "reconnect", "investigate", "remote"],
        "gt_keywords_resolution": [
            "openvpn",
            "config",
            "keepalive",
            "timeout",
            "split tunnel",
            "logs",
            "reinstall",
        ],
    },
    {
        "id": "TKT-011",
        "subject": "Entire Sales floor has no network - 50+ people affected",
        "description": (
            "The entire 4th floor (Sales department) lost network connectivity about 20 minutes ago. "
            "Both wired and wireless are down. We have quarter-end calls happening NOW. "
            "This is affecting 50+ sales reps and potentially millions in deals."
        ),
        "submitter": "Marcus Chen",
        "department": "Sales",
        "submitted_at": "2025-04-07T14:30:00Z",
        "gt_priority": "critical",
        "gt_priority_ok": [],
        "gt_category": "network",
        "gt_category_ok": [],
        "gt_team": "network-ops",
        "gt_team_ok": [],
        "gt_affected_system": "floor 4 network",
        "gt_sla_hours": 1,
        "gt_keywords_response": ["immediately", "dispatch", "floor 4", "priority", "escalat"],
        "gt_keywords_resolution": ["switch", "router", "cable", "port", "vlan", "network closet"],
    },
    # SOFTWARE ISSUES
    {
        "id": "TKT-002",
        "subject": "Request to install Figma on design workstation",
        "description": (
            "Hi team, I would like to request installation of Figma Desktop on my workstation. "
            "I will be using it for UI/UX design work starting next week. "
            "My machine is Windows 11, asset tag WS-4421. No rush on this one."
        ),
        "submitter": "Priya Nair",
        "department": "Design",
        "submitted_at": "2025-04-07T10:00:00Z",
        "gt_priority": "low",
        "gt_priority_ok": ["medium"],
        "gt_category": "software",
        "gt_category_ok": [],
        "gt_team": "helpdesk",
        "gt_team_ok": ["sysadmin"],
        "gt_affected_system": "workstation",
        "gt_sla_hours": 48,
        "gt_keywords_response": ["received", "schedule", "install", "approved", "request"],
        "gt_keywords_resolution": [
            "download",
            "install",
            "admin",
            "license",
            "deploy",
            "software center",
        ],
    },
    {
        "id": "TKT-008",
        "subject": "Database queries extremely slow — affecting all users",
        "description": (
            "Since this morning our CRM database has been responding very slowly. "
            "Simple queries that normally take <1s are now taking 45-60 seconds. "
            "All 200 sales reps are affected. We suspect a missing index or a locked table."
        ),
        "submitter": "Carlos Mendez",
        "department": "Engineering",
        "submitted_at": "2025-04-07T10:15:00Z",
        "gt_priority": "high",
        "gt_priority_ok": ["critical"],
        "gt_category": "software",
        "gt_category_ok": [],
        "gt_team": "dev",
        "gt_team_ok": ["sysadmin", "network-ops"],
        "gt_affected_system": "CRM database",
        "gt_sla_hours": 4,
        "gt_keywords_response": ["investigating", "database", "performance", "team", "priority"],
        "gt_keywords_resolution": [
            "index",
            "query plan",
            "lock",
            "vacuum",
            "slow query log",
            "optimize",
            "dba",
        ],
    },
    {
        "id": "TKT-012",
        "subject": "Excel keeps crashing when opening large files",
        "description": (
            "Every time I try to open our quarterly financial model (about 50MB), Excel crashes. "
            "I've tried restarting my computer. Other smaller files open fine. "
            "I need this for the board meeting tomorrow morning."
        ),
        "submitter": "Jennifer Wu",
        "department": "Finance",
        "submitted_at": "2025-04-07T16:00:00Z",
        "gt_priority": "high",
        "gt_priority_ok": ["medium"],
        "gt_category": "software",
        "gt_category_ok": [],
        "gt_team": "helpdesk",
        "gt_team_ok": ["sysadmin"],
        "gt_affected_system": "Excel",
        "gt_sla_hours": 4,
        "gt_keywords_response": ["understand", "board meeting", "priority", "help"],
        "gt_keywords_resolution": [
            "memory",
            "ram",
            "repair",
            "update",
            "safe mode",
            "add-ins",
            "64-bit",
        ],
    },
    {
        "id": "TKT-013",
        "subject": "Zoom audio not working in meetings",
        "description": (
            "For the past 3 days, my audio doesn't work in Zoom meetings. "
            "I can see everyone but can't hear them and they can't hear me. "
            "I've checked my microphone settings and they look correct. "
            "Using the Zoom desktop app on macOS."
        ),
        "submitter": "David Okonkwo",
        "department": "Customer Success",
        "submitted_at": "2025-04-07T11:30:00Z",
        "gt_priority": "medium",
        "gt_priority_ok": ["high"],
        "gt_category": "software",
        "gt_category_ok": ["hardware"],
        "gt_team": "helpdesk",
        "gt_team_ok": [],
        "gt_affected_system": "Zoom",
        "gt_sla_hours": 8,
        "gt_keywords_response": ["audio", "troubleshoot", "help", "meeting"],
        "gt_keywords_resolution": [
            "permissions",
            "microphone",
            "speaker",
            "reinstall",
            "audio settings",
            "system preferences",
        ],
    },
    # HARDWARE ISSUES
    {
        "id": "TKT-004",
        "subject": "Mouse completely unresponsive",
        "description": (
            "My wireless mouse stopped working. I replaced the battery but it's still dead. "
            "I have a spare trackpad I can use temporarily, but please send a replacement mouse."
        ),
        "submitter": "Liu Wei",
        "department": "Finance",
        "submitted_at": "2025-04-07T11:20:00Z",
        "gt_priority": "low",
        "gt_priority_ok": ["medium"],
        "gt_category": "hardware",
        "gt_category_ok": [],
        "gt_team": "helpdesk",
        "gt_team_ok": [],
        "gt_affected_system": "mouse",
        "gt_sla_hours": 24,
        "gt_keywords_response": ["replacement", "send", "pickup", "collect", "trackpad"],
        "gt_keywords_resolution": [
            "replacement",
            "new mouse",
            "inventory",
            "asset",
            "deliver",
            "usb receiver",
        ],
    },
    {
        "id": "TKT-007",
        "subject": "Office printer on Floor 3 offline for entire floor",
        "description": (
            "The HP LaserJet printer shared by all 40 users on Floor 3 has been offline since 8am. "
            "Error light is blinking red. We have an audit report due today that needs to be printed."
        ),
        "submitter": "Ananya Krishnan",
        "department": "Operations",
        "submitted_at": "2025-04-07T09:30:00Z",
        "gt_priority": "high",
        "gt_priority_ok": ["medium"],
        "gt_category": "hardware",
        "gt_category_ok": [],
        "gt_team": "helpdesk",
        "gt_team_ok": ["sysadmin"],
        "gt_affected_system": "printer",
        "gt_sla_hours": 4,
        "gt_keywords_response": ["dispatch", "technician", "floor 3", "printer", "audit"],
        "gt_keywords_resolution": [
            "paper jam",
            "toner",
            "driver",
            "restart",
            "cable",
            "firmware",
            "network printer",
        ],
    },
    {
        "id": "TKT-009",
        "subject": "New employee needs laptop setup",
        "description": (
            "We have a new hire starting Monday — Ravi Shankar, joining as a Junior Developer. "
            "He will need a MacBook Pro with developer tools: VS Code, Docker, Git, and VPN access."
        ),
        "submitter": "HR Team",
        "department": "HR",
        "submitted_at": "2025-04-07T12:00:00Z",
        "gt_priority": "medium",
        "gt_priority_ok": ["low"],
        "gt_category": "hardware",
        "gt_category_ok": ["software", "access"],
        "gt_team": "sysadmin",
        "gt_team_ok": ["helpdesk"],
        "gt_affected_system": "laptop",
        "gt_sla_hours": 24,
        "gt_keywords_response": ["prepare", "ready", "monday", "setup", "onboard"],
        "gt_keywords_resolution": [
            "macbook",
            "provision",
            "image",
            "vs code",
            "docker",
            "git",
            "vpn",
            "onboard",
        ],
    },
    {
        "id": "TKT-014",
        "subject": "Laptop screen flickering constantly",
        "description": (
            "My laptop screen has been flickering for the past hour. It's giving me a headache. "
            "Sometimes it goes completely black for a second. ThinkPad X1 Carbon, about 2 years old."
        ),
        "submitter": "Emma Thompson",
        "department": "Marketing",
        "submitted_at": "2025-04-07T15:00:00Z",
        "gt_priority": "medium",
        "gt_priority_ok": ["high"],
        "gt_category": "hardware",
        "gt_category_ok": [],
        "gt_team": "helpdesk",
        "gt_team_ok": [],
        "gt_affected_system": "laptop screen",
        "gt_sla_hours": 8,
        "gt_keywords_response": ["sorry", "headache", "diagnose", "help"],
        "gt_keywords_resolution": [
            "display driver",
            "refresh rate",
            "cable",
            "gpu",
            "external monitor",
            "replacement",
        ],
    },
    {
        "id": "TKT-015",
        "subject": "Conference room projector showing no signal",
        "description": (
            "The projector in Conference Room B is showing 'No Signal' even though the laptop is connected. "
            "We have an important client meeting in 45 minutes. Tried different HDMI cables already."
        ),
        "submitter": "Robert Kim",
        "department": "Sales",
        "submitted_at": "2025-04-07T13:15:00Z",
        "gt_priority": "high",
        "gt_priority_ok": ["critical"],
        "gt_category": "hardware",
        "gt_category_ok": [],
        "gt_team": "helpdesk",
        "gt_team_ok": [],
        "gt_affected_system": "projector",
        "gt_sla_hours": 1,
        "gt_keywords_response": ["client meeting", "immediately", "send", "help"],
        "gt_keywords_resolution": [
            "input source",
            "display settings",
            "extend",
            "duplicate",
            "resolution",
            "adapter",
        ],
    },
    # ACCESS ISSUES
    {
        "id": "TKT-003",
        "subject": "Forgot password — locked out of email",
        "description": (
            "I cannot log into my company email. I think I mistyped my password too many times "
            "and now the account is locked. I need access to email for a meeting in 2 hours."
        ),
        "submitter": "James Okafor",
        "department": "Sales",
        "submitted_at": "2025-04-07T08:45:00Z",
        "gt_priority": "medium",
        "gt_priority_ok": ["high"],
        "gt_category": "access",
        "gt_category_ok": [],
        "gt_team": "helpdesk",
        "gt_team_ok": ["sysadmin"],
        "gt_affected_system": "email",
        "gt_sla_hours": 2,
        "gt_keywords_response": ["reset", "unlock", "password", "identity", "meeting"],
        "gt_keywords_resolution": [
            "active directory",
            "password reset",
            "mfa",
            "unlock account",
            "verify identity",
        ],
    },
    {
        "id": "TKT-016",
        "subject": "Need access to shared drive for new project",
        "description": (
            "I've been assigned to the Falcon project but I can't access the shared drive at "
            "\\\\fileserver\\projects\\falcon. I get 'Access Denied'. My manager is Tom Bradley."
        ),
        "submitter": "Aisha Patel",
        "department": "Engineering",
        "submitted_at": "2025-04-07T09:00:00Z",
        "gt_priority": "medium",
        "gt_priority_ok": ["low"],
        "gt_category": "access",
        "gt_category_ok": [],
        "gt_team": "sysadmin",
        "gt_team_ok": ["helpdesk"],
        "gt_affected_system": "shared drive",
        "gt_sla_hours": 8,
        "gt_keywords_response": ["access", "manager", "approval", "verify"],
        "gt_keywords_resolution": [
            "permissions",
            "ad group",
            "security group",
            "file server",
            "acl",
        ],
    },
    {
        "id": "TKT-017",
        "subject": "Can't login to Salesforce - says account disabled",
        "description": (
            "When I try to login to Salesforce, it says my account has been disabled. "
            "I haven't changed anything and was using it fine yesterday. "
            "I have client calls scheduled all day that need CRM access."
        ),
        "submitter": "Michael Santos",
        "department": "Sales",
        "submitted_at": "2025-04-07T08:30:00Z",
        "gt_priority": "high",
        "gt_priority_ok": ["critical"],
        "gt_category": "access",
        "gt_category_ok": ["software"],
        "gt_team": "sysadmin",
        "gt_team_ok": ["helpdesk"],
        "gt_affected_system": "Salesforce",
        "gt_sla_hours": 2,
        "gt_keywords_response": ["urgent", "investigating", "client calls", "priority"],
        "gt_keywords_resolution": ["reactivate", "admin", "license", "sso", "provisioning"],
    },
    {
        "id": "TKT-018",
        "subject": "MFA not sending codes to my phone",
        "description": (
            "I'm trying to login but the MFA code never arrives on my phone. "
            "I've waited 10 minutes and tried 5 times. My phone number is correct in the system. "
            "Stuck outside the office and can't do anything without access."
        ),
        "submitter": "Rachel Green",
        "department": "HR",
        "submitted_at": "2025-04-07T07:45:00Z",
        "gt_priority": "high",
        "gt_priority_ok": ["medium"],
        "gt_category": "access",
        "gt_category_ok": ["security"],
        "gt_team": "helpdesk",
        "gt_team_ok": ["security"],
        "gt_affected_system": "MFA",
        "gt_sla_hours": 2,
        "gt_keywords_response": ["understand", "frustrating", "help", "verify"],
        "gt_keywords_resolution": [
            "backup codes",
            "authenticator app",
            "reset mfa",
            "phone number",
            "sms",
        ],
    },
    # SECURITY ISSUES
    {
        "id": "TKT-006",
        "subject": "Suspicious login attempts on admin account",
        "description": (
            "Our SIEM has flagged 47 failed login attempts on the admin@company.com account "
            "in the last 10 minutes from IP 185.220.101.x (Tor exit node). "
            "Account is currently active. No successful logins yet but this is serious."
        ),
        "submitter": "Elena Vasquez",
        "department": "IT Security",
        "submitted_at": "2025-04-07T14:30:00Z",
        "gt_priority": "critical",
        "gt_priority_ok": [],
        "gt_category": "security",
        "gt_category_ok": [],
        "gt_team": "security",
        "gt_team_ok": [],
        "gt_affected_system": "admin account",
        "gt_sla_hours": 1,
        "gt_keywords_response": [
            "lock",
            "disable",
            "investigat",
            "block",
            "incident",
            "immediately",
        ],
        "gt_keywords_resolution": [
            "disable account",
            "block ip",
            "mfa",
            "audit logs",
            "forensic",
            "incident response",
        ],
    },
    {
        "id": "TKT-019",
        "subject": "Phishing email reported - many employees received it",
        "description": (
            "Multiple employees (at least 20) received an email claiming to be from IT "
            "asking them to 'verify their password' via a suspicious link. "
            "Some people may have already clicked. Subject was 'Urgent: Password Expiry Notice'."
        ),
        "submitter": "IT Security Team",
        "department": "IT Security",
        "submitted_at": "2025-04-07T11:00:00Z",
        "gt_priority": "critical",
        "gt_priority_ok": [],
        "gt_category": "security",
        "gt_category_ok": [],
        "gt_team": "security",
        "gt_team_ok": [],
        "gt_affected_system": "email",
        "gt_sla_hours": 1,
        "gt_keywords_response": ["block", "warn", "all-staff", "do not click", "immediate"],
        "gt_keywords_resolution": [
            "block sender",
            "quarantine",
            "force password reset",
            "awareness",
            "compromised",
        ],
    },
    {
        "id": "TKT-020",
        "subject": "Found USB drive in parking lot - is it safe?",
        "description": (
            "I found a USB drive in the parking lot with our company logo on it. "
            "Should I plug it in to see what's on it? It might belong to someone."
        ),
        "submitter": "Alex Turner",
        "department": "Marketing",
        "submitted_at": "2025-04-07T12:30:00Z",
        "gt_priority": "medium",
        "gt_priority_ok": ["high"],
        "gt_category": "security",
        "gt_category_ok": [],
        "gt_team": "security",
        "gt_team_ok": ["helpdesk"],
        "gt_affected_system": "USB device",
        "gt_sla_hours": 4,
        "gt_keywords_response": ["DO NOT plug in", "bring to IT", "security risk", "thank you"],
        "gt_keywords_resolution": ["air-gapped", "scan", "malware", "baiting attack", "dispose"],
    },
    {
        "id": "TKT-021",
        "subject": "Laptop stolen from car - contains sensitive data",
        "description": (
            "My work laptop was stolen from my car last night. It has client contracts and "
            "financial data on it. The laptop was password-protected but not encrypted (I think). "
            "Serial number is LT-8834."
        ),
        "submitter": "Nicole Foster",
        "department": "Legal",
        "submitted_at": "2025-04-07T07:00:00Z",
        "gt_priority": "critical",
        "gt_priority_ok": [],
        "gt_category": "security",
        "gt_category_ok": [],
        "gt_team": "security",
        "gt_team_ok": ["sysadmin"],
        "gt_affected_system": "laptop",
        "gt_sla_hours": 1,
        "gt_keywords_response": ["remote wipe", "report", "police", "disable", "immediately"],
        "gt_keywords_resolution": [
            "remote wipe",
            "revoke credentials",
            "bitlocker",
            "mdm",
            "incident report",
            "breach notification",
        ],
    },
    # OTHER/EDGE CASES
    {
        "id": "TKT-022",
        "subject": "How do I use the new expense reporting system?",
        "description": (
            "I need to submit my travel expenses from last week but I don't know how to use "
            "the new Concur system. Is there a guide or can someone show me?"
        ),
        "submitter": "Patricia Williams",
        "department": "Finance",
        "submitted_at": "2025-04-07T14:00:00Z",
        "gt_priority": "low",
        "gt_priority_ok": [],
        "gt_category": "other",
        "gt_category_ok": ["software"],
        "gt_team": "helpdesk",
        "gt_team_ok": [],
        "gt_affected_system": "Concur",
        "gt_sla_hours": 48,
        "gt_keywords_response": ["guide", "documentation", "help", "training"],
        "gt_keywords_resolution": [
            "user guide",
            "knowledge base",
            "training video",
            "walk through",
        ],
    },
    {
        "id": "TKT-023",
        "subject": "Office too cold - thermostat issue?",
        "description": (
            "The temperature in the East Wing has been freezing for 3 days now. "
            "Multiple people are wearing coats at their desks. Is this an IT thing or facilities?"
        ),
        "submitter": "Chris Anderson",
        "department": "Engineering",
        "submitted_at": "2025-04-07T10:30:00Z",
        "gt_priority": "low",
        "gt_priority_ok": [],
        "gt_category": "other",
        "gt_category_ok": ["hardware"],
        "gt_team": "helpdesk",
        "gt_team_ok": [],
        "gt_affected_system": "thermostat",
        "gt_sla_hours": 24,
        "gt_keywords_response": ["facilities", "building management", "forward", "sorry"],
        "gt_keywords_resolution": ["facilities", "hvac", "building ops", "redirect", "not IT"],
    },
    {
        "id": "TKT-024",
        "subject": "Need to schedule a demo of new collaboration tool",
        "description": (
            "The IT team mentioned a new project management tool at the all-hands. "
            "How can my team get a demo? We're currently using spreadsheets and it's chaos."
        ),
        "submitter": "Sandra Lee",
        "department": "Operations",
        "submitted_at": "2025-04-07T15:30:00Z",
        "gt_priority": "low",
        "gt_priority_ok": [],
        "gt_category": "other",
        "gt_category_ok": ["software"],
        "gt_team": "helpdesk",
        "gt_team_ok": [],
        "gt_affected_system": "project management tool",
        "gt_sla_hours": 72,
        "gt_keywords_response": ["demo", "schedule", "contact", "team"],
        "gt_keywords_resolution": ["calendar", "demo session", "product team", "pilot"],
    },
    {
        "id": "TKT-025",
        "subject": "Something weird on my screen - looks like a virus?",
        "description": (
            "There's a strange popup that keeps appearing saying I've won a prize. "
            "I didn't click on anything weird (I think). Should I be worried? "
            "The popup won't close when I click X."
        ),
        "submitter": "Kevin O'Brien",
        "department": "Sales",
        "submitted_at": "2025-04-07T16:30:00Z",
        "gt_priority": "high",
        "gt_priority_ok": ["medium"],
        "gt_category": "security",
        "gt_category_ok": ["software"],
        "gt_team": "security",
        "gt_team_ok": ["helpdesk"],
        "gt_affected_system": "workstation",
        "gt_sla_hours": 2,
        "gt_keywords_response": ["disconnect", "don't click", "coming to help", "scan"],
        "gt_keywords_resolution": [
            "malware scan",
            "adware",
            "browser extension",
            "quarantine",
            "reimage",
        ],
    },
    # MESSY/INFORMAL TICKETS
    {
        "id": "TKT-026",
        "subject": "HELP!!!! computre wont turn on at ALL",
        "description": (
            "ok so i come in this morning and my computer is just DEAD. like completely dead. "
            "no lights no nothing. i tried unplugging it and pluging it back in (isnt that what "
            "ur supposed to do??) but still nothing. i have a huge deadline today pleeease help "
            "asap!!! its the dell one btw"
        ),
        "submitter": "Brittany Miller",
        "department": "Marketing",
        "submitted_at": "2025-04-07T08:02:00Z",
        "gt_priority": "high",
        "gt_priority_ok": ["medium"],
        "gt_category": "hardware",
        "gt_category_ok": [],
        "gt_team": "helpdesk",
        "gt_team_ok": [],
        "gt_affected_system": "desktop computer",
        "gt_sla_hours": 4,
        "gt_keywords_response": ["understand", "urgent", "deadline", "check", "power"],
        "gt_keywords_resolution": [
            "power supply",
            "power cable",
            "outlet",
            "surge protector",
            "psu",
            "motherboard",
        ],
    },
    {
        "id": "TKT-027",
        "subject": "slack is being weird again :/",
        "description": (
            "heyyy so slack keeps showing me msgs from like 3 days ago as 'new'?? and some "
            "channels wont load at all they just spin forever lol. also the emoji reactions "
            "are super laggy. restarted the app twice already. macbook if that matters. thx!"
        ),
        "submitter": "Jake Hernandez",
        "department": "Design",
        "submitted_at": "2025-04-07T10:45:00Z",
        "gt_priority": "low",
        "gt_priority_ok": ["medium"],
        "gt_category": "software",
        "gt_category_ok": [],
        "gt_team": "helpdesk",
        "gt_team_ok": [],
        "gt_affected_system": "Slack",
        "gt_sla_hours": 24,
        "gt_keywords_response": ["troubleshoot", "cache", "reinstall", "help"],
        "gt_keywords_resolution": [
            "clear cache",
            "reinstall",
            "workspace",
            "sync",
            "update",
            "web version",
        ],
    },
    {
        "id": "TKT-028",
        "subject": "umm i think i deleted something important??",
        "description": (
            "so dont be mad but i was cleaning up my downloads folder and i mightve accidentally "
            "deleted the Q3 financal report?? its not in the recycle bin either idk where it went. "
            "is there like a backup or something?? my manager is gonna kill me pls respond fast"
        ),
        "submitter": "Tyler Washington",
        "department": "Finance",
        "submitted_at": "2025-04-07T14:22:00Z",
        "gt_priority": "high",
        "gt_priority_ok": ["critical"],
        "gt_category": "software",
        "gt_category_ok": ["other"],
        "gt_team": "sysadmin",
        "gt_team_ok": ["helpdesk"],
        "gt_affected_system": "file system",
        "gt_sla_hours": 4,
        "gt_keywords_response": ["don't worry", "backup", "recover", "help", "check"],
        "gt_keywords_resolution": [
            "backup",
            "shadow copy",
            "restore",
            "previous version",
            "recuva",
            "onedrive",
        ],
    },
    {
        "id": "TKT-029",
        "subject": "RE: FWD: urgent loign issue (3rd time submiting this!!!)",
        "description": (
            "THIS IS THE THIRD TICKET IVE SUBMITTED ABOUT THIS!!!! Nobody has helped me yet!!! "
            "I CANNOT LOG INTO THE HR PORTAL. it keeps saying invalid credentails but im 100% "
            "typing it right. i need to submit my timesheet by end of day or i wont get paid. "
            "this is ridculous. pls escalate to someone who can actually help. "
            "- sent from my iphone"
        ),
        "submitter": "Karen Fischer",
        "department": "Operations",
        "submitted_at": "2025-04-07T16:55:00Z",
        "gt_priority": "high",
        "gt_priority_ok": ["medium"],
        "gt_category": "access",
        "gt_category_ok": [],
        "gt_team": "helpdesk",
        "gt_team_ok": ["sysadmin"],
        "gt_affected_system": "HR portal",
        "gt_sla_hours": 2,
        "gt_keywords_response": ["apolog", "priority", "timesheet", "help", "escalate"],
        "gt_keywords_resolution": [
            "password reset",
            "caps lock",
            "account unlock",
            "clear browser",
            "cookies",
        ],
    },
    {
        "id": "TKT-030",
        "subject": "wifi suuuucks in the break room",
        "description": (
            "not sure if this is even an IT thing but the wifi in the break room is soooo bad. "
            "like i cant even load instagram on my lunch break lmao. the signal drops to like 1 bar "
            "as soon as u walk in there. other ppl have complained too. can we get a wifi extender "
            "or something?? also the microwave might be interfering idk im not a tech person haha"
        ),
        "submitter": "Zoe Martinez",
        "department": "Customer Success",
        "submitted_at": "2025-04-07T12:15:00Z",
        "gt_priority": "low",
        "gt_priority_ok": [],
        "gt_category": "network",
        "gt_category_ok": [],
        "gt_team": "network-ops",
        "gt_team_ok": ["helpdesk"],
        "gt_affected_system": "wifi",
        "gt_sla_hours": 72,
        "gt_keywords_response": ["look into", "break room", "coverage", "thanks"],
        "gt_keywords_resolution": [
            "access point",
            "wifi extender",
            "site survey",
            "interference",
            "channel",
            "2.4ghz",
        ],
    },
]
