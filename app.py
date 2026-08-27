import streamlit as st
import pandas as pd
from openai import OpenAI
import io

st.title("📱 人間味MAX！ショート動画台本メーカー")
st.write("まるで人が考えたような『リアルでバズる』ショート台本を作ります。")

api_key = st.sidebar.text_input("OpenAI API Keyを入力してください", type="password")
genre = st.text_input("動画のジャンル（例：学校あるある、社畜の日常）", "学校あるある")
atmosphere = st.text_input("どんな感じの動画がいいか（例：共感できる、クスッと笑える）", "共感できる、クスッと笑える")
target_seconds = st.selectbox("動画の目標長さ", [15, 30, 60], index=1)

intro_text = "皆さんこんにちは、ドカンパです"
outro_text_1 = "チャンネル登録と高評価よろしくお願いします"
outro_text_2 = "ではまた！バイバーイ"

if st.button("人間味のある台本を生成する"):
    if not api_key:
        st.error("左側のサイドバーにOpenAIのAPIキーを入力してください。")
    else:
        client = OpenAI(api_key=api_key)
        prompt = f"""
        TikTokやYouTube Shortsでバズる人気クリエイターとして、人間が日常で感じる「あるある」や「ユーモア」を盛り込んだショート動画のネタを考えてください。AI特有の不自然な解説は禁止です。
        【条件】ジャンル: {genre}、雰囲気: {atmosphere}、長さ: {target_seconds}秒に収まるテンポ
        【ルール】最初の一行は必ず「{intro_text}」、最後は必ず順番に「{outro_text_1}」「{outro_text_2}」にする。メインの話し手は「ドカンパ」。「キャラクター名,セリフ」のCSV形式のみで出力せよ。
        """
        with st.spinner("面白いネタを考えています..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.85
                )
                raw_script = response.choices.message.content.strip()
                lines = [line.split(",", 1) for line in raw_script.split("\n") if "," in line]
                df = pd.DataFrame(lines, columns=["キャラクター名", "セリフ"])
                st.subheader("生成された台本")
                st.dataframe(df)
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
                st.download_button(
                    label="YMM4用CSVファイルをダウンロード", data=csv_buffer.getvalue().encode('utf-8-sig'),
                    file_name=f"ymm4_human_{genre}.csv", mime="text/csv"
                )
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
