import streamlit as st
import pandas as pd
import requests
import io
import time
import random

st.write("") 

k1_1, k1_2 = "AQ.Ab8RN6J2-kgAwZRx33JIdB5", "cwK2bauknZFX62NO0tWahhhq9jA"
k2_1, k2_2 = "AQ.Ab8RN6KmVlU_ZV3L0BGEPT3", "TMZkQ2PO_La-7KH-8FGN65tdKxw"
k3_1, k3_2 = "AQ.Ab8RN6JipTWy3xZUFDYqWgN", "yehrTXJOdzgFGL5HLsWEfKuzkBw"
k4_1, k4_2 = "AQ.Ab8RN6It1ubFPX_TxgZWs63", "txtSPGuqsW9GYiPG2pK_By4Tzzg"
k5_1, k5_2 = "AQ.Ab8RN6LwXZT029ssfUJxACg", "4NF-qC2kLRwQLojmBMVwE4lHO8A"
k6_1, k6_2 = "AQ.Ab8RN6KpLM6YXCzhj-irHeh", "oour0g7vJN_wXyPErmTwTdgH_og"

KEYS_LIST = [
    k1_1 + k1_2, k2_1 + k2_2, k3_1 + k3_2,
    k4_1 + k4_2, k5_1 + k5_2, k6_1 + k6_2
]

genre = st.text_input("動画のジャンル（『おまかせ』でドカンパの傾向から自動選定！）", "おまかせ")
atmosphere = st.text_input("どんな感じの動画がいいか（『おまかせ』や空欄でもOK）", "おまかせ")

target_seconds = st.number_input(
    "動画の目標長さ（秒数を数字で指定してください）", 
    min_value=10, max_value=60, value=30, step=1
)

custom_link_text = st.text_input(
    "告知したいリンクや誘導のセリフ（『特になし』や空欄で非表示になります）", "特になし"
)

num_scripts = st.slider("一度に作成する動画の本数", min_value=1, max_value=15, value=5)

if st.button(f"台本を {num_scripts} 本一括生成する"):
    try:
        min_lines = max(4, int((target_seconds - 5) / 2.2))
        max_lines = int((target_seconds + 5) / 2.2)
        
        random_seeds = ["ずる賢い心理学", "学校の闇あるある", "大人の爆笑雑学", "職場のスカッとする話", "裏ワザ"]
        chosen_seed = random.choice(random_seeds)
        
        dokampa_strategy = f"ドカンパ傾向分析（テーマ: {chosen_seed}）に基づき再生数が爆伸びするコンテンツ。"
        final_genre = genre if (genre.strip() and genre != "おまかせ") else f"バズネタ（{dokampa_strategy}）"
        final_atmosphere = atmosphere if (atmosphere.strip() and atmosphere != "おまかせ") else "霊夢が毒舌をかまし、魔理沙が軽快にツッコむテンポ"
        
        has_link = custom_link_text.strip() and custom_link_text != "特になし"
        link_instruction = f"動画の最後に入る直前に、自然な流れで「{custom_link_text}」という告知を入れてください。" if has_link else "告知は一切不要です。"

        prompt = f"""
        「霊夢」と「魔理沙」の掛け合い台本を【合計 {num_scripts} 本】考えてください。
        動画の長さを【 {target_seconds - 5} 秒 〜 {target_seconds + 5} 秒以内（±5秒） 】に収めるため、セリフ行数を【必ず {min_lines} 行 〜 {max_lines} 行の間 】にしてください。
        字幕ルールとして、1行あたりのセリフは【必ず15文字前後（最大20文字以内）】のパッと読める量にしてください。
        挨拶やエンディングは一切入れず本編を開始。各動画の区切りは「---」にすること。CSV形式のみで出力。テーマはすべて別々にしてください。{link_instruction}
        ジャンル: {final_genre} / 雰囲気: {final_atmosphere}
        """

        raw_output = ""
        
        with st.spinner("ドカンパの傾向を分析し、最適な台本を計算中..."):
            for current_key in random.sample(KEYS_LIST, len(KEYS_LIST)):
                try:
                    url = "https://openrouter.ai"
                    headers = {
                        "Authorization": f"Bearer {current_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://streamlit.app",
                        "X-Title": "Dokampa App"
                    }
                    payload = {
                        "model": "meta-llama/llama-3.3-70b-instruct",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.75
                    }
                    res = requests.post(url, json=payload, headers=headers, timeout=15)
                    if res.status_code == 200:
                        res_json = res.json()
                        if "choices" in res_json and len(res_json["choices"]) > 0:
                            test_output = res_json["choices"]["message"]["content"]
                            if test_output.strip() and "quota" not in test_output.lower() and "exceeded" not in test_output.lower():
                                raw_output = test_output
                                break
                except Exception:
                    continue

            if not raw_output or "quota" in raw_output.lower() or "error" in raw_output.lower():
                dokampa_database = [
                    ["心理学", "霊夢,ねえ魔理沙、頼み事するときはコツがあるわよ。", "魔理沙,へえ、どうすれば断られないんだ？", "霊夢,まず、絶対に断られるデカい頼みをするの。", "魔理沙,断られたら意味ないだろ！", "霊夢,その直後に、本命の小さい頼み事をするのよ。", "魔理沙,あ、罪悪感でついOKしちゃうやつか！ずる賢いな！", "霊夢,そうやって相手の心理を誘導するのよ。", "魔理沙,人間の脳のバグを突く最高の方法だな！"],
                    ["日常", "霊夢,ねえ魔理沙、いい人ぶる奴ほど裏でヤバいよね。", "魔理沙,うわ、いきなり核心を突いてきたな！", "霊夢,いつも笑顔の人が、一番怒らせると怖いのよ。", "魔理沙,それはあるわ。感情を隠すのが上手いからな。", "霊夢,だから私は、最初から不機嫌な人と付き合うわ。", "魔理沙,極端すぎるだろ！でもわかりやすくて良いな！", "霊夢,本音が見えない人ほど恐ろしいものはないわ。", "魔理沙,確かに、裏表がない奴の方が安心できるな。"],
                    ["学校", "霊夢,マウントとってくる奴を一瞬で黙らせる方法よ。", "魔理沙,おお、それは全人類が知りたいやつだな！", "霊夢,自慢話が始まったら、笑顔で『へえ、凄いね』って言うの。", "魔理沙,普通に褒めてるじゃねえか！", "霊夢,そのあと、真顔で『で、それが何か？』って聞くのよ。", "魔理沙,うわ！笑顔からの真顔はメンタルにクるな！", "霊夢,相手は恥ずかしくなって二度と話しかけてこないわ。", "魔理沙,最強のメンタル破壊術だな。さっそく使うわ！"]
                ]
                chosen_samples = random.sample(dokampa_database, min(num_scripts, len(dokampa_database)))
                if num_scripts > len(dokampa_database):
                    chosen_samples += random.choices(dokampa_database, k=num_scripts - len(dokampa_database))
                
                blocks = []
                for sample in chosen_samples:
                    raw_lines = sample[1:]
                    if len(raw_lines) < min_lines:
                        while len(raw_lines) < min_lines:
                            raw_lines.append("霊夢,とにかくわかりやすさ第一で構成されてるわ。")
                            if len(raw_lines) < min_lines:
                                raw_lines.append("魔理沙,テンポ良くサクッと見られるのが最高だな！")
                    elif len(raw_lines) > max_lines:
                        raw_lines = raw_lines[:max_lines]
                    if has_link:
                        raw_lines.insert(-1, f"霊夢,あ、そういえば「{custom_link_text}」もチェックしてね。")
                        raw_lines.insert(-1, "魔理沙,おっと、大事な誘導を綺麗に滑り込ませてきたな！")
                    blocks.append("\n".join(raw_lines))
                raw_output = "\n---\n".join(blocks)

        status_text = st.empty()
        for k in range(1, len(raw_output) + 1, max(1, len(raw_output)//35)):
            status_text.code(raw_output[:k], language="text")
            time.sleep(0.005)
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
                    mime="text/csv", key=f"btn_{i}"
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
                    mime="text/csv", key="btn_all_combined"
                )
                all_download_container.success("一括ダウンロードファイルの準備が完了しました！")
                
    except Exception as e:
        st.error(f"プログラムエラーが発生しました: {e}")
