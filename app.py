import streamlit as st
import pandas as pd
import google.generativeai as genai
import io

st.title("📱 霊夢＆魔理沙×最大15本一括！ショート動画台本メーカー")
st.write("Googleの無料AIを使い、霊夢と魔理沙のテンポ良い掛け合い台本を最大15本同時に作成します。")

api_key = st.sidebar.text_input("Gemini API Keyを入力してください", type="password")

# 1. ユーザー入力エリア
genre = st.text_input("動画のジャンル（『おまかせ』や空欄でもOK）", "おまかせ")
atmosphere = st.text_input("どんな感じの動画がいいか（『おまかせ』や空欄でもOK）", "おまかせ")
target_seconds = st.selectbox("動画の目標長さ", [15, 30, 60], index=1)

# ★告知リンク入力欄（空欄や特になしで無しにできるように修正）
custom_link_text = st.text_input(
    "告知したいリンクや誘導のセリフ（『特になし』や空欄で非表示になります）", 
    "特になし"
)

# 最大15本まで選択できるスライダー
num_scripts = st.slider("一度に作成する動画の本数", min_value=1, max_value=15, value=5)

# 必須セリフの定義
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
            final_genre = genre if (genre.strip() and genre != "おまかせ") else "今ネットでバズりそうな、人間味のある面白いトレンドネタ（あるある、雑学、心理学、ライフハック、学校ネタなど何でも可）"
            final_atmosphere = atmosphere if (atmosphere.strip() and atmosphere != "おまかせ") else "霊夢が鋭く（あるいはボケて）喋り、魔理沙が軽快にツッコむテンポの良い掛け合い"
            
            # 告知セリフの有無を判定する設定
            has_link = custom_link_text.strip() and custom_link_text != "特になし"
            link_instruction = f"本編の話が終わって、エンディングに入る直前に、必ず自然な流れでどちらかのキャラクターが「{custom_link_text}」というセリフを入れてください。" if has_link else "今回は告知やリンク誘導のセリフは一切不要です。本編が終わったらすぐにエンディングの挨拶に入ってください。"
            example_link_line = f"霊夢,{custom_link_text}\n" if has_link else ""

            # プロンプトの構築
            prompt = f"""
            あなたはTikTokやYouTube Shortsでバズる動画を手がける天才放送作家です。
            「霊夢（れいむ）」と「魔理沙（まりさ）」の2人が、人間味あふれるリアルで面白い掛け合いをするショート動画のネタを【合計 {num_scripts} 本】考えてください。
            
            【超重要ルール】
            1. それぞれの動画の内容やテーマは、すべて全く異なるエピソードやネタにしてください（使い回し厳禁）。
            2. キャラクターのセリフの先頭につける名前は、必ず「霊夢」または「魔理沙」にしてください。
            3. AI特有の不自然な解説や無機質な正論は禁止です。人間が日常で感じる「本音」や「クスッと笑えるユーモア」をベースにしてください。
            
            【動画1本あたりの条件】
            ・ジャンル: {final_genre}
            ・雰囲気: {final_atmosphere}
            ・長さ: {target_seconds}秒に収まる、1行あたり15文字前後の短いリズミカルなテンポ
            
            【動画1本あたりの構成ルール】
            1. 最初の一行は、必ず話し手を「霊夢」にして「霊夢,{intro_text}」から始めてください。その直後に魔理沙が挨拶を返すなどして本編に入ってください。
            2. {link_instruction}
            3. 最後の2行は、必ず話し手を「霊夢」にして、順番に以下の2行で締めくくってください。
               霊夢,{outro_text_1}
               霊夢,{outro_text_2}
            
            【出力フォーマット】
            必ず以下のCSV形式のみで出力してください。解説、装飾文字、バッククォート(```)などは一切含めないでください。
            各動画の区切りとして、行の先頭に「---」だけの行を入れて区切ってください。
            
            出力例：
            霊夢,皆さんこんにちは、ドカンパです
            魔理沙,うっす、よろしくな！
            霊夢,（ネタ1の掛け合いボケ）
            魔理沙,（ネタ1のツッコミ）
            {example_link_line}霊夢,{outro_text_1}
            霊夢,{outro_text_2}
            ---
            霊夢,皆さんこんにちは、ドカンパです
            魔理沙,今日もやっていくぜ！
            ...
            """
            
            with st.spinner(f"{num_scripts}本の異なる掛け合いネタを計算中..."):
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
