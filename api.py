"""
Flask REST API 后端服务
为前端提供问答和统计接口
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rag.rag_pipeline import RAGPipeline
from src.utils.logger import logger
from src.utils.config_loader import config

# 初始化Flask应用
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)  # 启用CORS支持

# 初始化RAG系统
rag_pipeline = None

def init_rag():
    """初始化RAG系统"""
    global rag_pipeline
    try:
        rag_pipeline = RAGPipeline()
        logger.info("RAG系统初始化成功")
        return True
    except Exception as e:
        logger.error(f"RAG系统初始化失败: {str(e)}")
        return False


@app.route('/')
def index():
    """提供前端页面"""
    return send_from_directory('frontend', 'index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    问答接口
    请求体:
    {
        "question": "问题内容",
        "top_k": 5,
        "temperature": 0.7
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'error': '请提供问题内容'
            }), 400
        
        question = data['question']
        top_k = data.get('top_k', 5)
        temperature = data.get('temperature', 0.7)
        
        logger.info(f"收到问题: {question}")
        
        # 调用RAG系统
        answer, sources = rag_pipeline.ask(
            question,
            return_sources=True,
            stream=False,
            top_k=top_k,
            temperature=temperature
        )
        
        # 格式化来源文档
        formatted_sources = []
        for source in sources:
            formatted_sources.append({
                'text': source.get('text', ''),
                'metadata': source.get('metadata', {})
            })
        
        return jsonify({
            'answer': answer,
            'sources': formatted_sources
        })
        
    except Exception as e:
        logger.error(f"问答处理失败: {str(e)}")
        return jsonify({
            'error': f'处理问题时出错: {str(e)}'
        }), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    """
    知识库统计接口
    """
    try:
        stats_data = rag_pipeline.vector_store.get_collection_stats()
        return jsonify({
            'document_count': stats_data.get('document_count', 0),
            'status': 'ready'
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({
            'document_count': 0,
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'rag_initialized': rag_pipeline is not None
    })


if __name__ == '__main__':
    # 初始化RAG系统
    print("正在初始化RAG系统...")
    if init_rag():
        print(" RAG系统初始化成功")
        print("\n" + "=" * 50)
        print(" 服务器启动成功!")
        print("=" * 50)
        print(f" 访问地址: http://localhost:5000")
        print(f" API文档: http://localhost:5000/api/health")
        print("=" * 50 + "\n")
        
        # 启动服务器
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    else:
        print(" RAG系统初始化失败，请检查配置和知识库")
        sys.exit(1)
