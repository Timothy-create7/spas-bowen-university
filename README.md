# Student Performance Analytics System (SPAS)
## Bowen University, Iwo — Dept. of Computer Science

### Quick Start
```bash
pip install -r requirements.txt
python app.py
```
Then open: http://localhost:5000

### Default Demo Account
- Email:    admin@bowen.edu.ng
- Password: admin123

### Features
- Login / Signup with role-based access (admin, lecturer, academic_officer)
- Student management (add, view, delete) with matric format BU22CSC1049
- Score entry: CA1 (max 15) + CA2 (max 15) + Exam (max 70) = 100
- Two semesters per session (e.g., 2024/2025 Semester 1 & 2)
- Auto-computed grades: A(70+), B(60+), C(50+), D(45+), E(40+), F(<40)
- Analytics: class average, pass rate, grade distribution, at-risk detection
- Course-level analysis with bar/doughnut charts
- Individual student performance profile with GPA per semester
- Persistent JSON database (db.json)

### File Structure
```
spas/
├── app.py            ← Flask backend (all APIs)
├── db.json           ← Auto-generated database
├── requirements.txt
└── templates/
    ├── auth.html     ← Login / Signup page
    └── dashboard.html← Main analytics dashboard
```
