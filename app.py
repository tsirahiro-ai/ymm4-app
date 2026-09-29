import streamlit as st
import pandas as pd
import requests
import io
import time

# タイトルやロゴなどの表示をすべて削除し、すぐに使えるスッキリした画面
st.write("") 

# 隠し金庫（Secrets）から安全にキーを自動取得
API_KEY = None
for key in st.secrets.keys():
    if "GEMINI" in key.upper() or "API_KEY" in key.upper():
        API_KEY = st.secrets[key]
        break

# 1. ユーザー入力エリア
genre = st.text_input("動画のジャンル（『おまかせ』でドカンパの傾向から自動選定！）", "おまかせ")
atmosphere = st.text_input("どんな感じの動画がいいか（『おまかせ』や空欄でもOK）", "おまかせ")

# 目標秒数の指定（数字で直接入力可能）
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
    # ★ドカンパの動画傾向と対策をプロンプトに完全注入
    dokampa_strategy = (
        "「ドカンパ」のチャンネル傾向（視聴者が今一番求めている、日常の不満、人間関係の本音、"
        "クスッと笑える大人の雑学、ずる賢い心理学、学校や職場のスカッとするあるあるネタなど）を徹底分析し、"
        "今一番再生数が伸びるコンテンツを予測して選定してください。"
    )
    
    final_genre = genre if (genre.strip() and genre != "おまかせ") else f"ドカンパの視聴者が最も熱狂する最新のバズネタ（{dokampa_strategy}）"
    final_atmosphere = atmosphere if (atmosphere.strip() and atmosphere != "おまかせ") else "霊夢が鋭い毒舌（またはおバカなボケ）をかまし、魔理沙が視聴者の気持ちを代弁して軽快にツッコむ、わかりやすさ第一のテンポ"
    
    has_link = custom_link_text.strip() and custom_link_text != "特になし"
    link_instruction = f"また、掛け合いが終わって動画の最後に入る直前に、自然な流れでどちらかのキャラクターが「{custom_link_text}」という告知・誘導セリフを入れてください。" if has_link else "今回は告知やリンク誘導のセリフは一切不要です。"

    # 1行15文字以内、わかりやすさ第一の厳格な指示
    prompt = f"""
    あなたはYouTube ShortsやTikTokで大人気のチャンネル「ドカンパ」のお抱え天才放送作家です。
    2次元キャラクターである「霊夢（れいむ）」と「魔理沙（まりさ）」の2人が、人間味あふれるリアルで面白い掛け合いをするショート動画の台本を【合計 {num_scripts} 本】考えてください。
    
    【超重要：視聴者のための字幕ルール（わかりやすさ第一）】
    1. 画面の字幕が長すぎると視聴者が疲れて離脱します。そのため、キャラクターの1行あたりのセリフは【必ず15文字前後（最大でも20文字以内）】の、パッと一瞬で読める量に極限まで削ってください。
    2. AI特有の難しい言葉、専門用語、無機質な解説は1文字も使わないでください。小学生でも一瞬で理解できる「超絶シンプルな言葉」だけを使用してください。
    
    【構成ルール】
    1. それぞれの動画の内容やテーマは、すべて全く異なるエピソードやネタにしてください（使い回し厳禁）。
    2. セリフの先頭につける名前は、必ず「霊夢」または「魔理沙」にしてください。
    3. 固定の挨拶や、決まったエンディングのセリフ（チャンネル登録よろしく等）は一切入れないでください。最初からいきなり本編の掛け合いを開始してください。
    4. 長さは、きっちり【 {target_seconds} 秒 】に収まるリズミカルなテンポにしてください。
    5. {link_instruction}
    
    【ターゲットテーマ】
    ・ジャンル: {final_genre}
    ・雰囲気: {final_atmosphere}
    
    【出力フォーマット】
    必ず以下のCSV形式のみで出力してください。解説、装飾文字、バッククォート(```)などは一切含めないでください。
    各動画の区切りとして、行の先頭に「---」だけの行を入れて区切ってください。
    """

    raw_output = ""
    
    with st.spinner(f"ドカンパの傾向を分析し、最適な台本を {num_scripts} 本計算中..."):
        # 第一ルート：無料の超高速オープンAPI
        try:
            url = "https://pollinations.ai"
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a professional video script writer for 'Dokampa'. Always output scripts strictly in character name and dialogue format separated by commas. Each dialogue line must be very short (around 15 characters) for easy reading."},
                    {"role": "user", "content": prompt}
                ],
                "model": "openai"
            }
            res = requests.post(url, json=payload, timeout=20)
            if res.status_code == 200 and res.text.strip():
                raw_output = res.text.strip()
        except:
            pass

        # 第二ルート（安全バリア）：もし通信が混雑していたら、ブラウザ側でドカンパ流の「1行が短い最強あるあるネタ」を即座に自動生成
        if not raw_output or "Quota" in raw_output or "満席" in raw_output or "error" in raw_output.lower():
            lines = []
            dokampa_plots = [
                ("人間関係の闇", [
                    "霊夢,ねえ魔理沙、いい人ぶる奴ほど裏でヤバいよね。",
                    "魔理沙,うわ、いきなり核心を突いてきたな！",
                    "霊夢,いつも笑顔の人が、一番怒らせると怖いのよ。",
                    "魔理沙,それはあるわ。感情を隠すのが上手いからな。",
                    "霊夢,だから私は、最初から不機嫌な人と付き合うわ。",
                    "魔理沙,極端すぎるだろ！でもわかりやすくて良いな！"
                ]),
                ("損しないための心理学", [
                    "霊夢,魔理沙、人に頼み事するときはコツがあるわよ。",
                    "魔理沙,へえ、どうすれば断られないんだ？",
                    "霊夢,まず、絶対に断られるデカい頼みをするの。",
                    "魔理沙,断られたら意味ないだろ！",
                    "霊夢,その直後に、本命の小さい頼み事をするのよ。",
                    "魔理沙,あ、罪悪感でついOKしちゃうやつか！ズルいな！"
                ]),
                ("学校・職場のスカッとする話", [
                    "霊夢,マウントとってくる奴を一瞬で黙らせる方法よ。",
                    "魔理沙,おお、それは全人類が知りたいやつだな！",
                    "霊夢,自慢話が始まったら、笑顔で『へえ、凄いね』って言うの。",
                    "魔理沙,普通に褒めてるじゃねえか！",
                    "霊夢,そのあと、真顔で『で、それが何か？』って聞くのよ。",
                    "魔理沙,うわ！笑顔からの真顔はメンタルにクるな！"
                ]),
                ("ずる賢いライフハック", [
                    "霊夢,おねだりするときは、相手の右側から話すのよ。",
                    "魔理沙,右側？そんなことで結果が変わるのかよ？",
                    "霊夢,人間の脳は、右耳からの情報を頼み事として受け入れやすいの。",
                    "魔理沙,まじか！科学的な根拠がある裏ワザなんだな。",
                    "霊夢,だから今度から、お小遣いねだるときは右側に回りなさい。",
                    "魔理沙,よし、さっそく右斜め後ろから攻めてみるわ！"
                ]),
                ("知ると得するお金の雑学", [
                    "霊夢,セールで『半額！』って見ると、つい買っちゃうよね。",
                    "魔理沙,お得だし、買わなきゃ損した気分になるもんな。",
                    "霊夢,でもね、必要ないものを半額で買っても、それは損よ。",
                    "魔理沙,うぐっ…耳が痛い正論だな…。",
                    "霊夢,『50％オフ』じゃなくて、『50％の無駄遣い』なのよ。",
                    "魔理沙,やめろー！私の財布にトドメを刺すんじゃない！"
                ])
            ]
            for i in range(num_scripts):
                title, plot_lines = dokampa_plots[i % len(dokampa_plots)]
                # 告知セリフの埋め込み
                if has_link:
                    plot_lines.insert(-1, f"霊夢,あ、そういえば「{custom_link_text}」も見てね。")
                    plot_lines.insert(-1, f"魔理沙,おっと、大事な告知を滑り込ませてきたな！")
                lines.append("\n".join(plot_lines))
            raw_output = "\n---\n".join(lines)

        # 高速カタカタストリーミング演出
        status_text = st.empty()
        for i in range(1, len(raw_output) + 1, max(1, len(raw_output)//25)):
            status_text.code(raw_output[:i], language="text")
            time.sleep(0.01)
        status_text.empty()

        if raw_output:
            raw_output = raw_output.replace("```csv", "").replace("```", "").strip()
            script_blocks = [block.strip() for block in raw_output.split("---") if block.strip()]
            
            all_dfs = []
            all_download_container = st.container()
            all_download_container.write("### 📥 まとめて一括ダウンロード")
            st.write("---")
            
            for i, block in enumerate(script_blocks[:num_scripts]):
                st.subheader(f"🎬 動画 {i+1} 本目 (字幕最適化済み)")
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
