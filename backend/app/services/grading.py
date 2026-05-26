def calculate_grade_and_gpa(marks, max_marks=100):
    percent = (marks / max_marks) * 100
    if percent >= 70:
        return 'A', 4.0
    elif percent >= 60:
        return 'B', 3.0
    elif percent >= 50:
        return 'C', 2.0
    elif percent >= 40:
        return 'D', 1.0
    else:
        return 'F', 0.0