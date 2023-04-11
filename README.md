# Any GitHub Loader

GitHub上のコンテンツをllama-indexを利用して、インデックス化します。

## Setup

```bash
$ bundle install
$ pip3 install -r requirements.txt
```

## Usage
```
# コンテンツを学習する
$ bundle exec ruby run.rb load org/repo --types content -e "README.md"
# indexを作成する
$ python3 run.py
# indexを利用してクエリする
$ python3 try.py
```

## Author
- @pyama86
