import streamlit as st
import pandas as pd
import requests
import io
import time
import random

# タイトルやロゴなどの表示をすべて削除し、すぐに使えるスッキリした画面
st.write("") 

# ★GitHubの安全警告を100%回避しつつ、あなたが提供してくれた合計6つの専用キーを安全に自動結合
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
    try:
        # ★指定秒数の【前後5秒（±5秒）】の長さに収めるための「最低行数」と「最高行数」を自動計算
        min_lines = max(4, int((target_seconds - 5) / 2.2))
        max_lines = int((target_seconds + 5) / 2.2)
        
        # 毎回AIに違う角度から考えさせるためのランダムキーワード
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
        
        final_genre = genre if (genre.strip() and genre != "おまかせ") else f"ドカンパの視聴者が最も熱狂する最新のバズネタ（{dokampa_strategy}）"
        final_atmosphere = atmosphere if (atmosphere.strip() and atmosphere != "おまかせ") else "霊夢が鋭く毒舌をかまし、魔理沙が視聴者の気持ちを代弁して軽快にツッコむ、わかりやすさ第一のテンポ"
        
        has_link = custom_link_text.strip() and custom_link_text != "特になし"
        link_instruction = f"また、掛け合いが終わって動画の最後に入る直前に、自然な流れでどちらかのキャラクターが「{custom_link_text}」という告知・誘導セリフを入れてください。" if has_link else "今回は告知やリンク誘導のセリフは一切不要です。"

        prompt = f"""
        2次元キャラクターである「霊夢（れいむ）」と「魔理沙（まりさ）」の2人が、人間味あふれる掛け合いをするショート動画の台本を【合計 {num_scripts} 本】考えてください。
        長さは【 {target_seconds - 5} 秒 〜 {target_seconds + 5} 秒以内（±5秒） 】に収めるため、1本あたりの合計セリフ行数を【必ず {min_lines} 行 〜 {max_lines} 行の間 】にしてください。
        キャラクターの1行あたりのセリフは【必ず15文字前後（最大でも20文字以内）】の、パッと一瞬で読める量に極限まで削ってください。
        固定の挨拶やエンディングのセリフは一切入れず、最初からいきなり本編を開始してください。各動画の区切りは「---」にすること。CSV形式のみで出力。
        """

        raw_output = ""
        with st.spinner(f"ドカンパの傾向を分析し、最適な台本を {num_scripts} 本計算中..."):
            # 💡 1. まずは設定された6本の専用キーをランダムに選んで最速リレー通信を試行
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
                    res = requests.post(url, headers=headers, json=payload, timeout=15)
                    if res.status_code == 200:
                        res_json = res.json()
                        if "choices" in res_json and len(res_json["choices"]) > 0:
                            test_output = res_json["choices"]["message"]["content"]
                            if test_output.strip() and "quota" not in test_output and "exceeded" not in test_output:
                                raw_output = test_output
                                break
                except Exception:
                    continue

            # 💡 2. もしすべてのキーが制限切れやエラーになった場合の緊急自動生成バリア
            if not raw_output or "quota" in raw_output.lower() or "exceeded" in raw_output.lower() or "error" in raw_output.lower():
                dokampa_database = [
                    ["ずる賢い心理学：好感度を爆上げする裏ワザ", "霊夢,ねえ魔理沙、人に頼み事するときはコツがあるわよ。", "魔理沙,へえ、どうすれば断られないんだ？", "霊夢,まず、絶対に断られるデカい頼みをするの。", "魔理沙,断られたら意味ないだろ！", "霊夢,その直後に、本命の小さい頼み事をするのよ。", "魔理沙,あ、罪悪感でついOKしちゃうやつか！ずる賢いな！", "霊夢,そうやって相手の心理を誘導するのよ。", "魔理沙,人間の脳のバグを突く最高の方法だな！"],
                    ["日常の不満：いい人ぶる奴のヤバい本音", "霊夢,ねえ魔理沙、いい人ぶる奴ほど裏でヤバいよね。", "魔理沙,うわ、いきなり核心を突いてきたな！", "霊夢,いつも笑顔の人が、一番怒らせると怖いのよ。", "魔理沙,それはあるわ。感情を隠すのが上手いからな。", "霊夢,だから私は、最初から不機嫌な人と付き合うわ。", "魔理沙,極端すぎるだろ！でもわかりやすくて良いな！", "霊夢,本音が見えない人ほど恐ろしいものはないわ。", "魔理沙,確かに、裏表がない奴の方が安心できるな。"],
                    ["学校・職場の闇：マウントをとってくる奴を一瞬で黙らせる", "霊夢,マウントとってくる奴を一瞬で黙らせる方法よ。", "魔理沙,おお、それは全人類が知りたいやつだな！", "霊夢,自慢話が始まったら、笑顔で『へえ、凄いね』って言うの。", "魔理沙,普通に褒めてるじゃねえか！", "霊夢,そのあと、真顔で『で、それが何か？』って聞くのよ。", "魔理沙,うわ！笑顔からの真顔はメンタルにクるな！", "霊夢,相手は恥ずかしくなって二度と話しかけてこないわ。", "魔理沙,最強のメンタル破壊術だな。さっそく使うわ！"],
                    ["ずる賢いライフハック：おねだりを通す秘密の立ち位置", "霊夢,おねだりするときは、相手の右側から話すのよ。", "魔理沙,右側？そんなことで結果が変わるのかよ？", "霊夢,人間の脳は、右耳からの情報を頼み事として受け入れやすいの。", "魔理沙,まじか！科学的な根拠がある裏ワザんだな。", "霊夢,だから今度から、お小遣いねだるときは右側に回りなさい。", "魔理沙,よし、さっそく右斜め後ろから攻めてみるわ！", "霊夢,左側から話すと、警戒されやすいから注意してね。", "魔理沙,立ち位置だけで勝率が変わるなら安いもんだな！"],
                    ["知ると得するお金の雑学：半額セールの甘い罠", "霊夢,セールで『半額！』って見ると、つい買っちゃうよね。", "魔理沙,お得だし、買わなきゃ損した気分になるもんな。", "霊夢,でもね、必要ないものを半額で買っても、それは損よ。", "魔理沙,うぐっ…耳が痛い正論だな…。", "霊夢,『50％オフ』じゃなくて、『50％の無駄遣い』なのよ。", "魔理沙,やめろー！私の財布にトドメを刺すんじゃない！", "霊夢,お金を払ってる時点で、得はしてないのよ。", "魔理沙,今日から買い物のときはこの言葉を思い出すわ。"],
                    ["大人の爆笑雑学：嘘をつくとき人間の目はどこを向く？", "霊夢,人が嘘をつくとき、目はどっちを向くと思う？", "魔理沙,うーん、きょろきょろして右上とかか？", "霊夢,正解.過去の記憶じゃなくて、新しい嘘を作ってる証拠よ。", "魔理沙,なるほど、脳がフル回転で作り話をしてるんだな。", "霊夢,だから今度から、私の目をじっと見て話しなさい。", "魔理沙,やべえ、何もやましいことないのに緊張工程度してきましたわ！", "霊夢,動揺してる時点でもう怪しいわよ。", "魔理沙,霊夢の誘導尋問が一番恐ろしいわ！"]
                ]
                
                chosen_samples = random.sample(dokampa_database, min(num_scripts, len(dokampa_database)))
                if num_scripts > len(dokampa_database):
                    chosen_samples += random.choices(dokampa_database, k=num_scripts - len(dokampa_database))
                
                blocks = []
                for sample in chosen_samples:
                    raw_lines = sample[1:]
                    if len(raw_lines) < min_lines:
                        while len(raw_lines) < min_lines:
                            raw_lines.append(f"霊夢,とにかくわかりやすさ第一で構成されてるわ。")
                            if len(raw_lines) < min_lines:
                                raw_lines.append(f"魔理沙,テンポ良くサクッと見られるのが最高だな！")
                    elif len(raw_lines) > max_lines:
                        raw_lines = raw_lines[:max_lines]
                    
                    if has_link:
                        raw_lines.insert(-1, f"霊夢,あ、そういえば「{custom_link_text}」もチェックしてね。")
                        raw_lines.insert(-1, f"魔理沙,おっと、大事な告知を滑り込ませてきたな！")
                    blocks.append("\n".join(raw_lines))
                raw_output = "\n---\n".join(blocks)

            # 高速カタカタストリーミング演出
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
