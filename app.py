from flask import Flask, render_template, jsonify
import requests
import datetime

app = Flask(__name__)

# 获取预约详情的函数
def fetch_appointment_details(app_id, app_secret, resource_id):
    token_url = "https://workflow.cuc.edu.cn/reservation/open/token/get"
    base_url = "https://workflow.cuc.edu.cn/reservation/open/resverve/get-appointment-detail"
    
    # 获取Token配置
    token_params = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    
    try:
        # 发送GET请求获取Token
        token_response = requests.get(token_url, params=token_params, verify=False)
        token_response.raise_for_status()
        
        # 解析JSON响应
        token_data = token_response.json()
        access_token = token_data["d"]["access_token"]
        
        print(f"成功获取Token: {access_token}")
    except Exception as e:
        print(f"获取Token时发生错误: {e}")
        return []
    
    # 获取预约详情配置
    query_params = {
        "access_token": access_token,
        "resource_id": resource_id,
        "start_date": datetime.date.today(),
        "end_date": datetime.date.today()
    }
    
    try:
        # 发送GET请求获取预约数据
        data_response = requests.get(base_url, params=query_params, verify=False)
        data_response.raise_for_status()
        
        # 解析并处理响应数据
        data = data_response.json()
        if data.get("e", "").upper() == "OK":
            appointments = []
            for item in data.get("d", []):
                remaining_slots = int(item.get("remainder_num", 0))  # 强制转换为整数，默认值为 0
                total_slots = 250  # 总预约人数固定为 250
                booked_slots = total_slots - remaining_slots  # 已预约人数 = 总人数 - 剩余名额
                
                appointments.append({
                    "time_period": item.get("str_time"),
                    "remaining_slots": remaining_slots,
                    "booked_slots": booked_slots,  # 添加已预约人数
                    "start_time": item.get("start_time"),
                    "status": "可用" if item.get("appoint_status") == 1 else "不可用"
                })
            return appointments
        else:
            error_msg = data.get("m", "未知错误")
            raise ValueError(f"业务错误: {error_msg}")
    except Exception as e:
        print(f"获取预约详情时发生错误: {e}")
        return []

@app.route('/')
def index():
    app_id = "14"
    app_secret = "ftt2ggiqxcs2pxhdgfzq1msztl4cu5q4"
    resource_id = "407"
    
    # 获取预约数据
    appointments = fetch_appointment_details(app_id, app_secret, resource_id)
    
    # 格式化数据为图表所需格式
    labels = [item["time_period"] for item in appointments]  # 时间段
    remaining_data = [item["remaining_slots"] for item in appointments]  # 剩余名额
    booked_data = [item["booked_slots"] for item in appointments]  # 已预约人数
    
    # 获取今天的日期并生成标题
    today_date = datetime.date.today().strftime("%Y-%m-%d")  # 格式化为 YYYY-MM-DD
    title = f"{today_date} 预约情况"
    
    # 自定义公告内容
    with open('公告.txt','r',encoding=('utf-8')) as txtdata:
     announcement = txtdata.read()
    
    # 渲染模板并传递数据
    return render_template('index.html', labels=labels, remaining_data=remaining_data, booked_data=booked_data, title=title, announcement=announcement)

@app.route('/update')
def update():
    app_id = "14"
    app_secret = "ftt2ggiqxcs2pxhdgfzq1msztl4cu5q4"
    resource_id = "407"
    
    # 获取预约数据
    
    appointments = fetch_appointment_details(app_id, app_secret, resource_id)
    
    # 格式化数据为 JSON 格式
    labels = [item["time_period"] for item in appointments]
    remaining_data = [item["remaining_slots"] for item in appointments]
    booked_data = [item["booked_slots"] for item in appointments]
    
    return jsonify({"labels": labels, "remaining_data": remaining_data, "booked_data": booked_data})

if __name__ == '__main__':
    app.run(debug=True)