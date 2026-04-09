import os
import json
from typing import Annotated
from typing_extensions import TypedDict
import sys
# Thư viện LangChain & LangGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- BƯỚC 1: IMPORT HÀM TÌM KIẾM TỪ FILE TOOLS ---
# Giả sử bạn đã lưu code ở câu trước vào agent/tools/search_tools.py
from tools.search_tools import search_youtube_reviews, search_reddit_comments, search_vinfast_showrooms

# Bọc @tool để LangChain tự sinh JSON schema cho Qwen
@tool
def tool_search_youtube_reviews(car_model: str) -> str:
    """
    CHỈ SỬ DỤNG khi người dùng MỘT CÁCH RÕ RÀNG yêu cầu xem "video", "clip", "review" hoặc đánh giá từ các "reviewer",
    KHÔNG SỬ DỤNG tool này nếu người dùng hỏi về trải nghiệm thực tế về một khía cạnh nào đó hoặc bình luận text.
    Trả về tiêu đề, mô tả và Nguồn (URL).
    """
    return search_youtube_reviews(car_model)

@tool
def tool_search_reddit_comments(car_model: str, specific_query: str) -> str:
    """
    CHỈ SỬ DỤNG khi người dùng muốn biết "ý kiến", "cảm nhận", "bình luận", "lỗi" từ "người dùng thực tế" đang lái xe.
    KHÔNG SỬ DỤNG tool này để tìm video.
    Trả về các thread thảo luận và Nguồn (URL).
    """
    return search_reddit_comments(car_model, specific_query)

@tool
def tool_search_vinfast_showrooms(location: str) -> str:
    """
    CHỈ SỬ DỤNG khi người dùng muốn biết địa điểm mua xe, tìm showroom, đại lý VinFast, địa chỉ hoặc số hotline.
    Tham số 'location': Tên Tỉnh/Thành phố hoặc Quận/Huyện (VD: 'Hà Nội', 'Quận 1'). 
    Nếu người dùng CHƯA CUNG CẤP vị trí trong câu hỏi, hãy truyền vào một chuỗi rỗng "".
    Trả về thông tin Tên showroom, vị trí, hotline.
    """
    return search_vinfast_showrooms(location)
# Danh sách công cụ cấp cho Agent
tools = [tool_search_youtube_reviews, tool_search_reddit_comments, tool_search_vinfast_showrooms]

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
llm = ChatOpenAI(
    model="qwen3.5-flash", # Thay bằng qwen-plus hoặc model 3.6 cụ thể bạn đang có
    api_key=QWEN_API_KEY,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1", # URL chuẩn của Qwen API
    temperature=0.2
)

# Ràng buộc tools vào LLM
llm_with_tools = llm.bind_tools(tools)

# --- BƯỚC 3: XÂY DỰNG LANGGRAPH ---
# Định nghĩa State của Agent (lưu trữ lịch sử chat)
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Node: Gọi LLM
def chatbot_node(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Khởi tạo Graph
graph_builder = StateGraph(State)

# Thêm các Node
graph_builder.add_node("chatbot", chatbot_node)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# Điều hướng (Edges)
graph_builder.add_edge(START, "chatbot")
# tools_condition sẽ kiểm tra: nếu LLM gọi tool -> đi đến node tools, nếu không -> kết thúc (END)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot") # Chạy tool xong quay lại LLM để tổng hợp

# Compile thành một agent hoàn chỉnh
agent = graph_builder.compile()

# --- BƯỚC 4: VÒNG LẶP CHAT (REPL) ĐỂ TEST ---
def chat_loop():
    print("="*50)
    print("🤖 CHATBOT AGENT VINFAST ĐÃ KHỞI ĐỘNG!")
    print("Nhập 'exit' hoặc 'quit' để thoát.")
    print("="*50)
    
    # Khởi tạo System Prompt đúng như định hướng trong file Spec
    system_prompt = SystemMessage(content=(
        "Bạn là tư vấn viên ảo của VinFast. Nhiệm vụ của bạn là hỗ trợ khách hàng tìm hiểu mua xe. "
        "Bạn ĐƯỢC PHÉP và PHẢI dùng tool tìm kiếm để lấy review thực tế từ YouTube và Reddit. "
        "Tuyệt đối không bịa thông tin. Mọi câu trả lời dựa trên tool PHẢI trích dẫn nguồn URL."
    ))
    
    # State ban đầu chứa System Prompt
    current_state = {"messages": [system_prompt]}

    while True:
        user_input = input("\n🧑 Bạn: ")
        if user_input.lower() in ["exit", "quit"]:
            print("🤖 Agent: Tạm biệt! Hẹn gặp lại.")
            break
        if not user_input.strip():
            continue

        # Thêm câu hỏi của user vào state
        current_state["messages"].append(HumanMessage(content=user_input))
        
        # Dùng stream để dễ dàng theo dõi log từng node
        for event in agent.stream(current_state):
            for node_name, node_state in event.items():
                latest_message = node_state["messages"][-1]
                
                # LOG: In ra màn hình nếu Agent quyết định GỌI TOOL
                if isinstance(latest_message, AIMessage) and latest_message.tool_calls:
                    print("-" * 40)
                    print(f"🛠️  [LOG] LLM QUYẾT ĐỊNH GỌI TOOL:")
                    for tc in latest_message.tool_calls:
                        print(f"    Tool name: {tc['name']}")
                        print(f"    Arguments: {json.dumps(tc['args'], ensure_ascii=False)}")
                    print("-" * 40)

                # LOG: In ra câu trả lời cuối cùng của Agent
                elif isinstance(latest_message, AIMessage) and not latest_message.tool_calls:
                    print(f"🤖 Agent: {latest_message.content}")


if __name__ == "__main__":
    chat_loop()