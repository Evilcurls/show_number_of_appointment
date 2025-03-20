import requests
import datetime

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
        return
    
    # 获取预约详情配置
    query_params = {
        "access_token": access_token,
        "resource_id": resource_id,
        "start_date": datetime.date.today(),
        "end_date": datetime.date.today() + datetime.timedelta(days=1)
    }
    
    try:
        # 发送GET请求获取预约数据
        data_response = requests.get(base_url, params=query_params, verify=False)
        data_response.raise_for_status()
        
        # 解析并处理响应数据
        data = data_response.json()
        if data.get("e", "").upper() == "OK":
            output_str = ""
            for item in data.get("d", []):
                output_str += f"时间段: {item.get('str_time')}\n"
                output_str += f"剩余名额: {item.get('remainder_num')}\n"
                output_str += f"开始时间: {item.get('start_time')}\n"
                output_str += f"预约状态: {item.get('appoint_status')}\n"
                output_str += "-" * 40 + "\n"
            return output_str
        else:
            error_msg = data.get("m", "未知错误")
            raise ValueError(f"业务错误: {error_msg}")
    except Exception as e:
        print(f"获取预约详情时发生错误: {e}")
        return

