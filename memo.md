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

Champsimのビルドとシミュレーション実行
```
$ ./run_command.sh
```

Champsimのシミュレーション結果から、jsonファイルを作成する。このコマンドはシミュレーション実行用のシェルスクリプトと結合予定。
```
$ ./run_txt2csv.sh
```

jsonファイルからpythonファイルの実行
```
$ python AVF_graph.py
```


