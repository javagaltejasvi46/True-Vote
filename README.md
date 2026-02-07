# True Vote - Online Voting System

> [!WARNING]
> **Migration Notice**: This project was originally hosted on the **Tejasvijavagal** GitHub profile. Due to the account being flagged under unknown circumstances, the project codebase has been migrated to this new repository: [https://github.com/javagaltejasvi46/True-Vote.git](https://github.com/javagaltejasvi46/True-Vote.git).

## Project Overview
**True Vote** is a secure and efficient online voting system built using Django. It is designed to manage and conduct elections within educational institutions, supporting multiple departments and branches. The system allows for role-based access where users can register as voters or candidates, and administrators can manage the entire election process.

## Key Features

### 🔐 authentication & Authorization
- **Secure Login/Registration**: User account creation with secure password handling.
- **Role-Based Access Control (RBAC)**: Distinct roles for Voters, Candidates, and Administrators (Staff).
- **Voter Verification**: Unique SRN (Student Registration Number) tracking to ensure legitimate voters.

### 🗳️ Election Management
- **Create & Manage Elections**: Admins can create polls for specific departments (e.g., Cultural, Technical, President).
- **Candidate Management**: detailed profiles for candidates including position, age, and manifesto.
- **Department & Branch Isolation**: Elections can be filtered or categorized by specific branches (CS, IS, EC, etc.) and departments.
- **Auto-Archiving**: Past elections are automatically archived based on the publication date.

### 📊 Voting & Results
- **One Voter, One Vote**: Strict enforcement to prevent double voting in the same election.
- **Real-Time Analytics**: Visual charts and graphs showing vote distribution and participation rates.
- **Live Results**: Voters can view results immediately after casting their vote.
- **Audit Logs**: Timestamps for every vote cast.

## Technology Stack
- **Backend**: Python, Django 5.0.2
- **Database**: SQLite (Development)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Bootstrap / Custom CSS

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/javagaltejasvi46/True-Vote.git
   cd True-Vote
   ```

2. **Create Verification Environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python manage.py migrate
   python initial_data.py  # Seeds departments and branches
   ```

5. **Create Admin User**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Server**
   ```bash
   python manage.py runserver
   ```
   Access the app at `http://127.0.0.1:8000/`.

## Usage
- **Admin Panel**: Visit `/admin` to manage users, polls, and system data.
- **Voter Registration**: Verification required via SRN during signup.
- **Voting**: Navigate to the homepage to see active elections.

## Deployment
**Live Demo**: [Hugging Face Space](https://huggingface.co/spaces/tejasvijavagal/TrueVote)

For instructions on how to deploy this project to the web, please read [DEPLOYMENT.md](DEPLOYMENT.md).

---
*Maintained by Javagal Tejasvi*
