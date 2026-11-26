
# Student ki learning difficulties detect karne ke liye function.
def detect_friction(student_activity):

    # Detected problems store karne ke liye empty list.
    friction_points = []

    # Student ki activity mein quiz score check karna.
    quiz_score = student_activity.get("quiz_score", 100)

    # Agar quiz score 50 se kam hai.
    if quiz_score < 50:

        # Low quiz performance ko learning difficulty maana jayega.
        friction_points.append("Low quiz performance")

    # Student ki repeated mistakes count karna.
    repeated_mistakes = student_activity.get("repeated_mistakes", 0)

    # Agar mistakes 3 ya usse zyada hain.
    if repeated_mistakes >= 3:

        # Repeated mistakes ko friction point mein add karna.
        friction_points.append("Repeated mistakes detected")

    # Student ki help requests count karna.
    help_requests = student_activity.get("help_requests", 0)

    # Agar student ne 5 ya usse zyada baar help maangi.
    if help_requests >= 5:

        # Frequent help requests ko difficulty maana jayega.
        friction_points.append("Frequent help requests")

    # Final detected difficulties return karna.
    return friction_points
