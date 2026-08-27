import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

st.title("📱 複数一括×おまかせ対応！ショート動画台本メーカー")
st.write("ジャンルを『おまかせ』にすれば、AIが今バズる人間味のあるネタを完全ランダムで考えてくれます。")

api_key = st.sidebar.text_input("Gemini API Keyを入力してください", type="password")

# 1. ユーザー入力エリア（おまかせ対応の説明を追加）
genre = st.text_input("動画のジャンル（『おまかせ』や空欄でもOK）", "おまかせ")
atmosphere = st.text_input("どんな感じの動画がいいか（『おまかせ』や空欄でもOK）", "おまかせ")
target_seconds = st.selectbox("動画の目標長さ", [15, 30, 60], index=1)

# 一度に作る本数の指定（1〜5本）
num_scripts = st.slider("一度に作成する動画の本数", min_value=1, max_value=5, value=3)

intro_text = "皆さんこんにちは、ドカンパです"
outro_text_1 = "チャンネル登録と高評価よろしくお願いします"
outro_text_2 = "ではまた！バイバーイ"

if st.button(f"台本を {num_scripts} 本一括生成する"):
    if not api_key:
        st.error("左側のサイドバーにGeminiのAPIキーを入力してください。")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.6-flash')
            
            # おまかせ判定
            final_genre = genre if (genre.strip() and genre != "おまかせ") else "今ネットでバズりそうな、人間味のある面白いトレンドネタ（あるある、雑学、心理学、ライフハックなど何でも可）"
            final_atmosphere = atmosphere if (atmosphere.strip() and atmosphere != "おまかせ") else "共感できる、クスッと笑える、テンポが良い"
            
            # プロンプトの構築
            prompt = f"""
            あなたはTikTokやYouTube Shortsで毎日数十万再生される人気クリエイターとして、人間が日常で感じる「あるある」や「ユーモア」を盛り込んだショート動画のネタを【合計 {num_scripts} 本】考えてください。
            
            【超重要ルール】
            それぞれの動画の内容や切り口、テーマ、ジャンルは、すべて全く異なるエピソードやネタにしてください。（同じような話の使い回しは絶対に禁止です）
            AI特有の不自然な解説や無機質な正論は禁止です。
            
            【動画1本あたりの条件】
            ・ジャンル: {final_genre}
            ・雰囲気: {final_atmosphere}
            ・長さ: {target_seconds}秒に収まるテンポ
            
            【動画1本あたりの構成ルール】
            1. 最初の一行は必ず「{intro_text}」にする。
            2. 最後は必ず順番に「{outro_text_1}」「{outro_text_2}」にする。
            3. メインの話し手は「ドカンパ」にする。
            
            【出力フォーマット】
            必ず以下のCSV形式のみで出力してください。解説、装飾文字、バッククォート(```)などは一切含めないでください。
            各動画の区切りとして、行の先頭に「---」だけの行を入れて区切ってください。
            
            出力例：
            ドカンパ,皆さんこんにちは、ドカンパです
            ドカンパ,（ネタ1の内容）
            ドカンパ,チャンネル登録と高評価よろしくお願いします
            ドカンパ,ではまた！バイバーイ
            ---
            ドカンパ,皆さんこんにちは、ドカンパです
            ドカンパ,（ネタ2の内容、ネタ1とは全く違う話・違うジャンル）
            ドカンパ,チャンネル登録と高評価よろしくお願いします
            ドカンパ,ではまた！バイバーイ
            """
            
            with st.spinner(f"{num_scripts}本の異なるネタを計算中..."):
                response = model.generate_content(prompt)
                raw_output = response.text.strip()
                
                # 余計なマークダウン装飾を除去
                raw_output = raw_output.replace("```csv", "").replace("```", "").strip()
                
                # 「---」で分割して各動画の台本を処理
                script_blocks = [block.strip() for block in raw_output.split("---") if block.strip()]
                
                for i, block in enumerate(script_blocks[:num_scripts]):
                    st.subheader(f"🎬 動画 {i+1} 本目")
                    
                    lines = [line.split(",", 1) for line in block.split("\n") if "," in line]
                    df = pd.DataFrame(lines, columns=["キャラクター名", "セリフ"])
                    
                    # プレビュー表示
                    st.dataframe(df)
                    
                    # 各動画ごとに個別のダウンロードボタンを用意
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
                    
                    st.download_button(
                        label=f"動画 {i+1} 本目のCSVをダウンロード", 
                        data=csv_buffer.getvalue().encode('utf-8-sig'),
                        file_name=f"ymm4_script_part{i+1}.csv", 
                        mime="text/csv",
                        key=f"btn_{i}"
                    )
                    st.write("---")
                    
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
