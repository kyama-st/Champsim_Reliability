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

# コードで調整したいこと
- ~~pythonファイル実行時にアドレスとAVFを格納するCSVディレクトリの作成をすること。~~
- 平均値を計算してそれをCSVファイルに格納
  - CSVファイルを元に、ヒストグラムを作成

## 平均値格納ファイル構成
index benchmark AVF
0 perlbench 0.55
1

# ページ粒度のAVFを計算する
ページ粒度のAVFの定義：ライン粒度のAVFの平均値（な気がする）
→In this work, we perform AVF analysis on memory at acache line granularity because memory reads and writes oc-cur at cache line granularity. We sum the AVF of individualcache lines to compose the AVF of a page and divide it bythe size of the hardware structure as per Equation 
とあるので、ビット幅でわると各びっとで出る

## Todo
pageとaddressの関係を把握する。理想はaddress -> pageの関数的なものがあれば最高

## 調べてみたこと
DRAM PAGES: 1048576 DRAM SIZE: 4096
((DRAM_SIZE<<10)>>2) ：<< は左シフト、>>は右シフト
これは、DRAM_SIZEを10bit左シフトして、2bit右シフトしている
わかってないこと：
CPUからの命令からアドレスがどうやって変換されているのか
page tableのアドレスと、LLCやメモリアドレスの違いって何？
DRAMのWQ->entry[index].address
WQの構造体はpacket_queue, entoryの構造体はpacket（イメージ WQの一つ一つの要素がエントリに近い）
DRAMのWQにインデックスが追加されるとき -> LLCがミスしている -> LLCのWQに追加されるとき -> L2D -> 
DRAM_RQ -> LLC_RQ -> L2C_RQ -> L1D_RQ -> DTLB_RQ 
**L1D_RQ とDTLB_RQでアドレス変換がされている**
DTLB_RQに追加するのはooo_cpu.cc内
次のadd_rqが呼ばれているのは、、？

dram_controller:process -> operate -> main.cc main関数 
llc


