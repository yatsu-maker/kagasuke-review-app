import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="加賀助 クチコミ返信ツール", page_icon="♨️")

st.markdown("""
<style>
    .stApp { background-color: #F8F9FA; font-family: 'Yu Gothic', '游ゴシック', sans-serif; }
    h1 { color: #2C3E50; font-weight: 600; font-size: 26px !important; padding-bottom: 10px; border-bottom: 2px solid #E0E0E0; margin-bottom: 30px; }
    .stTextArea textarea { background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 8px; padding: 15px; font-size: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    div[role="radiogroup"] { background-color: #FFFFFF; padding: 15px 20px; border: 1px solid #E0E0E0; border-radius: 8px; }
    [data-testid="stFileUploadDropzone"] { background-color: #FFFFFF; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    [data-testid="stForm"] { background-color: transparent; border: none; padding: 0; }
    .stButton>button { background-color: #2C3E50; color: white; border-radius: 8px; padding: 10px 24px; font-weight: bold; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; margin-top: 5px; }
    .stButton>button:hover { background-color: #1A252F; box-shadow: 0 6px 8px rgba(0,0,0,0.15); transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

st.title("♨️ 加賀助 専用クチコミ返信ツール")
st.caption("クチコミを貼り付けるか、画像をアップロードすると、加賀助の情報に基づいた返信文を自動生成します。")

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key: api_key = st.sidebar.text_input("Gemini API Key", type="password")

with st.form("review_form"):
    review_text = st.text_area("お客様からのクチコミ本文（テキスト）：", height=150)
    
    uploaded_file = st.file_uploader("クチコミの画像（スクリーンショット）を「コピーして貼り付け」または\n「ドラッグ＆ドロップ」", type=["png", "jpg", "jpeg"])
    # ★スタッフ向けの注意書きを追加
    st.caption("⚠️ **ご注意**：AIが文字を視覚的に解析するため、画像の読み取りはテキスト入力よりも生成に時間がかかります。")
    
    tone = st.radio("返信の方向性：", ["標準（丁寧・誠実）", "感謝強調（高評価向け）", "お詫び・改善強調（低評価向け）"], horizontal=True)
    
    st.caption("💡 **ヒント**：入力後にキーボードの **Ctrl ＋ Enter**（Macは ⌘ ＋ Enter）を押すことでも生成をスタートできます。")
    submitted = st.form_submit_button("返信文を生成する", type="primary")

if submitted:
    if not api_key: st.error("APIキーが設定されていません。")
    elif not review_text and not uploaded_file: st.warning("クチコミ本文を入力するか、画像をアップロードしてください。")
    else:
        try:
            client = genai.Client(api_key=api_key)
            if review_text:
                review_length = len(review_text)
                target_length = int(review_length * 1.5)
                length_rule = f"\n5. 【重要】返信文は元のクチコミの約1.5倍（約{target_length}文字）のボリュームになるようしっかり肉付けして作成してください。" if review_length <= 700 else "\n5. 【重要】長文のため簡潔に要点をまとめて作成してください。"
            else:
                length_rule = "\n5. 【重要】画像から読み取ったクチコミ本文の文字数を把握し、その約1.5倍のボリュームになるようしっかり肉付けして作成してください。"

            system_prompt = f"""あなたは温泉旅館「加賀助」のWeb担当者です。以下の情報を踏まえて返信を作成してください。
【加賀助の基本情報】
・温泉：100%源泉かけ流し。自慢の露天風呂がある。
・食事：夕食は地元の素材をふんだんに使用したバイキング等。ドリンクインクルーシブ付き。朝食はバイキング形式。
・建物・客室：川の音を聞きながら寛ぐ空間。全客室のお風呂はシャワーのみ（温泉は6階展望大浴場）。
・接客方針：アットホームで温かいおもてなし。
・クレーム対応：「部屋が古い」歴史をご理解いただきつつ清掃徹底を約束。「朝食の品数」こだわりをお伝えし貴重な意見として承る。
【返信作成ルール】
1. トーン: {tone}
2. 誠実な謝罪と改善姿勢、または感謝を示す。
3. 丁寧な「です・ます調」で作成。
4. 返信文章のみを出力。{length_rule}
5. 最後に改行して「鶯宿温泉 加賀助」と記名する。"""

            ai_contents = [system_prompt]
            if review_text: ai_contents.append(f"クチコミ本文:\n{review_text}")
            if uploaded_file: ai_contents.extend(["以下の画像を読み取って返信を作成してください：", Image.open(uploaded_file)])

            with st.spinner("作成中..."):
                response_stream = client.models.generate_content_stream(model='gemini-3.5-flash', contents=ai_contents)
                placeholder = st.empty()
                full_response = ""
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        placeholder.markdown(full_response + "▌")
                placeholder.empty()
            st.success("完了しました！")
            st.text_area("生成された返信文", full_response, height=300)
        except Exception as e: st.error(f"⚠️ エラーが発生しました。時間を置いてお試しください。詳細: {e}")
