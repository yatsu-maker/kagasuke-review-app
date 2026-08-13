import streamlit as st
from google import genai

# 1. ページ基本設定
st.set_page_config(page_title="加賀助 クチコミ返信ツール", page_icon="♨️")
st.title("♨️ 加賀助 専用クチコミ返信ツール")
st.caption("楽天トラベルなどのクチコミを貼り付けると、加賀助の情報に基づいた返信文を自動生成します。")

import streamlit as st
from google import genai

# 1. ページ基本設定
st.set_page_config(page_title="加賀助 クチコミ返信ツール", page_icon="♨️", layout="centered")

# ------------------------------------------------------------------
# ★ここから追加：洗練されたデザインにするためのカスタムCSS
# ------------------------------------------------------------------
st.markdown("""
# ------------------------------------------------------------------
# ★ここから追加：洗練されたデザインにするためのカスタムCSS
# ------------------------------------------------------------------
st.markdown("""
<style>
    /* 全体の背景色とフォント（游ゴシックに変更） */
    .stApp {
        background-color: #F8F9FA;
        font-family: 'Yu Gothic', '游ゴシック', YuGothic, '游ゴシック体', sans-serif;
    }
    
    /* タイトルのスタイル（文字サイズを小さくして改行を防ぐ） */
    h1 {
        color: #2C3E50;
        font-weight: 600;
        font-size: 26px !important; /* ←ここで文字サイズを小さく調整しています */
        padding-bottom: 10px;
        border-bottom: 2px solid #E0E0E0;
        margin-bottom: 30px;
    }
    
    /* 入力枠（テキストエリア）のスタイル：白背景、角丸、うっすら影をつける */
    .stTextArea textarea {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 15px;
        font-size: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* トーン選択（ラジオボタン）の枠を整える */
    div[role="radiogroup"] {
        background-color: #FFFFFF;
        padding: 15px 20px;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
    }

    /* 生成ボタンのスタイル：ダークネイビー、立体感、マウスオンでフワッと動く */
    .stButton>button {
        background-color: #2C3E50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        width: 100%; /* ボタンを横幅いっぱいに広げる */
    }
    
    /* ボタンにマウスを乗せたときの動き */
    .stButton>button:hover {
        background-color: #1A252F;
        color: white;
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px); /* 少し上に浮く */
    }
</style>
""", unsafe_allow_html=True)
# ------------------------------------------------------------------
# ★追加ここまで
# ------------------------------------------------------------------


# 2. APIキーの設定（アプリの設定画面から安全に読み込みます）
# （※これ以降のコードは今のままで変更不要です）
api_key = st.secrets.get("GEMINI_API_KEY", "")
# ...続く...



# 2. APIキーの設定（アプリの設定画面から安全に読み込みます）
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    api_key = st.sidebar.text_input("Gemini API Keyを入力してください", type="password")

# 3. 入力フォーム
review_text = st.text_area(
    "お客様からのクチコミ本文：", 
    height=150, 
    placeholder="例：部屋は少し古かったですが、夕食のカニがとても美味しくて最高でした。"
)

# 返信のトーン選択
tone = st.radio(
    "返信の方向性：", 
    ["標準（丁寧・誠実）", "感謝強調（高評価向け）", "お詫び・改善強調（低評価向け）"], 
    horizontal=True
)

# 4. 生成ボタン押下時の処理
if st.button("返信文を生成する", type="primary"):
    if not api_key:
        st.error("APIキーが設定されていません。")
    elif not review_text:
        st.warning("クチコミ本文を入力してください。")
    else:
        try:
            # 新しいSDK（google-genai）の通信方式
            client = genai.Client(api_key=api_key)
            
            # ★ 追加ロジック：クチコミの文字数を判定して指示を切り替える
            review_length = len(review_text)
            if review_length <= 700:
                target_length = review_length * 2
                length_rule = f"\n5. 【重要】お客様のクチコミが{review_length}文字です。返信文はその約2倍（{target_length}文字程度）のボリュームになるよう、当館の魅力や感謝の言葉をしっかり肉付けして作成してください。"
            else:
                length_rule = f"\n5. 【重要】お客様のクチコミが{review_length}文字と長文のため、簡潔かつ丁寧に要点をまとめた返信文を作成してください（無理に2倍にする必要はありません）。"

            # 加賀助のナレッジを組み込んだプロンプト
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
4. 前置きや解説は含めず、そのまま楽天トラベルの管理画面にコピペできる返信文章のみを出力してください。{length_rule}
"""

            with st.spinner("加賀助のナレッジを参照して返信文を作成中..."):
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=[system_prompt, f"クチコミ本文:\n{review_text}"]
                )

            st.success("作成が完了しました！")
            
            # ★ 修正箇所：横に伸びないように「テキストエリア（高さ300px）」で表示する
            st.text_area("生成された返信文（枠内をクリックし、すべて選択してコピーしてください）", response.text, height=300)

        except Exception as e:
            error_msg = str(e).lower()
            if "503" in error_msg or "high demand" in error_msg:
                st.error("⚠️ 現在、AIのサーバーが混み合っています。数秒〜1分ほど待ってから、もう一度ボタンを押してください。")
            elif "429" in error_msg or "quota" in error_msg:
                st.error("⚠️ 短時間の利用制限にかかりました。1分ほど待ってから再度お試しください。")
            else:
                st.error(f"⚠️ エラーが発生しました。少し時間をおいてやり直してください。（詳細: {e}）")
