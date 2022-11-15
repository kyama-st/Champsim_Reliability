<p align="center">
  <h1 align="center"> コマンドリスト </h1>
  <p> シミュレーションのコマンドや気をつけるべきことのメモ。 
</p>

# シミュレーション実行からAVF算出まで
トレースの取得
```
$ cd scripts
$ ./download_trace.sh
```

Champsimのビルドとシミュレーション実行-> champsimの結果ファイルから、jsonファイルを作成。
```
$ ./run_champsim.sh
```

jsonファイルからpythonファイルの実行
```
$ python AVF_graph.py
```

# 目標
- 全ベンチマークでAVFの標準偏差を算出する


# Todo
- pythoのモジュール化
  - main
  - 一つのベンチマークのAVFとWrRdを算出する
  - 一つのベンチマークのページ内のばらつきを調べる （標準偏差）
  - 