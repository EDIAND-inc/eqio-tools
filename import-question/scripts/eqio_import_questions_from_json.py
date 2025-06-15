import requests
import getpass
import json
import os
import boto3
import botocore.exceptions
from datetime import datetime, timedelta

BASE_URL = "https://4nqdy3iwwb.ap-northeast-1.awsapprunner.com"


def login():
    username_env = os.environ.get("EQIO_TOOL_USERNAME", "")
    username = input(f"Username[{username_env}]: ")
    if not username:
        username = username_env
    if not username:
        raise ValueError("Username is required")
    password_env = os.environ.get("EQIO_TOOL_PASSWORD", "")
    password = ""
    if password_env:
        password = password_env
    else:
        # getpassを使ってパスワードを入力
        password = getpass.getpass("Password: ")
    url = f"{BASE_URL}/account/signin"
    response = requests.post(url, json={"email": username, "password": password})
    print("STATUS CODE:", response.status_code)
    print("RESPONSE TEXT:", response.text)  # ← 追加して中身を確認

    response.raise_for_status()  # HTTPエラーならここで例外になる
    return response.json()["accessToken"]


def get_current_user(token):
    url = f"{BASE_URL}/users"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_organizations(token):
    url = f"{BASE_URL}/organizations/belonging"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    orgs = response.json()
    print("\n所属組織一覧:")
    for idx, org in enumerate(orgs):
        print(f"{idx + 1}. {org['name']} (ID: {org['id']})")
    choice = int(input("\n組織番号を選択してください: ")) - 1
    return orgs[choice]["id"]


def load_json_file():
    filepath_env = os.environ.get("EQIO_TOOL_JSON_INPUT_FILE", "")
    filepath = input(f"JSONファイルパスを入力してください[{filepath_env}]: ")
    if not filepath:
        filepath = filepath_env
    if not filepath:
        raise ValueError("JSONファイルパスは必須です")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"ファイルが見つかりません: {filepath}")
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSONファイルのルート要素はリストでなければなりません")
        # if not (200 <= len(data) <= 1000):
        #     raise ValueError("createQuestions の件数は200〜1000件でなければなりません")
        return data


# 組織にフォルダを作成
def create_folder(org_id, token):
    folder_name = input("施設名(フォルダ名)を入力してください: ")
    if not folder_name:
        raise ValueError("施設名(フォルダ名)は必須です")

    url = f"{BASE_URL}/organizations/{org_id}/folders"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": folder_name,
        "parentId": None,  # 親フォルダがない場合はNone
    }
    response = requests.post(url, json=payload, headers=headers)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print("❌ HTTP Error:", e)
        print("📥 Status Code:", response.status_code)
        print("📥 Response Body:", response.text)  # ← 追加
        raise
    print("✅ フォルダを正常に作成しました")
    return response.json()


# 試験作成
def create_exam(org_id, token):
    title = input("Examination Title: ")
    if not title:
        raise ValueError("タイトルは必須です")
    description = input("Examination Description: ")
    if not description:
        raise ValueError("説明は必須です")
    # 本日の日付をデフォルトの開始日として使用
    today = datetime.now().strftime("%Y-%m-%d")
    start_date = input(f"Examination Start Date (YYYY-MM-DD)[{today}]: ")
    if not start_date:
        start_date = today
    # end_date_envはstart_dateの1日後の日付
    end_date_env = start_date if start_date else today
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("開始日はYYYY-MM-DD形式で入力してください")
    try:
        end_date_env = datetime.strptime(end_date_env, "%Y-%m-%d") + timedelta(days=1)
        end_date_env = end_date_env.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("終了日はYYYY-MM-DD形式で入力してください")

    end_date = input(f"Examination End Date (YYYY-MM-DD)[{end_date_env}]: ")
    if not end_date:
        end_date = end_date_env
    if start_date >= end_date:
        raise ValueError("開始日は終了日より前でなければなりません")

    # APIエンドポイントにリクエストを送信
    url = f"{BASE_URL}/examinations"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"orgId": org_id,
               "title": title,
               "description": description,
               "startDate": start_date,
               "endDate": end_date,
               "requiredReviewCount": 1}
    response = requests.post(url, json=payload, headers=headers)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print("❌ HTTP Error:", e)
        print("📥 Status Code:", response.status_code)
        print("📥 Response Body:", response.text)  # ← 追加
        raise
    print("✅ 試験を正常に作成しました")
    return response.json()


# フォルダに試験を追加
def add_exam_to_folder(org_id, folder_id, exam_id, token):
    url = f"{BASE_URL}/organizations/{org_id}/folders/{folder_id}/examinations"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "examinationId": exam_id
    }
    response = requests.post(url, json=payload, headers=headers)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print("❌ HTTP Error:", e)
        print("📥 Status Code:", response.status_code)
        print("📥 Response Body:", response.text)
        raise
    print("✅ 試験をフォルダに追加しました")


# post /image
# request param: orgId=string, file=string($binary)
# request body:multipart/form-data
def import_images(orgId, questions, token):
    url = f"{BASE_URL}/image"
    headers = {
        "Authorization": f"Bearer {token}",
        # "Content-Type": "multipart/form-data" # requests library sets this with boundary for files
    }
    bucket_name = 'eqio-dev-2c3803c9-5239-441e-a5e0-09bb768b6234'
    s3_client = boto3.client('s3')  # Initialize S3 client once

    # Ensure the temporary directory exists
    temp_dir = "data/tmp"
    os.makedirs(temp_dir, exist_ok=True)

    for question_index in range(len(questions)):
        question = questions[question_index]
        if "imageIds" not in question or not isinstance(question["imageIds"], list):
            continue  # Skip if imageIds is missing or not a list

        # Iterate by index to safely modify the list
        for image_idx in range(len(question["imageIds"])):
            s3_image_key = question["imageIds"][image_idx]

            # It's good practice to ensure s3_image_key is a string if there's any doubt
            if not isinstance(s3_image_key, str):
                print(f"⚠️ Skipping non-string image ID: {s3_image_key} in question {question_index}")
                continue

            local_temp_path = os.path.join(temp_dir, s3_image_key)
            os.makedirs(os.path.dirname(local_temp_path), exist_ok=True)  # Ensure the directory exists

            downloaded_successfully = False
            try:
                # imageはS3バケット内の画像パス
                # S3の画像をダウンロード
                s3_client.download_file(
                    Bucket=bucket_name,
                    Key=s3_image_key,
                    Filename=local_temp_path  # 一時ファイルとして保存
                )
                downloaded_successfully = True

                with open(local_temp_path, 'rb') as f:
                    files = {'file': (local_temp_path, f)}
                    payload = {"orgId": orgId}
                    response = requests.post(url, files=files, data=payload, headers=headers)
                    response.raise_for_status()  # Raises HTTPError for 4xx/5xx

                    # If successful, parse JSON and get ID
                    response_data = response.json()  # Raises JSONDecodeError if not JSON
                    new_id = response_data["id"]    # Raises KeyError if "id" is missing
                    # imageの値をresponse.json()["id"]に置き換える
                    questions[question_index]["imageIds"][image_idx] = new_id

            except botocore.exceptions.BotoCoreError as e:  # Catch S3 related errors
                print(f"❌ S3 Download Error for '{s3_image_key}': {e}")
                # Original s3_image_key remains in place
            except requests.HTTPError as e:
                print(f"❌ HTTP Error uploading '{s3_image_key}': {e}")
                if e.response is not None:
                    print(f"📥 Status Code: {e.response.status_code}")
                    print(f"📥 Response Body: {e.response.text}")
                # Original s3_image_key remains in place
            except json.JSONDecodeError as e:
                print(f"❌ Failed to decode JSON response for '{s3_image_key}': {e}")
                if 'response' in locals() and response is not None:  # Check if response variable exists
                    print(f"📥 Response Body: {response.text}")
                # Original s3_image_key remains in place
            except KeyError:
                print(f"❌ 'id' key missing in JSON response for '{s3_image_key}'.")
                if 'response_data' in locals() and response_data is not None:
                    print(f"📥 Response JSON: {response_data}")
                elif 'response' in locals() and response is not None:
                    print(f"📥 Response Text: {response.text}")
                # Original s3_image_key remains in place
            except requests.exceptions.RequestException as e:  # Other network errors like ConnectionError
                print(f"❌ Network error during upload of '{s3_image_key}': {e}")
                # Original s3_image_key remains in place
            except Exception as e: # Catch any other unexpected errors for this image
                print(f"❌ An unexpected error occurred for image '{s3_image_key}': {e}")
            finally:
                # テンポラリの画像ファイルを削除 (if it was downloaded)
                if downloaded_successfully and os.path.exists(local_temp_path):
                    try:
                        os.remove(local_temp_path)
                        # print(f"🗑️ Removing temporary file: {local_temp_path}")
                    except OSError as e_remove:
                        print(f"⚠️ Could not remove temporary file '{local_temp_path}': {e_remove}")
    return questions


def import_questions(token, questions):
    url = f"{BASE_URL}/questions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"createQuestions": questions}
    response = requests.post(url, json=payload, headers=headers)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print("❌ HTTP Error:", e)
        print("📥 Status Code:", response.status_code)
        print("📥 Response Body:", response.text)  # ← 追加
        raise
    print("✅ 問題を正常にインポートしました")
    return response.json()


def create_exam_slots(examInfo, user_id, questions, token):
    url = f"{BASE_URL}/examinations/slots"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    slots = []  # questionsをコピーしてスロット用に使用
    for q in questions:
        slots.append({
            "examinationId": examInfo["id"],
            "questionId": q["id"],
            "description": examInfo["description"],
            "status": "completed",  # スロットのステータスを設定
            "assignerId": user_id,
            "reviewerIds": [user_id]
        })
    payload = {"createExaminationSlots": slots}
    response = requests.post(url, json=payload, headers=headers)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print("❌ HTTP Error:", e)
        print("📥 Status Code:", response.status_code)
        print("📥 Response Body:", response.text)  # ← 追加
        raise
    return response.json()


def main():
    try:
        token = login()
        org_id = get_organizations(token)
        user = get_current_user(token)
        questions = load_json_file()

        # 各問題に orgId をセット（ユーザー選択の組織IDを適用）
        for q in questions:
            q["orgId"] = org_id

        # フォルダを作成
        folder = create_folder(org_id, token)
        print(f"✅ フォルダを作成しました (ID: {folder['id']}, 名前: {folder['name']})")
        # 試験を作成
        examInfo = create_exam(org_id, token)
        print(f"✅ 試験を作成しました (ID: {examInfo['id']})")
        add_exam_to_folder(org_id, folder["id"], examInfo["id"], token)
        print(f"✅ 試験をフォルダに追加しました (フォルダ: {folder['name']}, 試験: {examInfo['title']})")
        # questionsが10件以上の場合は最大10件づつに分割して送信。
        # 10で割り切れない場合は、最後の部分が10件未満になる。
        chunk_size = 10
        for i in range(0, len(questions), chunk_size):
            chunk = questions[i:i + chunk_size]
            # print(f"📥 画像をインポート中: {i + 1}〜{min(i + chunk_size, len(questions))}件")
            chunk = import_images(org_id, chunk, token)
            print(f"📥 問題をインポート中: {i + 1}〜{min(i + chunk_size, len(questions))}件")
            # インポート処理を呼び出す
            res_questions = import_questions(token, chunk)
            res_slots = create_exam_slots(examInfo, user["id"], res_questions, token)
            print(f"✅ {len(res_slots)}件の問題を試験({examInfo['title']})に追加しました")
    except Exception as e:
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    main()
