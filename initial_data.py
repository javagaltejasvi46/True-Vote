import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system.settings')
django.setup()

from polls.models import Branch, Department

# Create Branches
branches = [
    {'branch_name': 'Computer Science', 'branch_code': 'CS'},
    {'branch_name': 'Information Science', 'branch_code': 'IS'},
    {'branch_name': 'Electronics and Communication', 'branch_code': 'EC'},
    {'branch_name': 'Electrical Engineering', 'branch_code': 'EE'},
    {'branch_name': 'Mechanical Engineering', 'branch_code': 'ME'},
]

for branch_data in branches:
    Branch.objects.get_or_create(
        branch_name=branch_data['branch_name'],
        branch_code=branch_data['branch_code']
    )
    print(f"Added branch: {branch_data['branch_name']}")

# Create Departments
departments = [
    {'department_name': 'Technical', 'dept_id': 'TECH'},
    {'department_name': 'Cultural', 'dept_id': 'CULT'},
    {'department_name': 'Sports', 'dept_id': 'SPRT'},
    {'department_name': 'Management', 'dept_id': 'MGMT'},
    {'department_name': 'Academic', 'dept_id': 'ACAD'},
]

for dept_data in departments:
    Department.objects.get_or_create(
        department_name=dept_data['department_name'],
        dept_id=dept_data['dept_id']
    )
    print(f"Added department: {dept_data['department_name']}")

print("Initial data added successfully!") 