r"""
精益 SOP 智能助手 - Streamlit 应用
基于 TF-IDF 检索 + DeepSeek API，离线索引，在线问答
"""

import os
import sys
import pickle
from pathlib import Path
from typing import List, Dict, Tuple

import streamlit as st
import numpy as np
from openai import OpenAI

# ====== 配置 ======
KB_DIR = Path(__file__).parent / "knowledge_base"

# 页面配置
st.set_page_config(
    page_title="精益SOP智能助手",
    page_icon="factory",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义 CSS
st.markdown("""
<style>
    .chat-message { padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem; }
    .user-message { background-color: #e3f2fd; }
    .assistant-message { background-color: #f5f5f5; }
    .source-box {
        background-color: #fff8e1; padding: 0.5rem; border-radius: 0.3rem;
        border-left: 3px solid #ffc107; margin: 0.3rem 0; font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# ====== 加载知识库（缓存） ======

@st.cache_resource
def load_knowledge_base():
    """加载知识库文件"""
    try:
        with open(KB_DIR / "chunks.pkl", "rb") as f:
            chunks = pickle.load(f)
        with open(KB_DIR / "vectorizer.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        with open(KB_DIR / "tfidf_matrix.pkl", "rb") as f:
            tfidf_matrix = pickle.load(f)
        return chunks, vectorizer, tfidf_matrix
    except FileNotFoundError:
        return None, None, None


def search_chunks(query: str, chunks: List[Dict], vectorizer, tfidf_matrix, top_k: int = 5) -> List[Dict]:
    """用 TF-IDF 余弦相似度搜索"""
    # 将查询向量化
    query_vec = vectorizer.transform([query])

    # 计算余弦相似度
    from sklearn.metrics.pairwise import cosine_similarity
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # 获取 Top-K 结果
    top_indices = similarities.argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        if similarities[idx] > 0:  # 过滤掉完全不相关的结果
            results.append({
                "chunk": chunks[idx],
                "score": float(similarities[idx]),
            })

    return results


def format_context(results: List[Dict]) -> str:
    """格式化为上下文"""
    parts = []
    for i, r in enumerate(results, 1):
        chunk = r["chunk"]
        source = chunk["source"]
        parts.append(f"[{i}] 来源: {source}\n{chunk['text']}\n")
    return "\n---\n".join(parts)


def init_llm_client(api_key: str):
    """初始化 DeepSeek 客户端"""
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )


def ask_llm(client: OpenAI, query: str, context: str) -> str:
    """调用 DeepSeek API 生成回答"""
    system_prompt = """你是一位精益生产领域的专家助手，名叫「精益助手」。
你的任务是基于提供的文档内容，准确回答用户关于精益生产的问题。

回答规则：
1. 严格基于提供的文档内容回答，不要编造信息
2. 如果文档内容不足以回答问题，请明确说明
3. 回答时引用具体文档来源（如：根据《xxx》）
4. 用中文回答，语言简洁清晰
5. 在回答结尾，可以追问用户是否需要更详细的信息"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""以下是相关的精益文档内容：

{context}

---

请基于以上文档内容回答以下问题：
{query}"""},
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用 DeepSeek API 出错: {e}"


# ====== 侧边栏 ======

with st.sidebar:
    st.title("factory 精益SOP助手")
    st.markdown("---")

    # API Key
    st.subheader("key 配置")
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="输入你的 DeepSeek API Key",
        help="在 platform.deepseek.com 获取",
    )
    if api_key:
        st.success("API Key 已配置")
    else:
        st.warning("请配置 API Key 后方可使用问答功能")

    st.markdown("---")

    # 知识库状态
    st.subheader("database 知识库状态")
    chunks, vectorizer, tfidf_matrix = load_knowledge_base()
    if chunks:
        sources = sorted(set(c["source"] for c in chunks))
        st.success("知识库已加载")
        st.metric("文本块数量", len(chunks))
        st.metric("来源文件数", len(sources))
    else:
        st.error("知识库未找到")
        st.info("请先运行 build_knowledge_base.py 构建知识库")
        st.markdown("```bash\ncd 精益SOP助手\npython build_knowledge_base.py\n```")

    st.markdown("---")

    # 使用说明
    st.subheader("book 使用说明")
    st.markdown("""
    1. 输入 DeepSeek API Key
    2. 在聊天框输入问题
    3. 助手基于你的文档回答

    **示例问题：**
    - 七大浪费有哪些？
    - 如何做价值流程图？
    - 5S 的实施步骤是什么？
    - 生产线平衡如何计算？
    """)

    st.markdown("---")
    st.caption("v1.0 | 数据来源: 精益文件夹")


# ====== 主界面 ======

st.title("chat 精益SOP智能问答")
st.markdown("基于你的精益文档知识库，智能回答关于精益生产的问题")

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是精益助手\n\n我学习了你的精益文档，可以回答关于精益生产的问题。请问有什么可以帮助你的？"}
    ]

if "sources" not in st.session_state:
    st.session_state.sources = []

# 显示聊天历史
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and i < len(st.session_state.sources):
            src_list = st.session_state.sources[i]
            if src_list:
                with st.expander("查看引用来源", expanded=False):
                    for s in src_list:
                        st.markdown(
                            f'<div class="source-box">{s}</div>',
                            unsafe_allow_html=True,
                        )

# 聊天输入
if prompt := st.chat_input("请输入你的精益相关问题..."):
    if not api_key:
        st.error("请在侧边栏输入 DeepSeek API Key")
        st.stop()

    if not chunks:
        st.error("知识库未初始化。请先运行 build_knowledge_base.py")
        st.stop()

    # 用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 检索
    with st.status("检索知识库...") as status:
        results = search_chunks(prompt, chunks, vectorizer, tfidf_matrix, top_k=5)
        if not results:
            status.update(label="未找到相关文档", state="error")
            response = "抱歉，知识库中没有找到与你的问题相关的内容。"
            st.session_state.sources.append([])
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.stop()

        status.update(label=f"找到 {len(results)} 个相关片段", state="complete")

    # 生成回答
    with st.status("正在生成回答...") as status:
        context = format_context(results)
        client = init_llm_client(api_key)
        try:
            response = ask_llm(client, prompt, context)
            status.update(label="回答生成完成", state="complete")
        except Exception as e:
            status.update(label="生成失败", state="error")
            response = f"调用 DeepSeek API 失败: {e}"

    # 来源
    source_texts = [f"{r['chunk']['source']} (匹配度: {r['score']:.2f})" for r in results[:3]]
    st.session_state.sources.append(source_texts)

    # 显示回答
    with st.chat_message("assistant"):
        st.markdown(response)
        if source_texts:
            with st.expander("查看引用来源", expanded=False):
                for s in source_texts:
                    st.markdown(f'<div class="source-box">{s}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})

# 底部
st.markdown("---")
st.caption("提示：回答基于你的精益文档内容，如有疑问请核对原始文档")
