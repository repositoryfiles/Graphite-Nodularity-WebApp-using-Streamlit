# nodularity_streamlit.py
 Web app for determining nodularity of graphite using streamlit and OpenCV

# 概要
球状黒鉛鋳鉄品（FCD）の組織画像について、JIS G5502-2022 球状黒鉛鋳鉄品のISO法およびJIS法によって黒鉛球状化率を求めるプログラムです。このJISでは、次式で定義される丸み係数を使って黒鉛球状化率を求めることを規定しています。

```math
丸み係数 = \frac{黒鉛の面積}{黒鉛の最大軸長を直径とする円の面積}　　　(1)
```

作成したプログラムでは、式(1)の**黒鉛の最大軸長**を**黒鉛の凸包の最遠点対の長さ**から求めています。

# 動作環境
以下のサイトを参考にして仮想環境を設定しました。
https://qiita.com/hiyasichuka/items/68373957bd021435a4a0

設定した仮想環境については、requirements.txt を参照ください。

# 使い方
- 倍率100倍で撮影した組織画像をご用意ください。このURLにあるjpgファイルはテスト用です。
- 設定した仮想環境において、コマンドプロンプトで以下のコマンドを実行します。<br>
streamlit run c:/Python/Nodularity_streamlit.py

- 「Browse files」でファイルを選択します。ファイルは複数選択できます。

- 読み込む画像のパラメータを設定します。**画像の幅**には、組織画像の幅いっぱいにスケールバーを入れたと想定したときの数値をμm単位で入力します。テスト用画像については、画像の幅は1420となります。

<img src="https://github.com/repositoryfiles/New-Nodularity-WebApp/assets/91704559/e9a0cee6-571b-4007-b819-e720606dadb1" width="400">

図　組織画像の幅いっぱいに入れたスケールバーと数値の例

- **評価する黒鉛のサイズ**の数値をμm単位で入力します。JIS G5502：2022では10μmとされていますので、10と入力します。
- **評価開始**をクリックします。
- 結果が画面に表示されるとともに、ダウンロードフォルダにファイルが保存されます。

# 保存されるファイルについて
- csvファイル（ファイル名：nodularity_日付と時刻.csv）<br>
ファイルの内容
    - 最小黒鉛サイズ…評価する黒鉛のサイズ÷画像の幅
    - 丸み係数のしきい値…ISO法で用いたしきい値
    - 画像処理と出力画像の幅…画像処理と保存された画像の画素数
    - ファイル名	 球状化率_ISO法(%)	 球状化率_JIS法(%)

- 画像ファイル<br>
ファイル名の付け方：元画像のファイル名_nodularity(ISO)または(JIS).拡張子<br>
ファイルの内容
    - ISO法　ISO法で黒鉛の形状を色分けしたもの（青：ⅤとⅥ、赤：Ⅰ～Ⅳ）
    - JIS法　JIS法で黒鉛の形状を色分けしたもの（Ⅰ：赤、Ⅱ：紫、Ⅲ：緑、Ⅳ：水色、Ⅴ：青）
 
# 注意事項

1. JIS G5502-2022の内容を理解の上、お使いください。<br>
2. プログラムの使用結果について当方は責任は負いません。

# 開発環境
- Windows11
- OpenCV 4.10.0
- streamlit 1.40.0

詳しくは requirements.txt を参照ください。



