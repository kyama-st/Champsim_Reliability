<p align="center">
  <h1 align="center"> コマンドリスト </h1>
  <p> シミュレーションのコマンドや気をつけるべきことのメモ。 
</p>

# シミュレーション実行からAVF算出まで
トレースの取得
```
$ cd scripts
$ ./download_dpc3_traces.sh
```

Champsimのビルドとシミュレーション実行-> champsimの結果ファイルから、jsonファイルを作成。
```
$ ./run_command.sh
```

jsonファイルからpythonファイルの実行
```
$ python AVF_graph.py
```
