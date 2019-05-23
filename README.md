# Node Graph Base


CGWORLD 2018 クリエイティブカンファレンス等で公開されたSQUARE ENIXの内製ツールであるnodalguiフレームワークをリスペクトして作成したノードグラフ用フレームワーク。

http://www.jp.square-enix.com/tech/library/pdf/CGWCC2018_CRAFT.pdf

PyQt4, PyQt5, PySide, PySide2 のどれでも動く、Maya®に依存しない等のポイントも出来るだけリスペクト。

## 搭載機能

### View
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
  
  
### Node
* ポートの親子関係
  - ラベルをクリックすることで折り畳みが可能
  - 折り畳み時にポートが非表示になった場合は仮のラインを表示
  
  
  
## サンプル

test_app.pyがシンプルなテストアプリケーションサンプル

![NodeTool](/images/01.gif)


## 改訂履歴
* 2019.05.24: 初版

## ライセンス

[MIT](https://github.com/mochio326/mochinode/blob/master/LICENSE)
