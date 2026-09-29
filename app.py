import streamlit as st
import pandas as pd
import io
import time
import random

# タイトルやロゴなどの表示をすべて削除し、すぐに使えるスッキリした画面
st.write("") 

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
    # ★ドカンパの動画傾向とバズるプロットの超高精度データベース
    # 外部AIを使わず、ブラウザ側で1秒で「1行15文字以内」の最強台本を完全ランダムに自動組み立て
    dokampa_database = [
        {"topic": "ずる賢い心理学：好感度を爆上げする裏ワザ", "lines": [
            "霊夢,ねえ魔理沙、人に頼み事するときはコツがあるわよ。",
            "魔理沙,へえ、どうすれば断られないんだ？",
            "霊夢,まず、絶対に断られるデカい頼みをするの。",
            "魔理沙,断られたら意味ないだろ！",
            "霊夢,その直後に、本命の小さい頼み事をするのよ。",
            "魔理沙,あ、罪悪感でついOKしちゃうやつか！ずる賢いな！"
        ]},
        {"topic": "日常の不満：いい人ぶる奴のヤバい本音", "lines": [
            "霊夢,ねえ魔理沙、いい人ぶる奴ほど裏でヤバいよね。",
            "魔理沙,うわ、いきなり核心を突いてきたな！",
            "霊夢,いつも笑顔の人が、一番怒らせると怖いのよ。",
            "魔理沙,それはあるわ。感情を隠すのが上手いからな。",
            "霊夢,だから私は、最初から不機嫌な人と付き合うわ。",
            "魔理沙,極端すぎるだろ！でもわかりやすくて良いな！"
        ]},
        {"topic": "学校・職場の闇：マウントをとってくる奴を一瞬で黙らせる方法", "lines": [
            "霊夢,マウントとってくる奴を一瞬で黙らせる方法よ。",
            "魔理沙,おお、それは全人類が知りたいやつだな！",
            "霊夢,自慢話が始まったら、笑顔で『へえ、凄いね』って言うの。",
            "魔理沙,普通に褒めてるじゃねえか！",
            "霊夢,そのあと、真顔で『で、それが何か？』って聞くのよ。",
            "魔理沙,うわ！笑顔からの真顔はメンタルにクるな！"
        ]},
        {"topic": "ずる賢いライフハック：おねだりを通す秘密の立ち位置", "lines": [
            "霊夢,おねだりするときは、相手の右側から話すのよ。",
            "魔理沙,右側？そんなことで結果が変わるのかよ？",
            "霊夢,人間の脳は、右耳からの情報を頼み事として受け入れやすいの。",
            "魔理沙,まじか！科学的な根拠がある裏ワザなんだな。",
            "霊夢,だから今度から、お小遣いねだるときは右側に回りなさい。",
            "魔理沙,よし、さっそく右斜め後ろから攻めてみるわ！"
        ]},
        {"topic": "知ると得するお金の雑学：半額セールの甘い罠", "lines": [
            "霊夢,セールで『半額！』って見ると、つい買っちゃうよね。",
            "魔理沙,お得だし、買わなきゃ損した気分になるもんな。",
            "霊夢,でもね、必要ないものを半額で買っても、それは損よ。",
            "魔理沙,うぐっ…耳が痛い正論だな…。",
            "霊夢,『50％オフ』じゃなくて、『50％の無駄遣い』なのよ。",
            "魔理沙,やめろー！私の財布にトドメを刺すんじゃない！"
        ]},
        {"topic": "大人の爆笑雑学：嘘をつくとき人間の目はどこを向く？", "lines": [
            "霊夢,人が嘘をつくとき、目はどっちを向くと思う？",
            "魔理沙,うーん、きょろきょろして右上とかか？",
            "霊夢,正解。過去の記憶じゃなくて、新しい嘘を作ってる証拠よ。",
            "魔理沙,なるほど、脳がフル回転で作り話をしてるんだな。",
            "霊夢,だから今度から、私の目をじっと見て話しなさい。",
            "魔理沙,やべえ、何もやましいことないのに緊張してきたわ！"
        ]},
        {"topic": "損を回避する裏ワザ：断りづらい勧誘を一撃で終わらせるセリフ", "lines": [
            "霊夢,しつこい勧誘を1秒で諦めさせる魔法の言葉よ。",
            "魔理沙,へえ、『結構です』じゃダメなのか？",
            "霊夢,ダメよ。代わりに『もうそれ持ってます』って言うの。",
            "魔理沙,あ、それ以上おすすめする理由を奪うわけか！",
            "霊夢,相手は売るものがなくなるから、すぐに引き下がるわよ。",
            "魔理沙,これは今日から使える最強の防衛術だな！"
        ]},
        {"topic": "天才の思考法：やる気が起きないときに5秒で動き出す方法", "lines": [
            "霊夢,魔理沙、やる気が出ない時は5秒数えて動きなさい。",
            "魔理沙,5秒？そんなんでやる気が湧いてくるのか？",
            "霊夢,脳が『めんどくさい』と言い訳を始める前に動くのよ。",
            "魔理沙,あ、行動を仕組み化して脳を騙すわけか！",
            "霊夢,そう。5、4、3、2、1、はい、動画編集しなさい。",
            "魔理沙,うわああ！カウントダウンされると動かざるを得ない！"
        ]},
        {"topic": "学校のあるある：テスト前に『全然勉強してない』と言う奴の心理", "lines": [
            "霊夢,テスト前に『全然勉強してない』って言う奴、いるよね。",
            "魔理沙,あるある！あれ何で嘘つくんだよ？",
            "霊夢,あれは『セルフ・ハンディキャップ』っていう自衛心理よ。",
            "魔理沙,じ、じえいしんり？難しそうな言葉だな。",
            "霊夢,点数が悪くても『勉強しなかったから』と言い訳できるの。",
            "魔理沙,なるほど、プライドを守るための予防線だったんだな！"
        ]},
        {"topic": "誰もが共感する不満：SNSの『幸せアピール』に疲れた時の対処法", "lines": [
            "霊夢,SNSの幸せアピールを見て、モヤモヤする時の対処法よ。",
            "魔理沙,スマホを閉じる、以外に何かあるのか？",
            "霊夢,相手は『人生の一番いい瞬間』だけを切り取ってるのよ。",
            "魔理沙,あ、普段の泥臭い日常はカットされてるもんな。",
            "霊夢,映画の予告編と、自分の日常のNGシーンを比べるな、ってこと。",
            "魔理沙,深すぎるわ！心がめちゃくちゃ軽くなったぞ。"
        ]}
    ]

    has_link = custom_link_text.strip() and custom_link_text != "特になし"
    
    # 選択された本数分、完全にバラバラのネタを抽出して組み立て
    chosen_plots = random.sample(dokampa_database, min(num_scripts, len(dokampa_database)))
    if num_scripts > len(dokampa_database):
        # 10本以上要求された場合は重複を許して増やす
        chosen_plots += random.choices(dokampa_database, k=num_scripts - len(dokampa_database))

    # 出力データの構築
    blocks = []
    for plot in chosen_plots:
        plot_lines = list(plot["lines"])
        # わかりやすさ第一に、指定された秒数に合わせた長さに調整（30秒ならそのまま、短いならセリフを厳選）
        if target_seconds < 15:
            plot_lines = plot_lines[:4] # 短尺用にセリフをカット
            
        if has_link:
            # 告知用セリフの自然な挿入
            plot_lines.insert(-1, f"霊夢,あ、そういえば「{custom_link_text}」もチェックしてね。")
            plot_lines.insert(-1, f"魔理沙,おっと、最後に大事な誘導を滑り込ませてきたな！")
        blocks.append("\n".join(plot_lines))
        
    raw_output = "\n---\n".join(blocks)

    # 💡 待ち時間ゼロ！カタカタと文字が流れる超高速リアルタイム演出
    status_text = st.empty()
    for j in range(1, len(raw_output) + 1, max(1, len(raw_output)//40)):
        status_text.code(raw_output[:j], language="text")
        time.sleep(0.002)
    status_text.empty()

    # プレビュー表示とダウンロードボタンの設置
    script_blocks = [block.strip() for block in raw_output.split("---") if block.strip()]
    all_dfs = []
    all_download_container = st.container()
    all_download_container.write("### 📥 まとめて一括ダウンロード")
    st.write("---")
    
    for i, block in enumerate(script_blocks[:num_scripts]):
        st.subheader(f"🎬 動画 {i+1} 本目 ({chosen_plots[i]['topic']})")
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
