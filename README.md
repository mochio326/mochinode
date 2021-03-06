# Node Graph Base

CGWORLD 2018 クリエイティブカンファレンス等で公開されたSQUARE ENIXの内製ツールであるnodalguiフレームワークをリスペクトして作成したノードグラフ用フレームワーク。

http://www.jp.square-enix.com/tech/library/pdf/CGWCC2018_CRAFT.pdf

PyQt4, PyQt5, PySide, PySide2 のどれでも動く、Maya®に依存しない等のポイントも出来るだけリスペクト。
  
## mochinode

ノードグラフの基礎パッケージ

### 搭載機能

##### View
* ビューの操作
  - 拡大（マウスホイール下）
  - 縮小（マウスホイール上）
  - 移動（Alf + 中ドラッグ）
* ノードの選択
  - 選択（マウス左ドラッグで矩形選択）
  - 拡張選択（Ctrl + マウス左ドラッグ）
* 画面フィット
  - シーン全体表示（Aキー）
  - 選択ノードにフィット（Fキー）
* ノード自動整列
  - Viewクラスauto_layoutメソッドを呼び出すことで自動整列
* ノード削除
  - ノードを選択状態でDELキー
  
  
#### Node
* ポートの親子関係
  - ラベルをクリックすることで折り畳みが可能
  - 折り畳み時にポートが非表示になった場合は仮のラインを表示
  
* シグナル

    | name | 説明 |
    ----|---- 
    | moved | 移動t中に発動 |
    | pos_changed | 移動後に発動 |
    | port_expanded | ポートの開閉動作で発動 |
    | port_connect_changed | ポートの接続状態変化で発動 |
    | port_connect | ポートの接続が行われたら発動 |
    | port_disconnect | ポートの接続解除が行われたら発動 |

  
## sample

mochinodeパッケージを利用したサンプルコード

### test_app.py

シンプルなテストアプリケーションサンプル
コード内でノードを定義している

![NodeTool](/images/01.gif)

## test_app2パッケージ

ノードをxmlファイルに定義・管理するサンプル
xml内にノード内での処理を記述して実行を行うことができる。
sampleでは四則演算やIFノード等を実装


## 改訂履歴
* 2019.05.26: 
  - サンプルコードtest_app2パッケージにUndoとRedo機能を実装

* 2019.05.25: 
  - サンプルコードtest_app2パッケージを追加

* 2019.05.24: 初版

## ライセンス

[MIT](https://github.com/mochio326/mochinode/blob/master/LICENSE)
