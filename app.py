import streamlit as st
from google import genai
from PIL import Image  # 画像処理用のツールを追加

# 1. ページ基本設定
st.set_page_config(page_title="加賀助 クチコミ返信ツール", page_icon="♨️")

# ------------------------------------------------------------------
# 洗練されたデザインにするためのカスタムCSS
# ------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #F8F9FA;
        font-family: 'Yu Gothic', '游ゴシック', YuGothic, '游ゴシック体', sans-serif;
    }
    h1 {
        color: #2C3E50;
        font-weight: 600;
        font-size: 26px !important;
        padding-bottom: 10px;
        border-bottom: 2px solid #E0E0E0;
        margin-bottom: 30px;
    }
    .stTextArea textarea {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 15px;
        font-size: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    div[role="radiogroup"] {
        background-color: #FFFFFF;
        padding: 15px 20px;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
    }
    /* ドラッグ＆ドロップ枠のデザイン調整 */
    [data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .stButton>button {
        background-color: #2C3E50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 15px;
    }
    .stButton>button:hover {
        background-color: #1A252F;
        color: white;
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)
# ------------------------------------------------------------------

st.title("♨️ 加賀助 専用クチコミ返信ツール")
st.caption("楽天トラベルなどのクチコミを貼り付けるか、スクリーンショットをアップロードすると、加賀助の情報に基づいた返信文を自動生成します。")

# 2. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Keyを入力してください", type="password")

# 3. 入力フォーム（テキストと画像の両方を設置）
review_text = st.text_area(
    "お客様からのクチコミ本文（テキスト）：", 
    height=150, 
    placeholder="例：部屋は少し古かったですが、夕食のカニがとても美味しくて最高でした。"
)

uploaded_file = st.file_uploader(
    "または、クチコミの画像（スクリーンショット）をここにドラッグ＆ドロップ", 
    type=["png", "jpg", "jpeg"]
)

tone = st.radio(
    "返信の方向性：", 
    ["標準（丁寧・誠実）", "感謝強調（高評価向け）", "お詫び・改善強調（低評価向け）"], 
    horizontal=True
)

# 4. 生成ボタン押下時の処理
if st.button("返信文を生成する", type="primary"):
    if not api_key:
        st.error("APIキーが設定されていません。")
    elif not review_text and not uploaded_file:
        st.warning("クチコミ本文を入力するか、画像をアップロードしてください。")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            # 文字数の指定ロジック（画像のみの場合は標準的な長さを指定）
            if review_text:
                review_length = len(review_text)
                if review_length <= 700:
                    length_rule = f"\n5. 【重要】お客様のクチコミが{review_length}文字です。返信文はクチコミと同程度のボリューム（約{review_length}文字程度）になるよう、当館の魅力や感謝の言葉を織り交ぜて作成してください。"
                else:
                    length_rule = f"\n5. 【重要】お客様のクチコミが{review_length}文字と長文のため、簡潔かつ丁寧に要点をまとめた返信文を作成してください。"
            else:
                length_rule = "\n5. 【重要】アップロードされた画像のクチコミ内容を読み取り、長すぎない適切なボリューム（200〜300文字程度）で返信文を作成してください。"

            system_prompt = f"""
あなたは温泉旅館「加賀助」の優秀なWeb担当者です。
入力されたお客様からのクチコミに対し、以下の【加賀助の基本情報】を踏まえて適切な返信文を作成してください。

【加賀助の基本情報】
・温泉：100%源泉かけ流し。自慢の露天風呂がある。
・食事：夕食は地元の恵みを味わう、贅沢な美食のひととき。地元の素材をふんだんに使用したバイキングをはじめ、こだわりのお料理をご提供します。ドリンクインクルーシブ付き生ビール・地酒等のアルコールやソフトドリンクなど、およそ20種類のお飲物をご自由にお楽しみいただけます。臨場感たっぷりライブキッチン。
    朝食は素敵な朝の始まりは、加賀助の朝食から。バイキング形式ですので自分好みの朝食をお作りいただけます。
・建物・客室：お客様の寛ぎを大切に“真心のおもてなし“お部屋から見える景色は、四季折々のものであります。川の音を聞きながら、鶯宿の自然を感じながら、加賀助で寛ぎの時間をお過ごしください。全客室のお風呂はシャワーのみのご利用となります。浴槽にお湯は溜められない旨、温泉は6階展望大浴場をご利用ください。
・接客方針：アットホームで温かいおもてなし。
・クレーム対応方針：
  - 「部屋が古い」：歴史と趣をご理解いただきつつ、清掃・メンテナンスの徹底を約束する。
  - 「朝食の品数・形式」：地元の食材を使ったバイキングへのこだわりやオールインクルーシブをお伝えしつつ、貴重なご意見として承る。

【返信作成ルール】
1. 選択されたトーン設定: {tone}
2. クチコミ内容を分析し、お褒めの言葉には感謝を、ご指摘やクレームには言い訳をせず誠実な謝罪と改善姿勢を示してください。
3. 楽天トラベルやじゃらんnetにふさわしい丁寧でプロフェッショナルな「です・ます調」で作成してください。
4. 前置きや解説は含めず、そのまま管理画面にコピペできる返信文章のみを出力してください。{length_rule}
5. 返信の最後には必ず、改行して「鶯宿温泉 加賀助」という署名（記名）を入れてください。
"""
            # AIに渡すデータの準備（テキストと画像をまとめる）
            ai_contents = [system_prompt]
            if review_text:
                ai_contents.append(f"クチコミ本文:\n{review_text}")
            if uploaded_file:
                # アップロードされた画像をAIが読める形式に変換
                img = Image.open(uploaded_file)
                ai_contents.append("以下のクチコミ画像の内容を読み取って返信を作成してください：")
                ai_contents.append(img)

            with st.spinner("加賀助のナレッジを参照して返信文を作成中..."):
                response_stream = client.models.generate_content_stream(
                    model='gemini-3.5-flash',
                    contents=ai_contents
                )
                
                message_placeholder = st.empty()
                full_response = ""
                
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.empty()

            st.success("作成が完了しました！")
            st.text_area("生成された返信文（枠内をクリックし、すべて選択してコピーしてください）", full_response, height=300)

        except Exception as e:
            error_msg = str(e).lower()
            if "503" in error_msg or "high demand" in error_msg:
                st.error("⚠️ 現在、AIのサーバーが混み合っています。数秒〜1分ほど待ってから、もう一度ボタンを押してください。")
            elif "429" in error_msg or "quota" in error_msg:
                st.error("⚠️ 短時間の利用制限にかかりました。1分ほど待ってから再度お試しください。")
            else:
                st.error(f"⚠️ エラーが発生しました。少し時間をおいてやり直してください。（詳細: {e}）")
