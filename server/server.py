from http.server import BaseHTTPRequestHandler, HTTPServer  # 导入处理 HTTP 请求的模块
import json  # 导入 JSON 模块，用于处理 JSON 数据
import db  # 导入数据库操作模块，方便与 SQLite 数据库进行交互

# 定义请求处理类，继承自 BaseHTTPRequestHandler
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # 处理 GET 请求的方法
    def do_GET(self):
        print("No Get")
        return
    # 处理 POST 请求的方法
    def do_POST(self):
        # 获取 POST 请求中数据的长度
        content_length = int(self.headers["Content-Length"])
        # 根据数据长度读取 POST 请求中的数据
        post_data = self.rfile.read(content_length)
        #print(post_data)
        # 将接收到的 JSON 数据转换为 Python 字典
        data = json.loads(post_data)
        
        # 打印接收到的数据到控制台，便于调试
        print("Received POST data:", data)

        # 将接收到的用户数据插入到数据库中
        if data['type'] == 'log' :
            success = db.log(data['account'],data['password'],data['identity'])
            # 将获取的用户数据转换为 JSON 格式
            response = success

        elif data['type'] == 'register' :
            success = db.insert_user(data['account'],data['password'],data['identity'])
            # 将获取的用户数据转换为 JSON 格式
            response = success

        elif data['type'] == 'find_all_class' :
            classes = db.get_all_classes()
            response = classes

        elif data['type'] == 'get_all_groups' :
            groups = db.get_all_groups(data['class'])
            response = groups

        elif data['type'] == 'leader_find_group_application' :
            application = db.get_all_application(data['group'])
            response = application

        elif data['type'] == 'student_join_class' :
            response = db.student_join_class(data['student'],data['class'])
            
        elif data['type'] == 'student_quit_class' :
            response = db.student_quit_class(data['student'],data['class'])

        elif data['type'] == 'student_join_group' :
            response = db.student_join_group(data['student'],data['class'],data['group'])
        
        elif data['type'] == 'student_delete_group' :
            response = db.student_delete_group(data['student'],data['class'],data['group'])

        elif data['type'] == 'teacher_create_class' :
            response = db.teacher_create_class(data['teacher'],data['class'])

        elif data['type'] == 'teacher_delete_class' :
            response = db.teacher_delete_class(data['teacher'],data['class'])
            
        elif data['type'] == 'teacher_mk_stu_join_group' :
            response = db.teacher_mk_stu_join_group(data['teacher'],data['student'],data['class'],data['group'])

        elif data['type'] == 'teacher_mk_stu_quit_group' :
            response = db.teacher_mk_stu_quit_group(data['teacher'],data['student'],data['class'],data['group'])

        elif data['type'] == 'teacher_delete_group' :
            response = db.teacher_delete_group(data['teacher'],data['class'],data['group'])

        elif data['type'] == 'get_user_classes' :
            response = db.get_user_classes(data['user_id'])

        elif data['type'] == 'get_class_key' :
            response = db.get_class_key(data['class_id'])

        elif data['type'] == 'get_class_by_key' :
            response = db.get_class_by_key(data['join_key'])

        elif data['type'] == 'student_join_class_by_key':
            response = db.student_join_class_by_key(data['student_id'], data['join_key'])

        elif data['type'] == 'student_create_team':
            response = db.student_create_team(
                data['student_id'],
                data['class_id'],
                data['team_name'],
                data.get('description')  # Optional description
            )

        elif data['type'] == 'student_apply_to_group':
            response = db.student_apply_to_group(
                data['student_id'],
                data['group_id']
            )

        elif data['type'] == 'get_group_applications':
            response = db.get_group_applications(data['group_id'])

        elif data['type'] == 'leader_approve_application':
            response = db.leader_approve_application(
                data['leader_id'],
                data['student_id'],
                data['group_id']
            )

        elif data['type'] == 'leader_refuse_application':
            response = db.leader_refuse_application(
                data['leader_id'],
                data['student_id'],
                data['group_id']
            )

        elif data['type'] == 'get_group_members':
            response = db.get_group_members(data['group_id'])

        elif data['type'] == 'get_group_members_simple':
            response = db.get_group_members_simple(data['group_id'])

        elif data['type'] == 'get_group_leader':
            response = db.get_group_leader(data['group_id'])

        elif data['type'] == 'student_quit_group':
            response = db.student_quit_group(
                data['student_id'],  # Changed from 'student' to match new function
                data['group_id']     # Changed from 'group' to match new function
            )

        elif data['type'] == 'teacher_remove_group':
            response = db.teacher_remove_group(
                data['teacher_id'],
                data['group_id']
            )

        elif data['type'] == 'update_user_description':
            response = db.update_user_description(
                data['user_id'],
                data['new_description']
            )

        elif data['type'] == 'get_user_groups':
            response = db.get_user_groups(data['user_id'])

        elif data['type'] == 'delete_class_with_groups':
            response = db.delete_class_with_groups(
                data['user_id'],
                data['class_id']
            )
            
        else :
            print(data['type'])
            self.send_response(403)
            return

        
        # 发送响应状态码 200，表示请求成功
        self.send_response(200)
        
        # 设置响应头，指定返回内容类型为 JSON
        self.send_header("Content-type", "application/json")
        self.end_headers()  # 结束响应头部分
        print(response)
        # 将响应内容转换为 JSON 格式并发送回客户端 
        self.wfile.write(json.dumps(response).encode())

# 设置服务器的主机和端口
host = "localhost"
port = 14456

# 在启动服务器之前，先确保数据库和表已经创建
db.create_db()

# 创建 HTTP 服务器对象，指定服务器地址和请求处理类
httpd = HTTPServer((host, port), SimpleHTTPRequestHandler)

# 打印服务器启动信息
print(f"Server started at http://{host}:{port}")

# 启动服务器，持续监听请求
httpd.serve_forever()

# curl -X GET http://localhost:8080 -H "Content-Type: application/json" \ -d "{\"type\":\"log\",\"account\":\"xyz\",\"password\":\"123456\"}"