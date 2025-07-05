import streamlit as st
import os
import uuid
import datetime
from supabase import create_client
from dotenv import load_dotenv

# .env から読み込み
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabase クライアント生成
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# タイトル
st.title("🎨 アート投稿フォーム（簡略版）")

# 入力フォーム
with st.form("art_form"):
    artist_name = st.text_input("アーティスト名")
    title = st.text_input("作品タイトル")
    description = st.text_area("作品説明")
    production_date = st.date_input("制作日", datetime.date.today())
    image_file = st.file_uploader("作品画像をアップロード", type=["jpg", "jpeg", "png"])
    submit = st.form_submit_button("送信")

    if submit:
        if not artist_name or not title or not description or not image_file:
            st.error("❌ 必須項目がすべて入力されていません。")
        else:
            try:
                # ファイルを読み込む
                file_bytes = image_file.read()
                file_name = image_file.name
                unique_filename = f"{uuid.uuid4()}_{file_name}"
                file_path = f"artworks/{unique_filename}"

                # ストレージにアップロード
                upload_response = supabase.storage.from_("artworks").upload(
                    file_path, file_bytes, {"content-type": image_file.type}
                )

                st.write("🟡 アップロード結果:\n", upload_response)

                # INSERT用データ作成
                data = {
                    "artist_name": artist_name,
                    "title": title,
                    "description": description,
                    "production_date": production_date.isoformat(),
                    "image_path": file_path,
                    "is_approved": bool(False)  # 明示的に指定
                }

                st.write("🟡 INSERT予定データ:\n", data)

                # 型チェックログを表示
                st.write("🟢 型チェック:")
                for key, value in data.items():
                    st.write(f"{key}: {value} （type: {type(value)}）")

                # SupabaseへINSERT
                response = supabase.table("artworks").insert(data).execute()

                # レスポンス確認
                if response.status_code == 201:
                    st.success("✅ 投稿完了！ありがとうございます。")
                else:
                    st.error(f"⚠️ エラー発生：{response.error}")
            except Exception as e:
                st.error(f"⚠️ エラーが発生しました：{e}")