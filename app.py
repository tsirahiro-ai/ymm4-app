import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import time
import random

# タイトルやロゴなどの表示をすべて削除し、すぐに使えるスッキリした画面
st.write("") 

# 隠し金庫（Secrets）から安全にキーを自動取得する仕組み（エラー防止強化版）
API_KEY = None
for key in st.secrets.keys():
    if "GEMINI" in key.upper() or "API_KEY" in key.upper():
        API_KEY = st.secrets[key]
        break

if not API_KEY:
    API_KEY = st.sidebar.text_input("Gemini API Keyを入力してください", type="password")

# 1. ユーザー入力エリア
genre = st.text_input("動画のジャンル（『おまかせ』でドカンパの傾向から自動選定！）", "おまかせ")
atmosphere = st.text_input("どんな感じの動画がいいか（『おまかせ』や空欄でもOK）", "おまかせ")

# 目標秒数の指定（数字で直接入力可能）
target_seconds = st.number_input(
    "動画の目標長さ（秒数を数字で指定してください）", 
    min_value=10, 
    max_value=60, 
    value=30,
    step=1
)

# 告知リンク入力欄
custom_link_text = st.text_input(
    "告知したいリンクや誘導のセリフ（『特になし』や空欄で非表示になります）", 
    "特になし"
)

# 最大15本まで選択できるスライダー
num_scripts = st.slider("一度に作成する動画の本数", min_value=1, max_value=15, value=5)

if st.button(f"台本を {num_scripts} 本一括生成する"):
    if not API_KEY:
        st.error("APIキーが設定されていません。Streamlit CloudのSettingsからSecretsを設定してください。")
    else:
        try:
            # Geminiの設定
            genai.configure(api_key=API_KEY)
            # ★Google公式の最新モデル「gemini-3.8-flash」に確実に修正しました
            model = genai.GenerativeModel('gemini-3.8-flash') 
            
            # ★指定秒数の【前後5秒（±5秒）】の長さに収めるための「最低行数」と「最高行数」を自動計算
            # 1行15文字を約2.2秒で喋る計算をベースに算出します
            min_lines = max(4, int((target_seconds - 5) / 2.2))
            max_lines = int((target_seconds + 5) / 2.2)
            
            # 毎回AIに違う角度から考えさせるためのランダムキーワードを自動生成（ネタ被りを100%防止）
            random_seeds = [
                "ずる賢い心理学", "学校の闇あるある", "大人の爆笑雑学", "職場のスカッとする話", 
                "ネットで話題の嘘のような本当の話", "知ると得する裏ワザ", "勘違いしやすい常識", 
                "誰もが共感する不満", "10秒で驚く雑学", "天才の思考法", "損を回避するライフハック"
            ]
            chosen_seed = random.choice(random_seeds)
            
            # ドカンパの動画傾向
            dokampa_strategy = (
                f"日常の不満、人間関係の本音、クスッと笑えるユーモア、"
                f"学校や職場のスカッとする話など。今回は特に【 {chosen_seed} 】のテーマに焦点を当ててください。"
            )
            
            final_genre = genre if (genre.strip() and genre != "おまかせ") else f"視聴者が最も熱狂する最新のバズネタ（{dokampa_strategy}）"
            final_atmosphere = atmosphere if (atmosphere.strip() and atmosphere != "おまかせ") else "霊夢が鋭く毒舌をかまし、魔理沙が視聴者の気持ちを代弁して軽快にツッコむ、わかりやすさ第一のテンポ"
            
            has_link = custom_link_text.strip() and custom_link_text != "特になし"
            link_instruction = f"また、掛け合いが終わって動画の最後に入る直前に、自然な流れでどちらかのキャラクターが「{custom_link_text}」という告知・誘導セリフを入れてください。" if has_link else "今回は告知やリンク誘導のセリフは一切不要です。"

            # プロンプトの構築（同じ定型文のループを禁止するルールを徹底強化）
            prompt = f"""
            あなたはYouTube ShortsやTikTokで大人気のチャンネル「ドカンパ」のお抱え天才放送作家です。
            2次元キャラクターである「霊夢（れいむ）」と「魔理沙（まりさ）」の2人が、人間味あふれるリアルで面白い掛け合いをするショート動画の台本を【合計 {num_scripts} 本】考えてください。
            
            【絶対厳守ルール1：同じセリフの繰り返し・ループは絶対に禁止】
            「とにかくわかりやすさ第一で構成されてるわ」「テンポ良くサクッと見られるのが最高だな！」といった、内容のない定型文や同じフレーズを何度も繰り返して行数を水増しすることは【絶対に禁止】です。
            最初から idle な雑談ではなく、テーマに沿った具体的なエピソードやボケ、ツッコミの言葉だけで会話を綺麗に埋め尽くしてください。
            
            【絶対厳守ルール2：長さは指定秒数の『前後5秒以内（±5秒）』にする】
            動画の長さが【 {target_seconds - 5} 秒 〜 {target_seconds + 5} 秒以内 】に収まるように、全体のセリフ合計行数を【必ず {min_lines} 行 〜 {max_lines} 行の間 】にしてください。短すぎるものは厳禁です。
            
            【絶対厳守ルール3：すべての動画を完全に違う内容にする】
            今回出力する {num_scripts} 本の動画は、プロット、オチ、雑学の内容などをすべて【完全にバラバラの、全く異なるエピソード】にしてください。
            
            【超重要：視聴者のための字幕ルール（わかりやすさ第一）】
            1. キャラクターの1行あたりのセリフは【必ず15文字前後（最大でも20文字以内）】の、パッと一瞬で読める量に極限まで削ってください。
            2. 小学生でも一瞬で理解できる「超絶シンプルな言葉」だけを使用してください。
            
            【構成ルール】
            1. 固定の挨拶や、決まったエンディングのセリフ（チャンネル登録よろしく等）は一切入れないでください。最初からいきなり本編の掛け合いを開始してください。
            2. {link_instruction}
            
            【ターゲットテーマ】
            ·ジャンル: {final_genre}
            ·雰囲気: {final_atmosphere}
            
            【出力フォーマット】
            必ず以下のCSV形式のみで出力してください。解説や装飾文字(```等)は一切含めないでください。
            各動画の区切りとして、行の先頭に「---」だけの行を入れて区切ってください。
            """

            # 待ち時間を無くすリアルタイムテキスト表示エリア
            status_text = st.empty()
            raw_output = ""
            
            # Google公式サーバーへ高速ストリーミング通信
            response = model.generate_content(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    raw_output += chunk.text
                    status_text.code(raw_output.replace("```csv", "").replace("```", ""), language="text")

            status_text.empty()
            
            if raw_output:
                raw_output = raw_output.replace("```csv", "").replace("```", "").strip()
                script_blocks = [block.strip() for block in raw_output.split("---") if block.strip()]
                
                all_dfs = []
                all_download_container = st.container()
                all_download_container.write("### 📥 まとめて一括ダウンロード")
                st.write("---")
                
                for i, block in enumerate(script_blocks[:num_scripts]):
                    actual_lines = [line for line in block.split("\n") if "," in line]
                    st.subheader(f"🎬 動画 {i+1} 本目 (±5秒字幕最適化済み・合計 {len(actual_lines)} 行)")
                    
                    lines = [line.split(",", 1) for line in block.split("\n") if "," in line]
                    df = pd.DataFrame(lines, columns=["キャラクター名", "セリフ"])
                    st.dataframe(df)
                    all_dfs.append(df)
                    
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
                    st.download_button(
                        label=f"動画 {i+1} 本目だけをダウンロード", 
                        data=csv_buffer.getvalue().encode('utf-8-sig'),
                        file_name=f"ymm4_script_part{i+1}.csv", 
                        mime="text/csv",
                        key=f"btn_{i}"
                    )
                    st.write("---")
                
                if all_dfs:
                    combined_csv_content = "キャラクター名,セリフ\n"
                    for current_df in all_dfs:
                        csv_text = current_df.to_csv(index=False, header=False, encoding="utf-8-sig")
                        combined_csv_content += csv_text
                        combined_csv_content += ",\n"
                    
                    all_download_container.download_button(
                        label=f"🔥 全 {len(all_dfs)} 本のネタを1つのファイルにまとめてダウンロード",
                        data=combined_csv_content.encode('utf-8-sig'),
                        file_name="ymm4_all_scripts_combined.csv",
                        mime="text/csv",
                        key="btn_all_combined"
                    )
                    all_download_container.success("一括ダウンロードファイルの準備が完了しました！")
                    
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
