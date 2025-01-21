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

    def call_deepseek_api(self, prompt, task_description):
        """调用 DeepSeek API 进行任务处理"""
        try:
            print(f"API Key: {API_KEY}")  # 打印 API Key
            print(f"Base URL: https://api.deepseek.com")  # 打印 API 地址
            print(f"请求内容: model=deepseek-chat, task={task_description}, prompt={prompt}")  # 打印请求内容
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant for {task_description}."},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
            )
            print(f"API 响应: {response}")  # 打印完整响应
            return response.choices[0].message.content
        except Exception as e:
            return f"API 请求失败: {str(e)}"


# 客户服务代理
class CustomerServiceAgent(Agent):
    def process_message(self, message):
        print(f"{self.name} 正在处理消息: {message}")  # 打印调试信息
        # 明确职责：处理客户请求
        ask_description = "进行数据分析"
        
        # 构建新的消息内容
        self.message2 = "你现在是客服代理，请完善用户的请求，让数据分析同事能够根据任务给出准确的结果:\n" + message
        
        # 调用 DeepSeek API 进行数据分析
        result = self.call_deepseek_api(self.message2, ask_description)
        print(f"{self.name} 处理结果: {result}")  # 打印处理结果
        return {"task": ask_description, "result": result}  # 返回任务描述和结果


# 数据分析代理
class DataAnalysisAgent(Agent):
    def process_message(self, message):
        print(f"{self.name} 正在处理消息: {message}")  # 打印调试信息
        # 明确职责：进行数据分析
        task_description = "进行数据分析"
        
        # 构建新的消息内容
        self.message2 = "你现在正在进行数据分析，请完善一下客服代理给出的任务:\n" + message["result"]
        
        # 调用 DeepSeek API 进行数据分析
        result = self.call_deepseek_api(self.message2, task_description)
        print(f"{self.name} 分析结果: {result}")  # 打印处理结果
        
        # 返回任务描述和结果
        return {"task": task_description, "result": result}


# 市场营销代理
class MarketingAgent(Agent):
    def process_message(self, message):
        print(f"{self.name} 正在处理消息: {message}")  # 打印调试信息
        # 明确职责：制定营销策略
        task_description = "制定营销策略"
        
        # 构建新的消息内容
        self.message2 = "你现在正在制定营销策略，请根据数据分析结果提出建议:\n" + message["result"]
        
        # 调用 DeepSeek API 制定营销策略t
        result = self.call_deepseek_api(self.message2, task_description)
        print(f"{self.name} 制定策略: {result}")  # 打印处理结果
        
        # 返回任务描述和结果
        return {"task": task_description, "result": result}


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

    # 打印代理线程状态
    print(f"客户服务代理状态: {customer_service.is_alive()}")
    print(f"数据分析代理状态: {data_analysis.is_alive()}")
    print(f"市场营销代理状态: {marketing.is_alive()}")

    # 从终端读取一次客户请求
    request = input("请输入客户请求: ")
    if request.strip():  # 确保输入不为空
        print(f"发送请求: {request}")
        queue1.put(request)  # 将客户请求放入队列

    # 等待代理完成任务
    time.sleep(10)  # 根据任务复杂度调整等待时间

    # 打印队列状态
    print(f"queue1 剩余消息: {queue1.qsize()}")
    print(f"queue2 剩余消息: {queue2.qsize()}")
    print(f"queue3 剩余消息: {queue3.qsize()}")

    print("所有任务完成")