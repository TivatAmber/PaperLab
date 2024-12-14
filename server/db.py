import sqlite3
import random
import string

def generate_class_key(length=6):
    """Generate a random alphanumeric key for class joining."""
    characters = string.ascii_uppercase + string.digits  # 使用大写字母和数字
    while True:
        key = ''.join(random.choices(characters, k=length))
        # 检查密钥是否已存在
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM classrooms WHERE join_key = ?", (key,))
        exists = cursor.fetchone()
        cursor.close()
        connection.close()
        if not exists:
            return key

# 获取数据库连接
def get_db_connection():
    connection = sqlite3.connect('db.sqlite')
    connection.row_factory = sqlite3.Row
    return connection

# 创建数据库表
def create_db():
    connection = get_db_connection()
    cursor = connection.cursor()

    # 创建用户表
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT CHECK(role IN ('teacher', 'student')) NOT NULL,
                        description TEXT,
                        avatar BLOB)''')

    # 创建课堂表
    cursor.execute('''CREATE TABLE IF NOT EXISTS classrooms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        join_key TEXT UNIQUE NOT NULL)''')  # 添加唯一的加入密钥

    # 创建用户与课堂关系表
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_classroom (
                        user_id INTEGER,
                        classroom_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (classroom_id) REFERENCES classrooms (id),
                        PRIMARY KEY (user_id, classroom_id))''')

    # 创建小组表，增加 leader_id 字段
    cursor.execute('''CREATE TABLE IF NOT EXISTS groups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        classroom_id INTEGER,
                        leader_id INTEGER,
                        FOREIGN KEY (classroom_id) REFERENCES classrooms (id),
                        FOREIGN KEY (leader_id) REFERENCES users (id))''')

    # 创建用户与小组关系表
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_group (
                        user_id INTEGER,
                        group_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (group_id) REFERENCES groups (id),
                        PRIMARY KEY (user_id, group_id))''')

    # 创建小组申请表
    cursor.execute('''CREATE TABLE IF NOT EXISTS applications (
                        student_id INTEGER,
                        group_id INTEGER,
                        status TEXT CHECK(status IN ('pending', 'approved', 'refused')),
                        FOREIGN KEY (student_id) REFERENCES users (id),
                        FOREIGN KEY (group_id) REFERENCES groups (id),
                        PRIMARY KEY (student_id, group_id))''')

    connection.commit()
    cursor.close()
    connection.close()

# 插入用户
def insert_user(account, password, role, description="签名"):
    # 连接数据库
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # 检查账号是否已存在
    cursor.execute("SELECT * FROM users WHERE account = ?", (account,))
    existing_user = cursor.fetchone()
    if existing_user:
        return {"success": False, "message": "Account already exists."}
    
    # 插入新用户
    cursor.execute("INSERT INTO users (account, password, role, description) VALUES (?, ?, ?, ?)", (account, password, role, description))
    connection.commit()
    user_id = cursor.lastrowid  # 获取插入的用户ID
    cursor.close()
    connection.close()
    
    return {"success": True, "message": "User created successfully.", "user_id": user_id}

def log(account, password, role):
    """
    User login with enhanced return information including description and avatar.
    
    Args:
        account (str): User account
        password (str): User password
        role (str): User role ('teacher' or 'student')
        
    Returns:
        dict: A dictionary containing success status, user info and message
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Query user information including description and avatar
    cursor.execute("""
        SELECT 
            id,
            role,
            description,
            avatar
        FROM users 
        WHERE account = ? 
        AND password = ? 
        AND role = ?
    """, (account, password, role))
    
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user is None:
        return {
            "success": False, 
            "message": "Invalid account or password."
        }

    # Format the response with all user information
    return {
        "success": True,
        "user_id": user["id"],
        "role": user["role"],
        "description": user["description"],
        "avatar": user["avatar"],  # This will be the blob data from the database
        "message": "Login successful."
    }


# 获取所有课堂
def get_all_classes():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM classrooms")
    classes = cursor.fetchall()
    cursor.close()
    connection.close()
    return [{"id": row["id"], "name": row["name"]} for row in classes]

def get_all_groups(class_id):
    """
    Get all groups in a class with their descriptions.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            g.id,
            g.name,
            g.description,
            g.leader_id,
            u.account as leader_name
        FROM groups g
        LEFT JOIN users u ON g.leader_id = u.id
        WHERE g.classroom_id = ?
    """, (class_id,))
    groups = cursor.fetchall()
    cursor.close()
    connection.close()
    return {"success": True,
            "groups": [{
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "leader_id": row["leader_id"],
        "leader_name": row["leader_name"]
    } for row in groups]}

# 学生加入课堂
def student_join_class(student_id, class_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # 检查学生是否已经在该课堂中
    cursor.execute("SELECT 1 FROM user_classroom WHERE user_id = ? AND classroom_id = ?", (student_id, class_id))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return {"message": "Student is already in the class."}
    
    # 加入课堂
    cursor.execute("INSERT INTO user_classroom (user_id, classroom_id) VALUES (?, ?)", (student_id, class_id))
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Student joined class successfully."}

# 学生退出课堂
def student_quit_class(student_id, class_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # 退出课堂
    cursor.execute("DELETE FROM user_classroom WHERE user_id = ? AND classroom_id = ?", (student_id, class_id))
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Student quit class successfully."}

# 学生加入小组
def student_join_group(student_id, group_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # 检查学生是否已经加入该小组
    cursor.execute("SELECT 1 FROM user_group WHERE user_id = ? AND group_id = ?", (student_id, group_id))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return {"message": "Student is already in the group."}
    
    # 加入小组
    cursor.execute("INSERT INTO user_group (user_id, group_id) VALUES (?, ?)", (student_id, group_id))
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Student joined group successfully."}

# 修改教师创建课堂的函数
def teacher_create_class(teacher_id, class_name):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 检查教师是否已在数据库中
        cursor.execute("SELECT id FROM users WHERE id = ? AND role = 'teacher'", (teacher_id,))
        teacher = cursor.fetchone()
        if teacher is None:
            return {"success": False, "message": "Teacher not found or not authorized."}
        
        # 生成唯一的加入密钥
        join_key = generate_class_key()
        
        # 创建课堂，包含加入密钥
        cursor.execute("INSERT INTO classrooms (name, join_key) VALUES (?, ?)", (class_name, join_key))
        connection.commit()

        # 获取刚刚插入的课堂ID
        classroom_id = cursor.lastrowid
        
        # 将教师添加到用户与课堂关系表中
        cursor.execute("INSERT INTO user_classroom (user_id, classroom_id) VALUES (?, ?)", (teacher_id, classroom_id))
        connection.commit()

        cursor.close()
        connection.close()

        return {
            "success": True,
            "message": "Class created successfully.",
            "class_id": classroom_id,
            "join_key": join_key
        }
    
    except Exception as e:
        return {"success": False, "message": f"An error occurred: {str(e)}"}

def get_class_by_key(join_key):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT id, name FROM classrooms WHERE join_key = ?", (join_key,))
    classroom = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if classroom:
        return {
            "success": True,
            "class_id": classroom['id'],
            "class_name": classroom['name']
        }
    return {
        "success": False,
        "message": "Invalid class key."
    }

def get_class_key(class_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT join_key FROM classrooms WHERE id = ?", (class_id,))
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if result:
        return {
            "success": True,
            "join_key": result['join_key']
        }
    return {
        "success": False,
        "message": "Class not found."
    }

# 教师删除课堂
def teacher_delete_class(teacher_id, class_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM classrooms WHERE id = ?", (class_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Class deleted successfully."}

# 教师创建小组并指定小组长
def teacher_create_group(teacher_id, class_id, group_name, leader_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # 检查教师是否在该课堂中
    cursor.execute("SELECT 1 FROM user_classroom WHERE user_id = ? AND classroom_id = ?", (teacher_id, class_id))
    if cursor.fetchone() is None:
        cursor.close()
        connection.close()
        return {"message": "Teacher is not in the class."}
    
    # 创建小组
    cursor.execute("INSERT INTO groups (name, classroom_id, leader_id) VALUES (?, ?, ?)", (group_name, class_id, leader_id))
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Group created successfully."}

# 教师删除小组
def teacher_delete_group(teacher_id, group_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # 删除小组
    cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Group deleted successfully."}

def leader_approve_application(leader_id, student_id, group_id):
    """
    Leader approves a student's application to join the group.
    
    Args:
        leader_id (int): The ID of the group leader
        student_id (int): The ID of the applying student
        group_id (int): The ID of the group
        
    Returns:
        dict: A dictionary containing success status and message
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verify that the user is the group leader
        cursor.execute("""
            SELECT 1 FROM groups 
            WHERE id = ? AND leader_id = ?
        """, (group_id, leader_id))
        
        if cursor.fetchone() is None:
            return {
                "success": False,
                "message": "Only the group leader can approve applications."
            }
            
        # Check if application exists and is pending
        cursor.execute("""
            SELECT status FROM applications 
            WHERE student_id = ? AND group_id = ?
        """, (student_id, group_id))
        
        application = cursor.fetchone()
        if not application:
            return {
                "success": False,
                "message": "Application not found."
            }
        
        if application['status'] != 'pending':
            return {
                "success": False,
                "message": f"Application is already {application['status']}."
            }
        
        # Update application status
        cursor.execute("""
            UPDATE applications 
            SET status = 'approved' 
            WHERE student_id = ? AND group_id = ?
        """, (student_id, group_id))
        
        # Add student to group
        cursor.execute("""
            INSERT INTO user_group (user_id, group_id) 
            VALUES (?, ?)
        """, (student_id, group_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "message": "Application approved and student added to group."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }

def leader_refuse_application(leader_id, student_id, group_id):
    """
    Leader refuses a student's application to join the group.
    
    Args:
        leader_id (int): The ID of the group leader
        student_id (int): The ID of the applying student
        group_id (int): The ID of the group
        
    Returns:
        dict: A dictionary containing success status and message
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verify that the user is the group leader
        cursor.execute("""
            SELECT 1 FROM groups 
            WHERE id = ? AND leader_id = ?
        """, (group_id, leader_id))
        
        if cursor.fetchone() is None:
            return {
                "success": False,
                "message": "Only the group leader can refuse applications."
            }
        
        # Update application status
        cursor.execute("""
            UPDATE applications 
            SET status = 'refused' 
            WHERE student_id = ? AND group_id = ? AND status = 'pending'
        """, (student_id, group_id))
        
        if cursor.rowcount == 0:
            return {
                "success": False,
                "message": "No pending application found."
            }
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "message": "Application refused successfully."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }

def get_user_classes(user_id):
    """
    Get all classes associated with a user (both teacher and student).
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        dict: A dictionary containing:
            - success (bool): Whether the operation was successful
            - classes (list): List of class dictionaries with id, name, and role
            - message (str): Error message if any
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First, verify the user exists and get their role
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user is None:
            return {
                "success": False,
                "message": "User not found.",
                "classes": []
            }
        
        # Get all classes the user is associated with
        cursor.execute("""
            SELECT 
                c.id,
                c.name,
                c.join_key,
                u.role
            FROM classrooms c
            JOIN user_classroom uc ON c.id = uc.classroom_id
            JOIN users u ON u.id = uc.user_id
            WHERE uc.user_id = ?
        """, (user_id,))
        
        classes = cursor.fetchall()
        
        # Format the results
        formatted_classes = [{
            "id": row["id"],
            "name": row["name"],
            "join_key": row["join_key"] if row["role"] == "teacher" else None,
            "role": row["role"]
        } for row in classes]
        
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "classes": formatted_classes,
            "message": "Classes retrieved successfully."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
            "classes": []
        }


def student_join_class_by_key(student_id, join_key):
    """
    Allow a student to join a class using a join key.
    
    Args:
        student_id (int): The ID of the student
        join_key (str): The join key for the class
        
    Returns:
        dict: A dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Success or error message
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First verify that the student exists and is actually a student
        cursor.execute("SELECT role FROM users WHERE id = ? AND role = 'student'", (student_id,))
        student = cursor.fetchone()
        if student is None:
            return {
                "success": False,
                "message": "Invalid student ID or not a student account."
            }
        
        # Find the class with the given join key
        cursor.execute("SELECT id FROM classrooms WHERE join_key = ?", (join_key,))
        classroom = cursor.fetchone()
        
        if classroom is None:
            return {
                "success": False,
                "message": "Invalid join key."
            }
        
        class_id = classroom['id']
        
        # Check if student is already in the class
        cursor.execute("""
            SELECT 1 FROM user_classroom 
            WHERE user_id = ? AND classroom_id = ?
        """, (student_id, class_id))
        
        if cursor.fetchone():
            return {
                "success": False,
                "message": "You are already a member of this class."
            }
        
        # Add student to the class
        cursor.execute("""
            INSERT INTO user_classroom (user_id, classroom_id)
            VALUES (?, ?)
        """, (student_id, class_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "message": "Successfully joined the class."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }
    
def student_create_team(student_id, class_id, team_name, description=None):
    """
    Allow a student to create a team and become its leader, ensuring they're not already in another group.
    
    Args:
        student_id (int): The ID of the student creating the team
        class_id (int): The ID of the class where the team will be created
        team_name (str): The name for the new team
        description (str, optional): Description of the team
        
    Returns:
        dict: A dictionary containing success status, message, and team_id if successful
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First verify that the user is a student
        cursor.execute("""
            SELECT role FROM users 
            WHERE id = ? AND role = 'student'
        """, (student_id,))
        
        if cursor.fetchone() is None:
            return {
                "success": False,
                "message": "Invalid student ID or not a student account."
            }
            
        # Check if student is in the class
        cursor.execute("""
            SELECT 1 FROM user_classroom 
            WHERE user_id = ? AND classroom_id = ?
        """, (student_id, class_id))
        
        if cursor.fetchone() is None:
            return {
                "success": False,
                "message": "Student is not a member of this class."
            }
            
        # Check if student is already in any group in this class
        cursor.execute("""
            SELECT g.name
            FROM user_group ug
            JOIN groups g ON ug.group_id = g.id
            WHERE g.classroom_id = ? AND ug.user_id = ?
            UNION
            SELECT g.name
            FROM groups g
            WHERE g.classroom_id = ? AND g.leader_id = ?
        """, (class_id, student_id, class_id, student_id))
        
        existing_group = cursor.fetchone()
        if existing_group:
            return {
                "success": False,
                "message": f"You are already a member of group '{existing_group['name']}' in this class."
            }

        # Check if student has any pending applications in this class
        cursor.execute("""
            SELECT g.name
            FROM applications a
            JOIN groups g ON a.group_id = g.id
            WHERE g.classroom_id = ? AND a.student_id = ? AND a.status = 'pending'
        """, (class_id, student_id))
        
        pending_app = cursor.fetchone()
        if pending_app:
            return {
                "success": False,
                "message": f"You have a pending application to group '{pending_app['name']}'. Please cancel it first."
            }
        
        # Create the new team
        cursor.execute("""
            INSERT INTO groups (name, description, classroom_id, leader_id) 
            VALUES (?, ?, ?, ?)
        """, (team_name, description, class_id, student_id))
        
        team_id = cursor.lastrowid
        
        # Add the student to the team as a member
        cursor.execute("""
            INSERT INTO user_group (user_id, group_id) 
            VALUES (?, ?)
        """, (student_id, team_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "message": "Team created successfully. You are now the team leader.",
            "team_id": team_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }
    
def student_apply_to_group(student_id, group_id):
    """
    Allow a student to apply to join a group.
    The application will be pending until the leader approves or refuses it.
    
    Args:
        student_id (int): The ID of the student applying
        group_id (int): The ID of the group to join
        
    Returns:
        dict: A dictionary containing success status and message
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verify that the user exists and is a student
        cursor.execute("""
            SELECT role FROM users 
            WHERE id = ? AND role = 'student'
        """, (student_id,))
        
        if cursor.fetchone() is None:
            return {
                "success": False,
                "message": "Invalid student ID or not a student account."
            }
            
        # Get the class ID for this group
        cursor.execute("""
            SELECT classroom_id, leader_id 
            FROM groups 
            WHERE id = ?
        """, (group_id,))
        group_info = cursor.fetchone()
        
        if group_info is None:
            return {
                "success": False,
                "message": "Group not found."
            }
            
        if group_info['leader_id'] == student_id:
            return {
                "success": False,
                "message": "You are already the leader of this group."
            }
            
        class_id = group_info['classroom_id']
        
        # Verify student is in the class
        cursor.execute("""
            SELECT 1 FROM user_classroom 
            WHERE user_id = ? AND classroom_id = ?
        """, (student_id, class_id))
        
        if cursor.fetchone() is None:
            return {
                "success": False,
                "message": "You must be a member of the class to apply to a group."
            }
        
        # Check if student is already in another group in this class
        cursor.execute("""
            SELECT g.name
            FROM user_group ug
            JOIN groups g ON ug.group_id = g.id
            WHERE g.classroom_id = ? AND ug.user_id = ?
        """, (class_id, student_id))
        
        existing_group = cursor.fetchone()
        if existing_group:
            return {
                "success": False,
                "message": f"You are already a member of group '{existing_group['name']}' in this class."
            }
        
        # Check if student already has a pending application for this group
        cursor.execute("""
            SELECT status 
            FROM applications 
            WHERE student_id = ? AND group_id = ?
        """, (student_id, group_id))
        
        existing_application = cursor.fetchone()
        if existing_application:
            if existing_application['status'] == 'pending':
                return {
                    "success": False,
                    "message": "You already have a pending application for this group."
                }
            elif existing_application['status'] == 'approved':
                return {
                    "success": False,
                    "message": "You are already a member of this group."
                }
            else:  # status is 'refused'
                # Update the existing application to pending
                cursor.execute("""
                    UPDATE applications 
                    SET status = 'pending' 
                    WHERE student_id = ? AND group_id = ?
                """, (student_id, group_id))
        else:
            # Create new application
            cursor.execute("""
                INSERT INTO applications (student_id, group_id, status) 
                VALUES (?, ?, 'pending')
            """, (student_id, group_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "message": "Application submitted successfully. Waiting for leader's approval."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }

def get_group_applications(group_id):
    """
    Get all applications for a group.
    
    Args:
        group_id (int): The ID of the group
        
    Returns:
        dict: A dictionary containing applications information
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT 
                a.student_id,
                a.status,
                u.account as student_name,
                u.description as description
            FROM applications a
            JOIN users u ON a.student_id = u.id
            WHERE a.group_id = ? AND a.status = 'pending'
        """, (group_id,))
        
        applications = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "applications": [{
                "student_id": app['student_id'],
                "student_name": app['student_name'],
                "description": app['description'],
                "status": app['status']
            } for app in applications]
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }
    
def get_group_members(group_id):
    """
    Get all members of a specific group with their details.
    
    Args:
        group_id (int): The ID of the group
        
    Returns:
        dict: A dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Error message if any
            - group: Group information including name and description
            - leader: Leader information
            - members: List of group members with their details
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First get group information
        cursor.execute("""
            SELECT 
                g.id,
                g.name,
                g.description,
                g.leader_id,
                u.account as leader_name,
                u.description as leader_description
            FROM groups g
            JOIN users u ON g.leader_id = u.id
            WHERE g.id = ?
        """, (group_id,))
        
        group = cursor.fetchone()
        
        if group is None:
            return {
                "success": False,
                "message": "Group not found."
            }
        
        # Get all members (including leader)
        cursor.execute("""
            SELECT 
                u.id,
                u.account,
                u.description,
                CASE WHEN u.id = ? THEN TRUE ELSE FALSE END as is_leader
            FROM user_group ug
            JOIN users u ON ug.user_id = u.id
            WHERE ug.group_id = ?
            ORDER BY is_leader DESC, u.account
        """, (group['leader_id'], group_id))
        
        members = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Format the response
        return {
            "success": True,
            "group": {
                "id": group['id'],
                "name": group['name'],
                "description": group['description']
            },
            "leader": {
                "id": group['leader_id'],
                "name": group['leader_name'],
                "description": group['leader_description']
            },
            "members": [{
                "id": member['id'],
                "name": member['account'],
                "description": member['description'],
                "is_leader": bool(member['is_leader'])
            } for member in members],
            "total_members": len(members)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }

def get_group_members_simple(group_id):
    """
    Get a simple list of members in a group.
    This is a lighter version that returns just basic member information.
    
    Args:
        group_id (int): The ID of the group
        
    Returns:
        dict: A dictionary containing success status and list of members
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get basic member information
        cursor.execute("""
            SELECT 
                u.id,
                u.account as name,
                u.description as description,
                CASE WHEN u.id = g.leader_id THEN TRUE ELSE FALSE END as is_leader
            FROM user_group ug
            JOIN users u ON ug.user_id = u.id
            JOIN groups g ON ug.group_id = g.id
            WHERE ug.group_id = ?
            ORDER BY is_leader DESC, name
        """, (group_id,))
        
        members = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if not members:
            return {
                "success": False,
                "message": "No members found or group doesn't exist."
            }
        
        return {
            "success": True,
            "members": [{
                "id": member['id'],
                "name": member['name'],
                "description": member['description'],
                "is_leader": bool(member['is_leader'])
            } for member in members],
            "total_members": len(members)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }
    
def get_group_leader(group_id):
    """
    Get the leader information of a specific group.
    
    Args:
        group_id (int): The ID of the group
        
    Returns:
        dict: A dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Error message if failed
            - leader (dict): Leader information if successful
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get leader information from group and user tables
        cursor.execute("""
            SELECT 
                u.id as leader_id,
                u.account as leader_name,
                u.description as leader_description,
                g.name as group_name
            FROM groups g
            JOIN users u ON g.leader_id = u.id
            WHERE g.id = ?
        """, (group_id,))
        
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result is None:
            return {
                "success": False,
                "message": "Group not found."
            }
            
        return {
            "success": True,
            "leader": {
                "id": result['leader_id'],
                "name": result['leader_name'],
                "description": result['leader_description']
            },
            "group_name": result['group_name']
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }

def student_quit_group(student_id, group_id):
    """
    Allow a student to quit a group, handling both membership and applications.
    
    Args:
        student_id (int): The ID of the student quitting the group
        group_id (int): The ID of the group to quit
        
    Returns:
        dict: A dictionary containing success status and message
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First verify the group exists
        cursor.execute("SELECT leader_id FROM groups WHERE id = ?", (group_id,))
        group = cursor.fetchone()
        
        if group is None:
            return {
                "success": False,
                "message": "Group not found."
            }
            
        # Check if student is the group leader
        if group['leader_id'] == student_id:
            return {
                "success": False,
                "message": "Group leader cannot quit. Transfer leadership or delete the group instead."
            }
        
        # Remove any pending applications
        cursor.execute("""
            DELETE FROM applications 
            WHERE student_id = ? AND group_id = ?
        """, (student_id, group_id))
        
        # Remove from group membership if exists
        cursor.execute("""
            DELETE FROM user_group 
            WHERE user_id = ? AND group_id = ?
        """, (student_id, group_id))
        
        # Determine what actions were taken
        total_changes = cursor.rowcount
        
        connection.commit()
        cursor.close()
        connection.close()
        
        if total_changes == 0:
            return {
                "success": False,
                "message": "Student was not a member of this group or had no pending applications."
            }
        
        return {
            "success": True,
            "message": "Successfully removed from group and/or applications."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }
    
def teacher_remove_group(teacher_id, group_id):
    """
    Allow a teacher to remove a specific group after verifying authorization.
    
    Args:
        teacher_id (int): The ID of the teacher
        group_id (int): The ID of the group to remove
        
    Returns:
        dict: A dictionary containing success status and message
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First get the group and its class info
        cursor.execute("""
            SELECT g.name, g.classroom_id
            FROM groups g
            WHERE g.id = ?
        """, (group_id,))
        
        group = cursor.fetchone()
        if group is None:
            return {
                "success": False,
                "message": "Group not found."
            }
            
        # Verify that the teacher is associated with this class
        cursor.execute("""
            SELECT 1 FROM user_classroom uc
            JOIN users u ON uc.user_id = u.id
            WHERE u.id = ? 
            AND u.role = 'teacher' 
            AND uc.classroom_id = ?
        """, (teacher_id, group['classroom_id']))
        
        if cursor.fetchone() is None:
            return {
                "success": False,
                "message": "Unauthorized. Teacher must be associated with this group's class."
            }
            
        # Begin cleanup - using a transaction to ensure all operations succeed or none do
        try:
            # Remove all applications for this group
            cursor.execute("DELETE FROM applications WHERE group_id = ?", (group_id,))
            
            # Remove all user-group relationships
            cursor.execute("DELETE FROM user_group WHERE group_id = ?", (group_id,))
            
            # Finally, remove the group
            cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
            
            connection.commit()
            
            return {
                "success": True,
                "message": f"Successfully removed group '{group['name']}' and all associated data."
            }
            
        except Exception as e:
            connection.rollback()
            raise e
            
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }
    finally:
        cursor.close()
        connection.close()

def update_user_description(user_id, new_description):
    """
    Update a user's description.
    
    Args:
        user_id (int): The ID of the user
        new_description (str): The new description text
        
    Returns:
        dict: A dictionary containing success status and message
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First verify user exists
        cursor.execute("SELECT 1 FROM users WHERE id = ?", (user_id,))
        if cursor.fetchone() is None:
            return {
                "success": False,
                "message": "User not found."
            }
        
        # Update the description
        cursor.execute("""
            UPDATE users 
            SET description = ? 
            WHERE id = ?
        """, (new_description, user_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "message": "Description updated successfully."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }
    
def get_user_groups(user_id):
    """
    Get all groups associated with a user, including their role in each group.
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        dict: A dictionary containing success status, user's groups and role details
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First verify user exists and get their role
        cursor.execute("""
            SELECT role FROM users 
            WHERE id = ?
        """, (user_id,))
        
        user = cursor.fetchone()
        if user is None:
            return {
                "success": False,
                "message": "User not found."
            }
        
        # Get all groups where the user is either a member or leader
        cursor.execute("""
            SELECT DISTINCT
                g.id,
                g.name,
                g.description,
                g.classroom_id,
                c.name as class_name,
                g.leader_id,
                CASE 
                    WHEN g.leader_id = ? THEN 'leader'
                    WHEN ug.user_id IS NOT NULL THEN 'member'
                END as role
            FROM groups g
            JOIN classrooms c ON g.classroom_id = c.id
            LEFT JOIN user_group ug ON g.id = ug.group_id AND ug.user_id = ?
            WHERE g.leader_id = ? OR ug.user_id = ?
            ORDER BY c.name, g.name
        """, (user_id, user_id, user_id, user_id))
        
        groups = cursor.fetchall()
        
        # Format the groups data
        formatted_groups = [{
            "group_id": group['id'],
            "group_name": group['name'],
            "description": group['description'],
            "class_id": group['classroom_id'],
            "class_name": group['class_name'],
            "is_leader": group['role'] == 'leader',
            "role": group['role']
        } for group in groups]
        
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "message": "Groups retrieved successfully.",
            "groups": formatted_groups,
            "total_groups": len(formatted_groups)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }
    
def delete_class_with_groups(user_id, class_id):
    """
    Delete a class and all its associated groups after verifying user authorization.
    Only teachers who are members of the class can delete it.
    
    Args:
        user_id (int): The ID of the user attempting to delete
        class_id (int): The ID of the class to delete
        
    Returns:
        dict: A dictionary containing success status and detailed message
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First verify the user is a teacher
        cursor.execute("""
            SELECT role, account 
            FROM users 
            WHERE id = ? AND role = 'teacher'
        """, (user_id,))
        
        teacher = cursor.fetchone()
        if not teacher:
            return {
                "success": False,
                "message": "Unauthorized. Only teachers can delete classes."
            }
            
        # Verify the class exists and get its info
        cursor.execute("""
            SELECT name 
            FROM classrooms 
            WHERE id = ?
        """, (class_id,))
        
        class_info = cursor.fetchone()
        if not class_info:
            return {
                "success": False,
                "message": "Class not found."
            }
            
        # Verify the teacher is associated with this class
        cursor.execute("""
            SELECT 1 
            FROM user_classroom 
            WHERE user_id = ? AND classroom_id = ?
        """, (user_id, class_id))
        
        if not cursor.fetchone():
            return {
                "success": False,
                "message": "Unauthorized. Teacher must be associated with this class."
            }
            
        try:
            # Get counts before deletion for the response message
            cursor.execute("SELECT COUNT(*) as group_count FROM groups WHERE classroom_id = ?", (class_id,))
            group_count = cursor.fetchone()['group_count']
            
            cursor.execute("""
                SELECT COUNT(DISTINCT ug.user_id) as member_count 
                FROM groups g 
                JOIN user_group ug ON g.id = ug.group_id 
                WHERE g.classroom_id = ?
            """, (class_id,))
            group_members_count = cursor.fetchone()['member_count']
            
            # Start deletion process in correct order
            
            # 1. Delete all applications for groups in this class
            cursor.execute("""
                DELETE FROM applications 
                WHERE group_id IN (
                    SELECT id FROM groups WHERE classroom_id = ?
                )
            """, (class_id,))
            
            # 2. Delete all user-group relationships for groups in this class
            cursor.execute("""
                DELETE FROM user_group 
                WHERE group_id IN (
                    SELECT id FROM groups WHERE classroom_id = ?
                )
            """, (class_id,))
            
            # 3. Delete all groups in the class
            cursor.execute("DELETE FROM groups WHERE classroom_id = ?", (class_id,))
            
            # 4. Delete all user-classroom relationships
            cursor.execute("DELETE FROM user_classroom WHERE classroom_id = ?", (class_id,))
            
            # 5. Finally delete the class itself
            cursor.execute("DELETE FROM classrooms WHERE id = ?", (class_id,))
            
            connection.commit()
            
            return {
                "success": True,
                "message": (f"Successfully deleted class '{class_info['name']}' "
                          f"including {group_count} groups and their {group_members_count} member relationships."),
                "details": {
                    "class_name": class_info['name'],
                    "groups_deleted": group_count,
                    "group_members_affected": group_members_count
                }
            }
            
        except Exception as e:
            connection.rollback()
            raise e
            
    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }
    finally:
        cursor.close()
        connection.close()