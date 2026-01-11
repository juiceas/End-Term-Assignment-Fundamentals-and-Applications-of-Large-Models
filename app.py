"""
Streamlit Web前端
"""
import streamlit as st
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rag.rag_pipeline import RAGPipeline
from src.utils.logger import logger
from src.utils.config_loader import config


# 页面配置
st.set_page_config(
    page_title=config.get('streamlit.title', '红楼梦智能问答系统'),
    page_icon=config.get('streamlit.page_icon', '📖'),
    layout=config.get('streamlit.layout', 'wide'),
    initial_sidebar_state="expanded"
)


# 自定义CSS样式
st.markdown("""
<style>
    /* 主标题样式 */
    .main-title {
        text-align: center;
        color: #8B0000;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.5em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 副标题样式 */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    
    /* 聊天消息样式 */
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    
    .user-message {
        background-color: #E8F4F8;
        border-left: 5px solid #2196F3;
    }
    
    .assistant-message {
        background-color: #FFF3E0;
        border-left: 5px solid #FF9800;
    }
    
    .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 1.1em;
    }
    
    /* 来源文档样式 */
    .source-doc {
        background-color: #F5F5F5;
        padding: 0.8rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
        border-left: 3px solid #4CAF50;
        font-size: 0.9em;
    }
    
    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background-color: #F8F9FA;
    }
    
    /* 统计卡片样式 */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stat-number {
        font-size: 2em;
        font-weight: bold;
    }
    
    .stat-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_rag():
    """初始化RAG系统(缓存)"""
    try:
        rag = RAGPipeline()
        logger.info("RAG系统初始化成功")
        return rag
    except Exception as e:
        logger.error(f"RAG系统初始化失败: {str(e)}")
        st.error(f"系统初始化失败: {str(e)}")
        return None


def display_message(role: str, content: str, sources: list = None):
    """显示消息"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-header">👤 您的问题</div>
            <div>{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <div class="message-header">🤖 红楼知音</div>
            <div>{content}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示来源文档
        if sources:
            with st.expander(f"📚 参考来源 ({len(sources)}个相关文档)", expanded=False):
                for i, source in enumerate(sources, 1):
                    source_info = source.get('metadata', {})
                    source_text = source.get('text', '')
                    
                    st.markdown(f"""
                    <div class="source-doc">
                        <strong>来源 {i}:</strong> {source_info.get('source', '未知')}
                        <br>
                        <em>{source_text[:200]}...</em>
                    </div>
                    """, unsafe_allow_html=True)


def main():
    """主函数"""
    # 标题
    st.markdown('<h1 class="main-title">一级红学家</h1>', unsafe_allow_html=True)
#    st.markdown('<p class="subtitle">基于RAG技术的红楼梦知识库问答助手</p>', unsafe_allow_html=True)
    
    # 初始化RAG系统
    rag = initialize_rag()
    if not rag:
        st.stop()
    
    # 侧边栏
    with st.sidebar:
        st.markdown("## ⚙️ 系统设置")
        
        # 知识库统计
        try:
            stats = rag.vector_store.get_collection_stats()
            doc_count = stats.get('document_count', 0)
            
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{doc_count}</div>
                <div class="stat-label">知识库文档数</div>
            </div>
            """, unsafe_allow_html=True)
        except:
            pass
        
        st.markdown("---")
        
        # 检索参数
        st.markdown("### 🔍 检索设置")
        top_k = st.slider("相关文档数量", min_value=1, max_value=50, value=5)
        
        st.markdown("### 🎛️ 生成参数")
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        
        st.markdown("---")
        
        # 示例问题
        st.markdown("### 💡 示例问题")
        example_questions = [
            "尤二姐悲剧的内核",
            "贾宝玉的性格缺陷？",
            "林黛玉的脾气秉性",
            "红楼梦的主题思想",
            "薛宝钗和林黛玉的关系"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question}"):
                st.session_state['current_question'] = question
        
        st.markdown("---")
        
        # 清空历史
        if st.button("🗑️ 清空对话历史", type="secondary"):
            st.session_state['chat_history'] = []
            st.rerun()
    
    # 初始化会话状态
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    # 显示对话历史
    for message in st.session_state['chat_history']:
        display_message(
            message['role'],
            message['content'],
            message.get('sources')
        )
    
    # 输入框
    with st.container():
        col1, col2 = st.columns([6, 1])
        
        with col1:
            # 检查是否有示例问题被点击
            default_value = st.session_state.get('current_question', '')
            if default_value:
                del st.session_state['current_question']
            
            user_input = st.text_input(
                "请输入您的问题：",
                placeholder="例如: 贾宝玉是谁？",
                key="user_input",
                label_visibility="collapsed",
                value=default_value
            )
        
        with col2:
            submit_button = st.button("🚀 发送", type="primary", use_container_width=True)
    
    # 处理用户输入
    if submit_button and user_input:
        try:
            # 显示用户消息
            display_message("user", user_input)
            
            # 添加到历史
            st.session_state['chat_history'].append({
                'role': 'user',
                'content': user_input
            })
            
            # 显示加载动画
            with st.spinner('🤔 正在思考...'):
                # 调用RAG
                answer, sources = rag.ask(
                    user_input,
                    return_sources=True,
                    stream=False
                )
            
            # 显示回答
            display_message("assistant", answer, sources)
            
            # 添加到历史
            st.session_state['chat_history'].append({
                'role': 'assistant',
                'content': answer,
                'sources': sources
            })
            
            # 重新运行以清空输入框
            st.rerun()
            
        except Exception as e:
            error_msg = f"抱歉，处理您的问题时出现错误: {str(e)}"
            st.error(error_msg)
            logger.error(f"问答处理失败: {str(e)}")
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.9em;'>
         基于Python + RAG技术构建 |  硅基流动渠道API驱动 |  CNKI红楼梦知识库
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
