# EQIO 問題インポートツール

このツールは、EQIO プラットフォームに JSON 形式の問題データを一括インポートする Python スクリプトです。

このディレクトリは `eqio-tools/import-question` に位置し、以下の構成となっています。

---

## 📁 ディレクトリ構成

```
import-question/
├── scripts/
│   └── eqio_import_questions_from_json.py  # 問題インポート用スクリプト
├── README.md                                # このファイル
├── requirements.txt                         # 必要なパッケージ一覧
├── .gitignore                               
└── venv/                                     # 仮想環境（Git管理対象外）
```

---

## 🧰 前提条件

- Python 3.7 以上
- Git がインストールされていること
- GitHub アカウントを持っていること

---

## 🧪 セットアップ手順

### 1. 仮想環境の作成と有効化

```bash
cd import-question
python3 -m venv venv
source venv/bin/activate   # Windows の場合: venv\Scripts\activate
```

### 2. パッケージのインストール

```bash
pip install -r requirements.txt
```

---

## 📝 スクリプトの実行方法

```bash
python scripts/eqio_import_questions_from_json.py
```

1. メールアドレスとパスワードでログイン  
2. 所属組織を選択  
3. インポート対象の JSON ファイルパスを入力  

---

## 📁 JSONファイル形式の例

```json
[
  {
    "title": "問題文1",
    "options": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
    "correct": "a",
    "explanation": "解説文"
  }
]
```

`orgId` はスクリプト内で自動的に付与されます。

---

## ⚙️ `.gitignore` の内容

以下のようなファイル/ディレクトリは Git の追跡対象外になります：

- `venv/` 仮想環境
- `__pycache__/`, `*.pyc` など Python のキャッシュ
- `.DS_Store`, `*.log` など一時ファイル

---

## 🔄 requirements.txt の更新方法（開発時）

パッケージを追加した場合：

```bash
pip freeze > requirements.txt
```

---

## ✅ GitHub に Push する手順

```bash
cd eqio-tools
git init
git add .
git commit -m "Initial commit with import-question tool structure"
git remote add origin https://github.com/<your-username>/eqio-tools.git
git branch -M main
git push -u origin main
```

---

## 📌 備考

- この構成は将来 `eqio-tools/export-question` などの追加にも対応可能なように設計されています。
