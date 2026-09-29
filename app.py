import streamlit as st
import pandas as pd
import io
import time
import random
import zipfile

# タイトルやロゴなどの表示をすべて削除し、すぐに使えるスッキリした画面
st.write("") 

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
        
        # 毎回完全にランダムでバラバラのバズ台本を組み立てるための超巨大データベース
        topics_pool = [
            "ずる賢い心理学", "学校の闇あるある", "大人の爆笑雑学", "職場のスカッとする話", 
            "ネットで話題の嘘のような本当の話", "知ると得する裏ワザ", "勘違いしやすい常識", 
            "誰もが共感する不満", "10秒で驚く雑学", "天才の思考法", "損を回避するライフハック",
            "人間関係の裏側", "SNSの甘い罠", "タイムパフォーマンス最強の技", "友達に即話したい噂",
            "脳のバグを突くライフハック", "お金持ちだけが知っている秘密", "一瞬で人を操る対話術"
        ]
        
        bokes_pool = [
            "いい人ぶる奴ほど裏で超ヤバいのよ。", "人に頼み事するときは絶対に断られるデカい話からするの。",
            "マウントをとってくる奴には笑顔からの真顔が最強よ。", "おねだりするときは相手の右斜め後ろから攻めなさい。",
            "セールで半額って見ると、財布のトドメを刺されるわよね。", "人が嘘をつくとき、目は必ず右上を向くのよ。",
            "しつこい勧誘には『もうそれ持ってます』で一撃よ。", "やる気が出ない時は5秒数えて脳を騙すのよ。",
            "テスト前に勉強してないって言う奴はプライドの予防線よ。", "SNSの幸せアピールは映画の予告編と同じよ。",
            "早く寝たいときほどスマホを見ちゃうの脳のバグよ。", "本当にモテる奴は自分の話を一切しないのよ。"
        ]
        
        tsukkomis_pool = [
            "うわ、いきなり核心を突いてきたな！", "断られたら意味ないだろ！でもずる賢いな！",
            "うぐっ…笑顔からの真顔はメンタルにクるわ…。", "立ち位置だけで勝率が変わるなら安いもんだな！",
            "やめろー！私の無駄遣いを正論で殴るんじゃない！", "脳がフル回転で作り話をしてる証拠なんだな。",
            "なるほど、それ以上おすすめする理由を奪うわけか！", "あ、行動を仕組み化して動く天才の思考法か！",
            "あるある！あれセルフハンディキャップって言うんだな！", "深すぎるわ！カットされた泥臭い日常を見るなと。",
            "わかるわ、あの謎の夜更かしの誘惑はヤバいよな。", "聞き手に回って相手に気持ちよく喋らせる技か！"
        ]

        # 追加用の短いセリフプール
        extra_lines_pool = [
            ("霊夢,これがネットで爆伸びする最新の仕掛けよ。", "魔理沙,なるほど、人間の心理を完璧に突いてるな。"),
            ("霊夢,知っておくだけで損を回避する知識よ。", "魔理沙,確かに、これは友達に即話したくなるわ。"),
            ("霊夢,日常の不満を一瞬でスカッとさせる裏ワザね。", "魔理沙,明日から職場でさっそく試してみる価値あるな。"),
            ("霊夢,小学生でも一瞬で理解できるシンプルな話よ。", "魔理沙,わかりやすさが第一だから、一番バズるテンポだな。")
        ]

        generated_blocks = []
        has_link = custom_link_text.strip() and custom_link_text != "特になし"

        # 指定本数分の台本を作成
        for i in range(num_scripts):
            random.shuffle(topics_pool)
            random.shuffle(bokes_pool)
            random.shuffle(tsukkomis_pool)
            random.shuffle(extra_lines_pool)
            
            t = topics_pool[0]
            b1 = bokes_pool[0]
            ts1 = tsukkomis_pool[0]
            b2 = bokes_pool[1]
            ts2 = tsukkomis_pool[1]
            b3 = bokes_pool[2]
            ts3 = tsukkomis_pool[2]
            
            raw_lines = [
                f"霊夢,ねえ魔理沙、今回は『{t}』に関するヤバい話よ。",
                f"魔理沙,ほう、ドカンパ視聴者が大好物のネタだな！",
                f"霊夢,{b1}",
                f"魔理沙,{ts1}",
                f"霊夢,{b2}",
                f"魔理沙,{ts2}",
                f"霊夢,{b3}",
                f"魔理沙,{ts3}"
            ]
            
            # 指定された±5秒の範囲の行数に収まるようにランダムにセリフを引き伸ばす（バリエーション作成）
            target_line_count = random.randint(min_lines, max_lines)
            for extra_r, extra_m in extra_lines_pool:
                if len(raw_lines) >= target_line_count:
                    break
                raw_lines.append(extra_r)
                if len(raw_lines) < target_line_count:
                    raw_lines.append(extra_m)
                    
            if len(raw_lines) > max_lines:
                raw_lines = raw_lines[:max_lines]
                
            if has_link:
                raw_lines.insert(-1, f"霊夢,あ、そういえば「{custom_link_text}」もチェックしてね。")
                raw_lines.insert(-1, "魔理沙,おっと、最後に大事な誘導を滑り込ませてきたな！")
                
            # 作成したセリフのリストを行数（長さ）と一緒に保存
            generated_blocks.append(raw_lines)
            
        # ★【重要】すべての台本を「セリフの行数が一番長いものから順番（降順）」に並び替える魔法の処理
        generated_blocks.sort(key=len, reverse=True)

        # カタカタと文字が流れるストリーミング演出用にテキストを合体
        raw_output = "\n---\n".join(["\n".join(b) for b in generated_blocks])

        status_text = st.empty()
        for k in range(1, len(raw_output) + 1, max(1, len(raw_output)//40)):
            status_text.code(raw_output[:k], language="text")
            time.sleep(0.002)
        status_text.empty()

        if generated_blocks:
            zip_file_contents = []
            all_download_container = st.container()
            all_download_container.write("### 📥 まとめて一括ダウンロード")
            st.write("---")
            
            # 長い順に並び替えたリストをループ処理して画面に表示
            for i, block_lines in enumerate(generated_blocks):
                st.subheader(f"🎬 動画 {i+1} 本目 (±5秒字幕最適化済み・合計 {len(block_lines)} 行)")
                
                # データフレームの作成
                lines_split = [line.split(",", 1) for line in block_lines if "," in line]
                df = pd.DataFrame(lines_split, columns=["キャラクター名", "セリフ"])
                st.dataframe(df)
                
                # 単品保存データの作成
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
                
                # ZIP用に「ファイル名」と「CSVの中身」をセットで保存（ここでも長い順番に保存されます）
                file_name = f"ymm4_script_part{i+1}.csv"
                zip_file_contents.append((file_name, csv_buffer.getvalue()))
                
                st.download_button(
                    label=f"動画 {i+1} 本目だけをダウンロード", 
                    data=csv_buffer.getvalue().encode('utf-8-sig'),
                    file_name=file_name, 
                    mime="text/csv", key=f"btn_{i}"
                )
                st.write("---")
            
            # まとめてZIPにする処理
            if zip_file_contents:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    for f_name, csv_data in zip_file_contents:
                        zf.writestr(f_name, csv_data.encode('utf-8-sig'))
                
                all_download_container.download_button(
                    label=f"🔥 【最長台本順】全 {len(zip_file_contents)} 本の台本を別々のCSVにして1つのZIPで一括保存",
                    data=zip_buffer.getvalue(),
                    file_name="ymm4_all_scripts_files.zip",
                    mime="application/zip", key="btn_all_zip_combined_desc"
                )
                all_download_container.success("一括ZIPファイルの準備が完了しました！解凍すると一番長い台本順にCSVファイルが現れます！")
                
    except Exception as e:
        st.error(f"プログラムエラーが発生しました: {e}")
