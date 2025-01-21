import threading
import queue
import time
from openai import OpenAI

# DeepSeek API 配置
API_KEY = "sk-61a2affaa28f409580f87d7e4e74e1a1"  # 替换为你的 DeepSeek API Key
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

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
                result = self.process_message(message)
                if self.outbox and result:
                    self.outbox.put(result)  # 将处理结果发送给下一个代理
            time.sleep(1)  # 模拟处理时间

    def process_message(self, message):
        raise NotImplementedError("子类必须实现 process_message 方法")

    def call_deepseek_api(self, prompt, task):
        """调用 DeepSeek API 进行任务处理"""
        try:
            print(f"API Key: {API_KEY}")  # 打印 API Key
            print(f"Base URL: https://api.deepseek.com")  # 打印 API 地址
            print(f"请求内容: model=deepseek-chat, task={task}, prompt={prompt}")  # 打印请求内容
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant for {task}."},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"API 请求失败: {str(e)}"


# 客户服务代理
class CustomerServiceAgent(Agent):
    def process_message(self, message):
        if message.startswith("客户请求"):
            # 调用 DeepSeek API 处理客户请求
            result = self.call_deepseek_api(message, task="customer_service")
            return f"{self.name} 处理结果: {result}"


# 数据分析代理
class DataAnalysisAgent(Agent):
    def process_message(self, message):
        if "数据" in message:
            # 调用 DeepSeek API 进行数据分析
            result = self.call_deepseek_api(message, task="data_analysis")
            return f"{self.name} 分析结果: {result}"


# 市场营销代理
class MarketingAgent(Agent):
    def process_message(self, message):
        if "分析结果" in message:
            # 调用 DeepSeek API 制定营销策略
            result = self.call_deepseek_api(message, task="marketing")
            return f"{self.name} 制定策略: {result}"


# 主程序
if __name__ == "__main__":
    # 创建消息队列
    queue1 = queue.Queue()  # 客户服务 -> 数据分析
    queue2 = queue.Queue()  # 数据分析 -> 市场营销
    queue3 = queue.Queue()  # 市场营销 -> 结束

    # 创建代理
    customer_service = CustomerServiceAgent("客户服务代理", queue1, queue2)
    data_analysis = DataAnalysisAgent("数据分析代理", queue2, queue3)
    marketing = MarketingAgent("市场营销代理", queue3)

    # 启动代理
    customer_service.start()
    data_analysis.start()
    marketing.start()

    # 模拟客户请求
    requests_list = ["客户请求: 查询订单状态", "客户请求: 数据报告", "客户请求: 产品推荐"]
    for request in requests_list:
        print(f"发送请求: {request}")
        queue1.put(request)
        time.sleep(2)  # 模拟请求间隔

    # 等待代理完成任务
    time.sleep(10)
    print("所有任务完成")