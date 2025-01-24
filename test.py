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
        self.running = True  # 控制代理是否继续运行

    def run(self):
        while self.running:
            if not self.inbox.empty():
                message = self.inbox.get()
                print(f"{self.name} 收到消息: {message}")
                result = self.process_message(message)
                if self.outbox and result:
                    self.outbox.put(result)  # 将处理结果发送给下一个代理
            time.sleep(1)  # 模拟处理时间

    def stop(self):
        """停止代理运行"""
        self.running = False

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
        task_description = "处理客户请求"
        
        # 构建新的消息内容
        self.message2 = "你现在是客服代理，请完善用户的请求，让产品策划同事能够根据任务给出准确的结果:\n" + message
        
        # 调用 DeepSeek API 进行处理
        result = self.call_deepseek_api(self.message2, task_description)
        print(f"{self.name} 处理结果: {result}")  # 打印处理结果
        return {"task": task_description, "result": result}  # 返回任务描述和结果


# 产品策划代理
class ProductPlanningAgent(Agent):
    def process_message(self, message):
        print(f"{self.name} 正在处理消息: {message}")  # 打印调试信息
        # 明确职责：进行产品策划
        task_description = "进行产品策划"
        
        # 构建新的消息内容
        self.message2 = "你现在正在进行产品策划，请根据客服代理给出的任务提出产品设计方案:\n" + message["result"]
        
        # 调用 DeepSeek API 进行产品策划
        result = self.call_deepseek_api(self.message2, task_description)
        print(f"{self.name} 策划结果: {result}")  # 打印处理结果
        return {"task": task_description, "result": result}


# 代码开发代理
class CodeDevelopmentAgent(Agent):
    def process_message(self, message):
        print(f"{self.name} 正在处理消息: {message}")  # 打印调试信息
        # 明确职责：进行代码开发或重做
        if message.get("task") == "代码开发重做":
            task_description = "代码开发重做"
            self.message2 = "你现在需要重新开发代码，请根据测试反馈的错误信息进行修改:\n" + message["result"]
        else:
            task_description = "进行代码开发"
            self.message2 = "你现在正在进行代码开发，请根据产品策划方案编写代码，输出命令行可以复制的代码:\n" + message["result"]
        
        # 调用 DeepSeek API 进行代码开发或重做
        result = self.call_deepseek_api(self.message2, task_description)
        print(f"{self.name} 开发结果: {result}")  # 打印处理结果
        return {"task": task_description, "result": result}


# 运行测试代理
class TestingAgent(Agent):
    def process_message(self, message):
        print(f"{self.name} 正在处理消息: {message}")  # 打印调试信息
        # 明确职责：进行运行测试
        task_description = "进行运行测试"
        
        # 构建新的消息内容
        self.message2 = "你现在正在进行运行测试，请根据代码开发结果进行运行测试:\n" + message["result"] + "\n代码无误，则返回'通过'，代码有误则返回错误原因"
        
        # 调用 DeepSeek API 进行运行测试
        result = self.call_deepseek_api(self.message2, task_description)
        print(f"{self.name} 测试结果: {result}")  # 打印处理结果

        # 检查测试结果是否包含错误
        if "通过" not in result:
            print(f"{self.name} 检测到错误，返回给代码开发代理重做。")
            return {"task": "代码开发重做", "result": result}  # 返回错误信息给代码开发代理
        else:
            print(f"{self.name} 测试通过，任务完成。")
            return None  # 测试通过，不再发送消息


# 主程序
if __name__ == "__main__":
    # 创建消息队列
    queue1 = queue.Queue()  # 客户服务 -> 产品策划
    queue2 = queue.Queue()  # 产品策划 -> 代码开发
    queue3 = queue.Queue()  # 代码开发 -> 运行测试
    queue4 = queue.Queue()  # 运行测试 -> 代码开发（重做）或结束

    # 创建代理
    customer_service = CustomerServiceAgent("客户服务代理", queue1, queue2)
    product_planning = ProductPlanningAgent("产品策划代理", queue2, queue3)
    code_development = CodeDevelopmentAgent("代码开发代理", queue3, queue4)
    testing = TestingAgent("运行测试代理", queue4, queue3)  # 测试失败时返回给代码开发代理

    # 启动代理
    customer_service.start()
    product_planning.start()
    code_development.start()
    testing.start()

    # 打印代理线程状态
    print(f"客户服务代理状态: {customer_service.is_alive()}")
    print(f"产品策划代理状态: {product_planning.is_alive()}")
    print(f"代码开发代理状态: {code_development.is_alive()}")
    print(f"运行测试代理状态: {testing.is_alive()}")

    # 从终端读取一次客户请求
    request = input("请输入客户请求: ")
    if request.strip():  # 确保输入不为空
        print(f"发送请求: {request}")
        queue1.put(request)  # 将客户请求放入队列

    # 等待代理完成任务
    time.sleep(30)  # 根据任务复杂度调整等待时间

    # 停止所有代理
    customer_service.stop()
    product_planning.stop()
    code_development.stop()
    testing.stop()

    # 打印队列状态
    print(f"queue1 剩余消息: {queue1.qsize()}")
    print(f"queue2 剩余消息: {queue2.qsize()}")
    print(f"queue3 剩余消息: {queue3.qsize()}")
    print(f"queue4 剩余消息: {queue4.qsize()}")

    print("所有任务完成")