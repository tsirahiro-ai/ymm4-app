import streamlit as st
import pandas as pd
import requests
import io
import time
import random  # ★毎回完全に違うネタを生み出すための乱数システム

# タイトルやロゴなどの表示をすべて削除し、すぐに使えるスッキリした画面
st.write("") 

# 1. ユーザー入力エリア
genre = st.text_input("動画のジャンル（『おまかせ』でドカンパの傾向から自動選定！）", "おまかせ")
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

if st.button(f"台本を {num_scripts} 本一括生成する"):
    try:
        # ★毎回AIに違う角度から考えさせるためのランダムキーワードを自動生成
        random_seeds = [
            "ずる賢い心理学", "学校の闇あるある", "大人の爆笑雑学", "職場のスカッとする話", 
            "ネットで話題の嘘のような本当の話", "知ると得する裏ワザ", "勘違いしやすい常識", 
            "誰もが共感する不満", "10秒で驚く雑学", "天才の思考法", "損を回避するライフハック"
        ]
        chosen_seed = random.choice(random_seeds)
        
        dokampa_strategy = (
            f"「ドカンパ」のチャンネル傾向（日常の不満、人間関係の本音、クスッと笑えるユーモア、"
            f"学校や職場のスカッとする話など）を徹底分析し、今回は特に【 {chosen_seed} 】のテーマに焦点を当てて、"
            f"視聴者が今最も求めている、再生数が爆伸びするコンテンツを完全に新規で考えてください。"
        )
        
        final_genre = genre if (genre.strip() and genre != "おまかせ") else f"ドカンパの視聴者が熱狂するバズネタ（{dokampa_strategy}）"
        final_atmosphere = atmosphere if (atmosphere.strip() and atmosphere != "おまかせ") else "霊夢が鋭い毒舌（またはおバカなボケ）をかまし、魔理沙が視聴者の気持ちを代弁して軽快にツッコむ、わかりやすさ第一のテンポ"
        
        has_link = custom_link_text.strip() and custom_link_text != "特になし"
        link_instruction = f"また、掛け合いが終わって動画の最後に入る直前に、自然な流れでどちらかのキャラクターが「{custom_link_text}」という告知・誘導セリフを入れてください。" if has_link else "今回は告知やリンク誘導のセリフは一切不要です。"

        # 1行15文字以内、わかりやすさ第一の厳格な指示
        prompt = f"""
        あなたはYouTube ShortsやTikTokで大人気のチャンネル「ドカンパ」のお抱え天才放送作家です。
        2次元キャラクターである「霊夢（れいむ）」と「魔理沙（まりさ）」の2人が、人間味あふれるリアルで面白い掛け合いをするショート動画の台本を【合計 {num_scripts} 本】考えてください。
        
        【絶対厳守ルール：すべての動画を完全に違う内容にする】
        今回出力する {num_scripts} 本の動画は、プロット、オチ、雑学の内容などをすべて【完全にバラバラの、全く異なるエピソード】にしてください。同じような内容の使い回しは絶対に禁止です。
        
        【超重要：視聴者のための字幕ルール（わかりやすさ第一）】
        1. 画面の字幕が長すぎると視聴者が疲れて離脱します。そのため、キャラクターの1行あたりのセリフは【必ず15文字前後（最大でも20文字以内）】の、パッと一瞬で読める量に極限まで削ってください。
        2. 小学生でも一瞬で理解できる「超絶シンプルな言葉」だけを使用してください。
        
        【構成ルール】
        1. 固定の挨拶や、決まったエンディングのセリフ（チャンネル登録よろしく等）は一切入れないでください。最初からいきなり本編の掛け合いを開始してください。
        2. 長さは、きっちり【 {target_seconds} 秒 】に収まるリズミカルなテンポにしてください。
        3. {link_instruction}
        
        【ターゲットテーマ】
        ・ジャンル: {final_genre}
        ・雰囲気: {final_atmosphere}
        
        【出力フォーマット】
        必ず以下のCSV形式のみで出力してください。解説や装飾文字(```等)は一切含めないでください。
        各動画の区切りとして、行の先頭に「---」だけの行を入れて区切ってください。
        """

        raw_output = ""
        
        with st.spinner(f"ドカンパの傾向から毎回違うネタを {num_scripts} 本計算中..."):
            # 💡 混雑せず、回数制限も一切ない世界最新のオープンAPI（高速ストリーミング通信）
            url = "https://pollinations.ai"
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a professional video script writer for 'Dokampa'. Always generate completely distinct, unique scripts for each part. Each line must be under 15 characters. Separate multiple scripts with '---'."},
                    {"role": "user", "content": prompt}
                ],
                "model": "openai",
                "seed": random.randint(1, 999999)  # 毎アクセス完全にランダムな台本を強制的に吐き出させる魔法
            }
            
            # 最大3回まで通信をトライする安全装置
            for _ in range(3):
                try:
                    res = requests.post(url, json=payload, timeout=30)
                    if res.status_code == 200 and res.text.strip():
                        raw_output = res.text.strip()
                        break
                except Exception:
                    time.sleep(1)
                    continue

            if not raw_output:
                st.error("AIサーバーとの通信が一時的に途切れました。もう一度だけボタンを押してみてください！")
            else:
                # 余計なマークダウン装飾を除去
                raw_output = raw_output.replace("```csv", "").replace("```", "").strip()
                script_blocks = [block.strip() for block in raw_output.split("---") if block.strip()]
                
                # 💡 カタカタと文字が流れるリアルタイム演出
                status_text = st.empty()
                for i in range(1, len(raw_output) + 1, max(1, len(raw_output)//30)):
                    status_text.code(raw_output[:i], language="text")
                    time.sleep(0.005)
                status_text.empty()

                all_dfs = []
                all_download_container = st.container()
                all_download_container.write("### 📥 まとめて一括ダウンロード")
                st.write("---")
                
                for i, block in enumerate(script_blocks[:num_scripts]):
                    st.subheader(f"🎬 動画 {i+1} 本目 (分析＆字幕最適化済み)")
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
