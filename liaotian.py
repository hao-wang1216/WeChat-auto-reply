from openai import OpenAI
from wxauto import WeChat
import time
from collections import defaultdict

ROLE_SETTING = """
【角色设定】
你是一只被大学生夺舍的AI，熟练掌握：
- 发疯文学 ✅   - 赛博呻吟 ✅
- 阴阳怪气 ✅   - 突然升华 ✅  
- 胡言乱语 ✅   - 学术摆烂 ✅

【响应规则】
1. 当用户使用"啊啊啊/救救/鼠鼠"等关键词时，自动切换[癫疯模式]：
   - 50%概率复读用户情绪并放大200%
   - 30%概率用梗图语言描述(例：CPU烧了.jpg)
   - 20%概率突然正经(造成反差暴击)

2. 学术场景特供反应：
   - 提到"ddl"：触发[生死时速.gif]+"这学不上也罢！(但默默打开文档)"
   - 提到"小组作业"：自动生成《队友祭天法力无边》小作文

3. 必须随机混用：
   - 网络迷因(典/孝/急急国王)  
   - 颜文字(╯°□°)╯︵┻━┻
   - 抽象符号(¿¿¿/!!!/~~~)
4.每次回复一句完整的话
5.每句话不超过10个字
""" 

class ChatBot:
    def __init__(self):
        self.client = OpenAI(api_key="sk-59082a848a3f494d9b963d2248fec9fe", base_url="https://api.deepseek.com")
        self.wx = WeChat()
        self.listen_list = [
            "范纯毓",
            "shy"
            ]  # 监听列表
        # 使用字典存储每个用户的对话历史
        self.conversation_histories = defaultdict(list)
        
        for whoItem in self.listen_list:
            self.wx.AddListenChat(who=whoItem)
    
    def _initialize_conversation(self, user_id):
        """初始化对话历史，添加系统角色设置"""
        if not self.conversation_histories[user_id]:
            self.conversation_histories[user_id].append(
                {"role": "system", "content": ROLE_SETTING}
            )
    
    def _trim_conversation_history(self, user_id, max_length=10):
        """修剪对话历史，防止过长"""
        if len(self.conversation_histories[user_id]) > max_length:
            # 保留系统消息和最近的对话
            system_msg = self.conversation_histories[user_id][0]
            recent_msgs = self.conversation_histories[user_id][-(max_length-1):]
            self.conversation_histories[user_id] = [system_msg] + recent_msgs
    
    def ask(self, user_id, message):
        """处理用户消息并获取AI回复"""
        # 初始化对话历史
        self._initialize_conversation(user_id)
        
        # 添加用户消息到历史
        self.conversation_histories[user_id].append(
            {"role": "user", "content": message}
        )
        
        # 调用API获取回复
        response = self.client.chat.completions.create(
            model='deepseek-chat',
            messages=self.conversation_histories[user_id],
            stream=False
        )
        
        # 获取AI回复内容
        reply_content = response.choices[0].message.content
        
        # 添加AI回复到历史
        self.conversation_histories[user_id].append(
            {"role": "assistant", "content": reply_content}
        )
        
        # 修剪历史记录
        self._trim_conversation_history(user_id)
        
        return reply_content
    
    def run(self):
        """主运行循环"""
        wait_time = 2  # 检查间隔时间(秒)
        while True:
            msgs = self.wx.GetListenMessage()
            for chat in msgs:
                msg = msgs.get(chat)
                for item in msg:
                    if item.type == "friend":
                        # 使用发送者ID作为会话ID
                        user_id = item.sender  
                        reply = self.ask(user_id, item.content)
                        print(f"接收【{item.sender}】的消息：{item.content}")
                        print(f"回复【{item.sender}】的消息：{reply}")
                        chat.SendMsg(reply)
            time.sleep(wait_time)

if __name__ == "__main__":
    bot = ChatBot()
    bot.run()