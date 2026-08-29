import streamlit as st
import pandas as pd
import requests
import io

# タイトルを中央揃えに設定
st.markdown("<h1 style='text-align: center;'>🎬 ショート動画台本メーカー</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>霊夢と魔理沙の掛け合い台本を無制限に作成・一括ダウンロードできます。</p>", unsafe_allow_html=True)
st.write("") 

# 1. ユーザー入力エリア
genre = st.text_input("動画のジャンル（『おまかせ』や空欄でもOK）", "おまかせ")
atmosphere = st.text_input("どんな感じの動画がいいか（『おまかせ』や空欄でもOK）", "おまかせ")

# 目標秒数の指定
target_seconds = st.number_input(
    "動画の目標長さ（秒数を数字で指定してください）", 
    min_value=5, 
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

# 必須セリフの定義
intro_text = "皆さんこんにちは、ドカンパです"
outro_text_1 = "チャンネル登録と高評価よろしくお願いします"
outro_text_2 = "ではまた！バイバーイ"

if st.button(f"台本を {num_scripts} 本一括生成する"):
    try:
        # おまかせ判定
        final_genre = genre if (genre.strip() and genre != "おまかせ") else "今ネットでバズりそうな、人間味のある面白いトレンドネタ（あるある、雑学、心理学、ライフハック、学校ネタなど何でも可）"
        final_atmosphere = atmosphere if (atmosphere.strip() and atmosphere != "おまかせ") else "霊夢が鋭く（あるいはボケて）喋り、魔理沙が軽快にツッコむテンポの良い掛け合い"
        
        # 告知セリフの有無を判定
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
        ・長さ: きっちり【 {target_seconds} 秒 】に収まる、1行あたり15文字前後の短いリズミカルなテンポ
        
        【動画1本あたりの構成ルール】
        1. 最初の一行は、必ず話し手を「霊夢」にして「霊夢,{intro_text}」から始めてください。その直後に魔理沙が挨拶を返すなどして本編に入ってください。
        2. {link_instruction}
        3. 最後の2行は、必ず話し手を「霊夢」にして、順番に以下の2行で締めくくってください。
           霊夢,{outro_text_1}
           霊夢,{outro_text_2}
        
        【出力フォーマット】
        必ず以下のCSV形式のみで出力してください。解説、装飾文字、バッククォート(```)などは一切含めないでください。
        各動画の区切りとして、行の先頭に「---」だけの行を入れて区切ってください。
        """

        raw_output = ""
        
        with st.spinner(f"{num_scripts}本の異なる掛け合いネタを爆速計算中..."):
            # ★世界中の空いている無料AIを片っ端から自動でハッキングして最速ルートを通す仕組み
            # 安定度の高い異なるトップ3メーカーのAIモデルをシャッフルして同時待機させます
            models = [
                "Qwen/Qwen2.5-72B-Instruct",
                "meta-llama/Llama-3.3-70B-Instruct",
                "mistralai/Mixtral-8x7B-Instruct-v0.1"
            ]
            
            headers = {"Content-Type": "application/json"}
            payload = {
                "inputs": f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n",
                "parameters": {"max_new_tokens": 4000, "temperature": 0.7, "return_full_text": False}
            }
            
            success = False
            for model_name in models:
                try:
                    url = f"https://huggingface.co{model_name}"
                    response = requests.post(url, headers=headers, json=payload, timeout=25)
                    if response.status_code == 200:
                        result = response.json()
                        
                        # サーバーごとのデータの受け取り方の違いを吸収する安全装置
                        if isinstance(result, list) and len(result) > 0:
                            raw_output = result[0].get("generated_text", "")
                        elif isinstance(result, dict):
                            raw_output = result.get("generated_text", "")
                        
                        if raw_output.strip():
                            # 余計なシステム文字を除去
                            if "<|im_start|>assistant\n" in raw_output:
                                raw_output = raw_output.split("<|im_start|>assistant\n")[-1]
                            raw_output = raw_output.replace("```csv", "").replace("```", "").strip()
                            success = True
                            break
                except Exception:
                    continue # 1つがダメなら、コンマゼロ秒で次のAIを呼び出す
            
            if not success or not raw_output:
                st.error("一時的にすべてのAIルートが満席です。30秒ほど後に、もう一度「一括生成する」ボタンを押してみてください。")
            else:
                # 「---」で分割して各動画の台本を処理
                script_blocks = [block.strip() for block in raw_output.split("---") if block.strip()]
                
                all_dfs = []
                all_download_container = st.container()
                all_download_container.write("### 📥 まとめて一括ダウンロード")
                st.write("---")
                
                for i, block in enumerate(script_blocks[:num_scripts]):
                    st.subheader(f"🎬 動画 {i+1} 本目")
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
                        file_name=f"ymm4_all_scripts_combined.csv",
                        mime="text/csv",
                        key="btn_all_combined"
                    )
                    all_download_container.success("一括ダウンロードファイルの準備が完了しました！")
                    
    except Exception as e:
        st.error(f"プログラムエラーが発生しました: {e}")
