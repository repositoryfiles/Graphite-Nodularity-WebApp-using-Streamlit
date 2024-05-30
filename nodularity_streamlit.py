import os
import datetime
import streamlit as st
import cv2
import tempfile
import math

# 画像ファイルごとの球状化率はこの変数に格納
nodularity_ISO = []
nodularity_JIS = []

pic_width=1920 # 入力画像のサイズによらず、画像処理や出力画像はこの幅に設定

# 初期値の設定（main関数のst.number_inputで都度設定できるが、初期値を使用環境に応じた設定すればmain関数のst.number_inputは省略できる）
min_grainsize=0.0071 # 画像の幅に対する黒鉛の最小長さ（撮影した画像に応じて設定が必要）

# 丸み係数のしきい値（JISで規定）
marumi_ratio = 0.6 #iso法で形状ⅤとⅥと判定する丸み係数のしきい値

# https://kamedassou.com/python_user_folder/#:~:text=%E3%83%A6%E3%83%BC%E3%82%B6%E3%83%BC%E3%81%AE%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E3%82%92%E5%8F%96%E5%BE%97%E3%81%99%E3%82%8B%E3%81%9F%E3%82%81%E3%81%AE%E9%96%A2%E6%95%B0%20Returns%3A%20str%3A%20%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E3%83%91%E3%82%B9%20%22%22%22%20%23%20%E3%83%A6%E3%83%BC%E3%82%B6%E3%83%BC%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E3%81%AE%E3%83%91%E3%82%B9%E3%82%92%E5%8F%96%E5%BE%97%20user_folder,%3D%20os.path.expanduser%28%22~%22%29%20folder%20%3D%20os.path.join%28user_folder%2C%20%22Downloads%22%29%20return%20folder
def get_user_download_folder():
    """
        ユーザーのダウンロードフォルダを取得するための関数
    Returns:
        str: フォルダパス
    """
    # ユーザーフォルダのパスを取得
    user_folder = os.path.expanduser("~")
    folder = os.path.join(user_folder, "Downloads")

    return folder

# contoursからmin_grainsize未満の小さい輪郭と、画像の端に接している輪郭を除いてcoutours1に格納
def select_contours(contours, pic_width, pic_height, min_grainsize):
    contours1 = []
    for e, cnt in enumerate(contours):
        x_rect, y_rect, w_rect, h_rect = cv2.boundingRect(cnt)
        (x_circle, y_circle), radius_circle = cv2.minEnclosingCircle(cnt)
        if int(pic_width * min_grainsize) <= 2 * radius_circle \
            and 0 < int(x_rect) and 0 < int(y_rect) and \
            int(x_rect + w_rect) < pic_width and int(y_rect + h_rect) < pic_height:
            contours1.append(cnt)
    return contours1

# 輪郭の長軸の中心座標と、最遠点対の半分の長さを求める（キャリパ法）
def get_graphite_length(hull):
    max_distance = 0
    for i, hull_x in enumerate(hull):
        for j, hull_y in enumerate(hull):
            if j + 1 < len(hull) and i != j + 1:
                dis_x = hull[j+1][0][0] - hull[i][0][0]
                dis_y = hull[j+1][0][1] - hull[i][0][1]
                dis = math.sqrt(dis_x**2 + dis_y**2)
                if dis > max_distance:
                    max_distance = dis # 最遠点対の距離を更新
                    x = dis_x * 0.5 + hull[i][0][0] # 最遠点対の中点を更新
                    y = dis_y * 0.5 + hull[i][0][1] # 最遠点対の中点を更新
    return(x, y, max_distance * 0.5) # 最遠点対の半分の長さ（円の半径）

# 「評価開始」ボタンを押した後の処理（黒鉛球状化率の評価）
def eval_graphite_nodularity():
    # ファイルの読み込み
    for uploaded_file in uploaded_files:
        temp_file = tempfile.NamedTemporaryFile(delete=False)

        st.write(uploaded_file.name)

        temp_file.write(uploaded_file.read())
        img_color_ISO = cv2.imread(temp_file.name)
        temp_file.close()

        img_height, img_width, channel = img_color_ISO.shape # 画像のサイズ取得

        # 画像処理や出力画像のサイズ計算（pic_width, pic_height）
        pic_height=int(pic_width * img_height / img_width)
        img_color_ISO = cv2.resize(img_color_ISO, (pic_width, pic_height)) # 読み込んだ画像ファイルのサイズ変換
        img_color_JIS = img_color_ISO.copy() #img_colorのコピーの作成

        # カラー→グレー変換、白黒反転の二値化、輪郭の検出、球状化率の評価に用いる輪郭の選別
        img_gray = cv2.cvtColor(img_color_ISO, cv2.COLOR_BGR2GRAY)
        ret, img_inv_binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        contours, hierarchy = cv2.findContours(img_inv_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours1 = select_contours(contours, pic_width, pic_height, min_grainsize) # 球状化率の評価に用いる輪郭をcoutours1に格納

        # 黒鉛の面積と黒鉛の長軸の中心座標、長軸の半分の長さの計算、丸み係数の算出
        sum_graphite_areas = 0
        sum_graphite_areas_5and6 = 0
        num_graphite1 = num_graphite2 = num_graphite3 = num_graphite4 = num_graphite5 = 0

        for i, cnt in enumerate(contours1):
            graphite_area = cv2.contourArea(cnt)
            sum_graphite_areas += graphite_area
            hull = cv2.convexHull(cnt) # 凸包
            x, y, graphite_radius = get_graphite_length(hull) # 輪郭の長軸の中心座標（x, y）と長軸の半分の長さ(graphite_radius)
            marumi = graphite_area / ((graphite_radius ** 2) * math.pi) #丸み係数

            # ISO法により形状ⅤとⅥの黒鉛を判定し、それらの黒鉛の輪郭を青色で描画
            if marumi >= marumi_ratio:
                sum_graphite_areas_5and6 += graphite_area
                cv2.drawContours(img_color_ISO, contours1, i, (0, 0, 255, 255), -1) #青

            # JIS法による形状分類
            if marumi <= 0.2:
                num_graphite1 += 1
                cv2.drawContours(img_color_JIS, contours1, i, (255, 0, 0, 255), -1) #赤
            if 0.2 < marumi <= 0.4:
                num_graphite2 += 1
                cv2.drawContours(img_color_JIS, contours1, i, (128, 0, 128, 255), -1) #紫
            if 0.4 < marumi <= 0.7:
                num_graphite3 += 1
                cv2.drawContours(img_color_JIS, contours1, i, (0, 255, 0, 255), -1) #緑
            if 0.7 < marumi <= 0.8:
                num_graphite4 += 1
                cv2.drawContours(img_color_JIS, contours1, i, (0, 255, 255, 255), -1) #水色
            if 0.8 < marumi:
                num_graphite5 += 1
                cv2.drawContours(img_color_JIS, contours1, i, (0, 0,255, 255), -1) #青

        # 球状化率（ISO法）
        nodularity_ISO.append(sum_graphite_areas_5and6 / sum_graphite_areas * 100)

        # 球状化率（JIS法）
        nodularity_JIS.append((0.3 * num_graphite2 + 0.7 * num_graphite3 + 0.9 * num_graphite4 + 1.0 * num_graphite5)/ len(contours1) * 100)

        # 黒鉛を形状分類した画像の画面表示
        st.image(img_color_ISO)
        st.image(img_color_JIS)

        # 黒鉛を形状分類した画像の保存（ダウンロードフォルダに保存される）
        src = uploaded_file.name
        idx = src.rfind(r'.')
        result_ISO_filename = get_user_download_folder() + "/" + src[:idx] + "_nodularity(ISO)." + src[idx+1:]
        result_JIS_filename = get_user_download_folder() + "/" + src[:idx] + "_nodularity(JIS)." + src[idx+1:]

        # ブラウザ表示と保存されるファイルの色を揃えるための処理
        img_color_ISO_BGR = cv2.cvtColor(img_color_ISO, cv2.COLOR_RGB2BGR)
        img_color_JIS_BGR = cv2.cvtColor(img_color_JIS, cv2.COLOR_RGB2BGR)

        if os.access(result_ISO_filename, os.R_OK):
            cv2.imwrite(result_ISO_filename, img_color_ISO_BGR)
        else:
            st.write("ファイルに読み取り権限がありません")
        if os.access(result_JIS_filename, os.R_OK):
            cv2.imwrite(result_JIS_filename, img_color_JIS_BGR)
        else:
            st.write("ファイルに読み取り権限がありません")

    # 球状化率などのデータ画面表示
    st.write("最小黒鉛サイズ（評価に用いる黒鉛の最小長さ÷画像の幅）, {:.4f}".format(min_grainsize))
    st.write("丸み係数のしきい値, {:.3f}".format(marumi_ratio))
    st.write("画像処理と出力画像の幅, {} (画素)".format(pic_width))
    st.write("ファイル名, 球状化率_ISO法(%), 球状化率_JIS法(%)")
    for i in range(len(uploaded_files)):
        st.write("{}, {:.2f}, {:.2f}" .format(uploaded_files[i].name, nodularity_ISO[i], nodularity_JIS[i]))

    # 球状化率などのデータの保存（ダウンロードフォルダに保存される）
    now = datetime.datetime.now()
    output_file = get_user_download_folder() + '/nodularity_{0:%Y%m%d%H%M}'.format(now) + ".csv"

    if os.access(output_file, os.R_OK):
        with open(output_file, mode='w') as f1:
            print("最小黒鉛サイズ, {:.4f}".format(min_grainsize), file = f1)
            print("丸み係数のしきい値, {:.3f}".format(marumi_ratio), file = f1)
            print("画像処理と出力画像の幅, {}".format(pic_width), file = f1)
            print("ファイル名, 球状化率_ISO法(%), 球状化率_JIS法(%)", file = f1)
            for i in range(len(uploaded_files)):
                print("{}, {:.2f}, {:.2f}" .format(uploaded_files[i].name, nodularity_ISO[i], nodularity_JIS[i]), file = f1)
    else:
        st.write("ファイルに読み取り権限がありません")


if __name__ == '__main__':
    uploaded_files = st.file_uploader(label='画像ファイル', type=['png', 'jpeg', 'jpg'], accept_multiple_files=True)
    pic_width_scale = st.number_input("画像の幅（μm）", min_value=1, max_value=None, format=None, value=1420)
    min_grain_length = st.number_input("評価する黒鉛のサイズ（μm）", min_value=1, max_value=None, format=None, value=10)
    min_grainsize = min_grain_length / pic_width_scale

    if len(uploaded_files) != 0:
        if st.button('評価開始'):
            eval_graphite_nodularity()
