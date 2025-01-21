import threading
import queue
import time
import requests  # 确保正确导入 requests

# DeepSeek API 配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/analyze"  # 假设的 API 地址
API_KEY = "sk-61a2affaa28f409580f87d7e4e74e1a1"  # 替换为你的 DeepSeek API Key

# 定义一个基类 Agent
class Agent(threading.Thread):
    def __init__(self, name, inbox, outbox=None):
        super().__init__()
        self.name = name
        self.inbox = inbox  # 接收消息的队列
        self.outbox = outbox  # 发送消息的队列

    def run(self):
        while True:
            if not self.inbox.empty():
                message = self.inbox.get()
                print(f"{self.name} 收到消息: {message}")
                self.process_message(message)
            time.sleep(1)  # 模拟处理时间

    def process_message(self, message):
        raise NotImplementedError("子类必须实现 process_message 方法")


# 客户服务代理
class CustomerServiceAgent(Agent):
    def process_message(self, message):
        if message.startswith("客户请求"):
            response = f"{self.name} 已处理: {message}"
            print(response)
            if self.outbox:
                self.outbox.put(response)  # 将处理结果发送给下一个代理


# 数据分析代理
class DataAnalysisAgent(Agent):
    def process_message(self, message):
        if "数据" in message:
            # 调用 DeepSeek API 进行数据分析
            analysis_result = self.call_deepseek_api(message)
            print(f"{self.name} 分析结果: {analysis_result}")
            if self.outbox:
                self.outbox.put(analysis_result)  # 将分析结果发送给下一个代理

    def call_deepseek_api(self, text):
        """调用 DeepSeek API 进行分析"""
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "text": text,
            "task": "analyze",  # 假设的任务类型
        }
        response = requests.post(DEEPSEEK_API_URL, json=data, headers=headers)
        if response.status_code == 200:
            return response.json().get("result", "无结果")
        else:
            return f"API 请求失败: {response.status_code}"


# 市场营销代理
class MarketingAgent(Agent):
    def process_message(self, message):
        if "分析结果" in message:
            strategy = f"{self.name} 制定策略: 增加广告投放"
            print(strategy)


# 主程序
if __name__ == "__main__":
    # 创建消息队列
    queue1 = queue.Queue()  # 客户服务 -> 数据分析
    queue2 = queue.Queue()  # 数据分析 -> 市场营销

    # 创建代理
    customer_service = CustomerServiceAgent("客户服务代理", queue1, queue2)
    data_analysis = DataAnalysisAgent("数据分析代理", queue2, queue2)
    marketing = MarketingAgent("市场营销代理", queue2)

    # 启动代理
    customer_service.start()
    data_analysis.start()
    marketing.start()

    # 模拟客户请求
    requests_list = ["客户请求: 查询订单状态", "客户请求: 数据报告", "客户请求: 产品推荐"]  # 重命名变量以避免冲突
    for request in requests_list:
        print(f"发送请求: {request}")
        queue1.put(request)
        time.sleep(2)  # 模拟请求间隔

    # 等待代理完成任务
    time.sleep(5)
    print("所有任务完成")