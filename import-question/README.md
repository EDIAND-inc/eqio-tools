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
3. インポート対象の JSON ファイルパスを入力（2で選択したorgIdを使用して問題APIを実行する）  

---

## 📁 サンプルのJSONファイル

dataフォルダにあります。

---

## 📌 備考

- この構成は将来 `eqio-tools/export-question` などの追加にも対応可能なように設計されています。
