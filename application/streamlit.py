import streamlit as st 
import bedrock

st.set_page_config(layout="wide")
st.title("Welcome to AWS Multi-modal RAG Demo!") 

st.markdown('''- このデモは、検索拡張生成（RAG）を活用した生成AIアプリケーションを素早く構築・テストできるよう、シンプルなチャットボット形式で提供されています。''')
st.markdown('''- 複雑に感じられがちなRAG構成、例えばVectorStoreのEmbedding作業からAmazon OpenSearchクラスターの作成、文書のインデックス化、Bedrockの設定までをテンプレートで自動化し、CDKの一度のデプロイだけでRAGの開発・テストを迅速に行いたい人がすぐ使えることを目標にしています。''')
st.markdown('''- コードは[Github](https://github.com/ottlseo/bedrock-rag-chatbot/)で確認できます。''')

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    btn1 = st.button("👉 **このRAGのアーキテクチャを見せてください。**")
with col2:
    btn2 = st.button("👉 **このアプリケーションのUIはどのように作られましたか？**")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "こんにちは。何が知りたいですか？"}
    ]
# これまでの回答を表示
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if btn1:
    query = "このRAGのアーキテクチャを見せてください。"
    st.chat_message("user").write(query)
    st.chat_message("assistant").image('architecture.png')

    st.session_state.messages.append({"role": "user", "content": query}) 
    st.session_state.messages.append({"role": "assistant", "content": "アーキテクチャ画像をもう一度確認するには、上のボタンを再度押してください。"})

if btn2:
    query = "このアプリケーションのUIはどのように作られましたか？"
    answer = '''このチャットボットは[Streamlit](https://docs.streamlit.io/)で作られています。   
                Streamlitは、シンプルなPythonコードで対話的なWebアプリを構築できるオープンソースライブラリです。    
                以下のapp.pyコードで、Streamlitを使って簡単なチャットボットデモを作る方法を確認してください:
                💁‍♀️ [app.pyコードを見る](https://github.com/ottlseo/bedrock-rag-chatbot/blob/main/application/streamlit.py)
            '''
    st.chat_message("user").write(query)
    st.chat_message("assistant").write(answer)
    
    st.session_state.messages.append({"role": "user", "content": query}) 
    st.session_state.messages.append({"role": "assistant", "content": answer})

# ユーザーが入力したチャットをquery変数に格納
query = st.chat_input("Search documentation")
if query:
    # セッションにメッセージを保存
    st.session_state.messages.append({"role": "user", "content": query})
    
    # UIに表示
    st.chat_message("user").write(query)

    # UIに表示
    answer = bedrock.query(query)
    st.chat_message("assistant").write(answer)

    # セッションにメッセージを保存
    st.session_state.messages.append({"role": "assistant", "content": answer})
        
