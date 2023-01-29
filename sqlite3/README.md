## Command

```bash
# イメージ作成
docker build -t sqlite3_creator .
# コンテナ起動
docker run -it --rm -w /root -v $(pwd):/root/ sqlite3_creator
```
