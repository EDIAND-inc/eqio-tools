import requests
import getpass
import json
import os

BASE_URL = "https://4nqdy3iwwb.ap-northeast-1.awsapprunner.com"


def login():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    url = f"{BASE_URL}/account/signin"
    response = requests.post(url, json={"email": username, "password": password})
    print("STATUS CODE:", response.status_code)
    print("RESPONSE TEXT:", response.text)  # ← 追加して中身を確認

    response.raise_for_status()  # HTTPエラーならここで例外になる
    return response.json()["accessToken"]


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


def load_json_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"ファイルが見つかりません: {filepath}")
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSONファイルのルート要素はリストでなければなりません")
        # if not (200 <= len(data) <= 1000):
        #     raise ValueError("createQuestions の件数は200〜1000件でなければなりません")
        return data


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


def main():
    try:
        token = login()
        org_id = get_organizations(token)
        json_path = input("JSONファイルパスを入力してください: ")
        questions = load_json_file(json_path)

        # 各問題に orgId をセット（ユーザー選択の組織IDを適用）
        for q in questions:
            q["orgId"] = org_id

        import_questions(token, questions)
    except Exception as e:
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    main()
