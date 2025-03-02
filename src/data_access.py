from db_utils import execute_query, execute_query_single

# User functions
def get_user_by_phone(phone_number):
    """Get a user by phone number"""
    query = "SELECT * FROM users WHERE phone_number = %s"
    return execute_query_single(query, (phone_number,))

def create_user(phone_number, unit_id=None, user_type='resident', staff_role=None):
    """Create a new user"""
    query = """
    INSERT INTO users (phone_number, unit_id, user_type, staff_role)
    VALUES (%s, %s, %s, %s)
    RETURNING *
    """
    params = (phone_number, unit_id, user_type, staff_role)
    return execute_query_single(query, params, commit=True)

def update_user(user_id, **kwargs):
    """Update user properties"""
    allowed_fields = ['unit_id', 'user_type', 'staff_role', 'is_active']
    field_updates = []
    params = []
    
    for field, value in kwargs.items():
        if field in allowed_fields:
            field_updates.append(f"{field} = %s")
            params.append(value)
    
    if not field_updates:
        return None
    
    query = f"""
    UPDATE users
    SET {", ".join(field_updates)}
    WHERE id = %s
    RETURNING *
    """
    params.append(user_id)
    return execute_query_single(query, params, commit=True)

# Unit functions
def get_unit_by_number(unit_number):
    """Get a unit by unit number"""
    query = "SELECT * FROM units WHERE unit_number = %s"
    return execute_query_single(query, (unit_number,))

def create_unit(unit_number):
    """Create a new unit"""
    query = """
    INSERT INTO units (unit_number)
    VALUES (%s)
    RETURNING *
    """
    return execute_query_single(query, (unit_number,), commit=True)

def get_users_in_unit(unit_id):
    """Get all users in a unit"""
    query = "SELECT * FROM users WHERE unit_id = %s"
    return execute_query(query, (unit_id,))

# Facility functions
def get_all_facilities():
    """Get all facilities"""
    query = "SELECT * FROM facilities"
    return execute_query(query)

def create_facility(name, description=None, max_concurrent_bookings=1, 
                   booking_limit_type=None, booking_limit_count=None, 
                   unit_booking_limit=None):
    """Create a new facility"""
    query = """
    INSERT INTO facilities 
    (name, description, max_concurrent_bookings, booking_limit_type, 
     booking_limit_count, unit_booking_limit)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING *
    """
    params = (name, description, max_concurrent_bookings, booking_limit_type, 
              booking_limit_count, unit_booking_limit)
    return execute_query_single(query, params, commit=True)

# Booking functions
def create_booking(facility_id, user_id, unit_id, start_time, end_time):
    """Create a facility booking"""
    query = """
    INSERT INTO bookings
    (facility_id, user_id, unit_id, start_time, end_time)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING *
    """
    params = (facility_id, user_id, unit_id, start_time, end_time)
    return execute_query_single(query, params, commit=True)

def get_bookings_by_unit(unit_id):
    """Get all bookings for a unit"""
    query = """
    SELECT b.*, f.name as facility_name
    FROM bookings b
    JOIN facilities f ON b.facility_id = f.id
    WHERE b.unit_id = %s
    ORDER BY b.start_time DESC
    """
    return execute_query(query, (unit_id,))

def check_facility_availability(facility_id, start_time, end_time):
    """Check if a facility is available for booking"""
    query = """
    SELECT COUNT(*) as booking_count
    FROM bookings
    WHERE facility_id = %s
    AND status = 'confirmed'
    AND (
        (start_time <= %s AND end_time > %s)
        OR (start_time < %s AND end_time >= %s)
        OR (start_time >= %s AND end_time <= %s)
    )
    """
    params = (facility_id, start_time, start_time, end_time, end_time, start_time, end_time)
    result = execute_query_single(query, params)
    
    # Get facility's max concurrent bookings
    facility_query = "SELECT max_concurrent_bookings FROM facilities WHERE id = %s"
    facility = execute_query_single(facility_query, (facility_id,))
    
    # Return True if available, False if not
    return result['booking_count'] < facility['max_concurrent_bookings']

# Issue functions
def create_issue(user_id, unit_id, description, category_id=None):
    """Create a new maintenance issue"""
    query = """
    INSERT INTO issues (user_id, unit_id, category_id, description)
    VALUES (%s, %s, %s, %s)
    RETURNING *
    """
    params = (user_id, unit_id, category_id, description)
    return execute_query_single(query, params, commit=True)

def get_issues_by_unit(unit_id):
    """Get all issues for a unit"""
    query = """
    SELECT i.*, ic.name as category_name,
           u.phone_number as assignee_phone
    FROM issues i
    LEFT JOIN issue_categories ic ON i.category_id = ic.id
    LEFT JOIN users u ON i.assigned_to = u.id
    WHERE i.unit_id = %s
    ORDER BY i.created_at DESC
    """
    return execute_query(query, (unit_id,))

# Chat Log functions
def log_message(user_id, content, message_type):
    """Log a chat message"""
    query = """
    INSERT INTO chat_logs (user_id, content, message_type)
    VALUES (%s, %s, %s)
    RETURNING id
    """
    params = (user_id, content, message_type)
    result = execute_query_single(query, params, commit=True)
    return result['id'] if result else None

def log_anonymous_message(content, message_type):
    """Log a message without a user ID"""
    query = """
    INSERT INTO chat_logs (content, message_type)
    VALUES (%s, %s)
    RETURNING id
    """
    params = (content, message_type)
    result = execute_query_single(query, params, commit=True)
    return result['id'] if result else None
