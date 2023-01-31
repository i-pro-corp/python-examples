'''
Copyright 2023 i-PRO Co., Ltd.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

##########
#
# i-PRO AIアプリケーションメタデータ受信サンプル
# i-PRO AI Application Metadata Receiver Sample
#
#   AIカメラからのONVIFストリームを受信し、イベント発生時のJPEG画像をファイルに保存する
#       * 実行するとカメラとネゴシエーションの後、メタ情報受信待ちになります
#       * 終了手段は用意されていないので、Ctlr+C等で強制終了してください
#   Receive ONVIF stream from AI camera and save JPEG image to file when event occurs.
#       * After execution, the camera negotiates with the camera and waits for the meta information to be received.
#       * No exit method is provided, so please force close with Ctlr+C, etc.
#
#   Requirements:
#       websocket-client    https://github.com/websocket-client/websocket-client
#         pip3 install websocket-client
# 
#   Environment:
#        本サンプルは、以下環境で動作確認をおこなっています。
#        This sample has been tested in the following environment.
#            MK-DVASTNP01  v2.00
#            WV-XAE200WUX  v1.31
#
#   Usage:
#        以下の箇所を使用するカメラの設定に合わせて変更してください
#        Change the following sections to match the settings of the camera you are using.
#           _cam_ip = "192.168.0.10"    # Change to match your camera setting
#           _cam_id = "user-id"         # Change to match your camera setting
#           _cam_pwd = "password"       # Change to match your camera setting
#
#   Note:
#       本サンプルはAIアプリケーションの送信電文を開発用途で確認するためのもので、例外処理・セキュリティの考慮等は対応されていません。
#       使用者の自己責任の元でご使用ください。
#       This sample is intended to verify the sent telegrams of AI applications for development purposes, and does not support
#        exception handling, security considerations, etc.
#        Please use at your own risk.
#
#       ONVIFは、ONVIF,Inc.の商標です。
#       ONVIF is a trademark of ONVIF, Inc.
#       
#   Author:
#       Ozawa Kazuya (小澤 和哉)
#
#   History:
#       2023/01/24 ver 1.00 初版
#       2023/01/26 ver 1.01 JPEGタグを含まないデータを受信した時にスキップする処理を追加
#                           1回のrecv()でXMLデータを受信した時の処理を追加
#       2023/01/30 ver 1.02 コメント追記・修正
#       2023/01/30 ver 1.03 時刻にミリ秒が付与されている時に、保存ファイル名が..jpgとなってしまう不具合を修正
#       2023/01/31 ver 1.04 コメント追記・修正
##########
import urllib.request
import websocket
import base64
import threading
import os

# カメラ接続情報
_cam_ip = "192.168.0.10"    # Change to match your camera setting
_cam_id = "user-id"         # Change to match your camera setting
_cam_pwd = "password"       # Change to match your camera setting

# Websocket通信用変数
_ws_h = None
_ws_uri = f"ws://{_cam_ip}/rtsp-over-websocket"
_rtsp_start_uri = f"rtsp://{_cam_ip}/MediaInput/stream_1?event=1"
_rtsp_base_uri = ""
_rtsp_sid = ""
_rtsp_cseq = 1
_rtsp_state = 0
    # 0 : OPTIONS応答待ち
    # 1 : DESCRIBE応答待ち
    # 2 : SETUP応答待ち
    # 3 : Meta受信中 
_rtsp_keepalive_time = 10

# メタデータ受信用変数
_xml_rcvstate = 0
    # 0 : XML受信開始前
    # 1 : XMLデータ受信開始
    # 2 : XMLデータ受信終了
_xml_rcvdata = None

# 受信データ保存フォルダ名(カレントディレクトリ配下に作成)
_img_savedir = "image"



##########
#   Digest認証用情報を取得する
#
#   Note:
#       ダミーのCGIを送信し、認証ヘッダを取得する
##########
def digest_getAuthHeader(cam_ip, cam_id, cam_pwd):
    # 送信CGI
    cam_auth_uri = f"http://{cam_ip}/cgi-bin/getinfo?FILE=1"

    retValue = None

    # 認証情報設定
    pass_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    pass_mgr.add_password(realm=None, uri=cam_auth_uri, user=cam_id, passwd=cam_pwd)
    auth_handler = urllib.request.HTTPDigestAuthHandler(pass_mgr)
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)

    # CGIの送信
    req = urllib.request.Request(cam_auth_uri)
    with urllib.request.urlopen(req) as httpres:
        retValue = req.get_header("Authorization")

    return retValue


##########
#   RTSP　キープアライブコマンドを送信する
#
#   Note:
#       定期的にキープアライブを送信しないと、カメラから接続を切断される為
##########
def metarcv_keepalive():
    # コマンド送信
    _ws_h.send(
        f"GET_PARAMETER {_rtsp_base_uri} RTSP/1.0\r\n" + \
        f"CSeq: {_rtsp_cseq}\r\n" + \
        f"Session:{_rtsp_sid}\r\n" + \
        f"\r\n"
    )
    threading.Timer(_rtsp_keepalive_time, metarcv_keepalive).start()


##########
#   RTSP　メッセージ受信
#
#   Note:
##########
def on_message(ws, message):
    # グローバル変数参照
    global _rtsp_base_uri
    global _rtsp_sid
    global _rtsp_cseq
    global _rtsp_state
    global _xml_rcvdata
    global _xml_rcvstate

    # RTSPコマンドのレスポンスの場合
    if (type(message) == str):
        if ("200 OK" not in message):
            ws.close()
            return
        _rtsp_cseq += 1

        # 最初のOPTIONSに対する応答
        if (0 == _rtsp_state):
            # DESCRIBE送信
            ws.send(
                f"DESCRIBE {_rtsp_start_uri} RTSP/1.0\r\nCSeq: {_rtsp_cseq}\r\nAccept: application/sdp\r\n\r\n"
            )
            _rtsp_state += 1
        # DESCRIBEに対する応答
        elif (1 == _rtsp_state):
            # 応答から、メタストリーム受信用アドレスを取得する
            params = message.split("\r\n")
            for param in params:
                items = param.split(": ")
                if ("Content-Base" == items[0]):
                    _rtsp_base_uri = items[1]
                    break
            # SETUP送信
            ws.send(
                f"SETUP {_rtsp_base_uri}trackID=4 RTSP/1.0\r\n" + \
                f"CSeq: {_rtsp_cseq}\r\n" + \
                f"Transport: RTP/AVP/TCP;unicast;interleaved=0-1\r\n" + \
                f"\r\n"
            )
            _rtsp_state += 1
        # SETUPに対する応答
        elif (2 == _rtsp_state):
            # 応答から、キープアライブに付与するセッションIDを取得する
            params = message.split("\r\n")
            for param in params:
                items = param.split(": ")
                if ("Session" == items[0]):
                    _rtsp_sid = items[1].split(";")[0]
                    break
            # PLAY送信
            ws.send(
                f"PLAY {_rtsp_base_uri} RTSP/1.0\r\n" + \
                f"CSeq: {_rtsp_cseq}\r\n" + \
                f"Session:{_rtsp_sid}\r\n" + \
                f"\r\n"
            )

            # キープアライブスレッドを起動
            threading.Thread(target=metarcv_keepalive).start()
            _rtsp_state += 1
    
    # Metaデータの先頭4byteはWebSocketの識別情報、その後の12byteはRTPヘッダ
    # RTPヘッダのPayload typeが96以上(dynamic)の場合のみ処理する
    elif (type(message) == bytes and (message[5] & 0x7f) >= 96):
        # 受信データのタグ
        # XMLデータをParseする事が必要だが、サンプルアプリのため簡易に文字列検索でデータを取り出す
        key_s_xml = "<?xml version="
        key_e_xml = "</tt:MetaDataStream>"
        key_s_date = "<tt:Message UtcTime="
        key_s_img = "<xsd:base64Binary>"
        key_e_img = "</xsd:base64Binary>"

        # 受信データから識別情報・RTPヘッダを取り除く
        stripdata = message[16:].decode()

        # XMLデータの開始を受信
        if (key_s_xml in stripdata):
            # 1回で全電文を受信している
            if (key_e_xml in stripdata):
                _xml_rcvdata = stripdata
                _xml_rcvstate = 2
            else:
                # 分割でXMLデータ受信を開始する
                _xml_rcvdata = stripdata
                _xml_rcvstate = 1
                return
        elif (key_e_xml in stripdata):
            # XMLの最後を受信
            _xml_rcvdata += stripdata
            _xml_rcvstate = 2
        else:
            # 途中のデータを受信
            if (1 == _xml_rcvstate):
                _xml_rcvdata += stripdata
            return

        # 受信データから日付を取得
        pos_key_s_date = _xml_rcvdata.find(key_s_date)
        if (-1 == pos_key_s_date):
            print("not exist date")
            _xml_rcvstate = 0
            return
        value_date = _xml_rcvdata[pos_key_s_date+len(key_s_date)+1:pos_key_s_date+len(key_s_date)+20]

        # 受信データからJPEGイメージを取得
        pos_key_s_img = _xml_rcvdata.find(key_s_img)
        pos_key_e_img = _xml_rcvdata.find(key_e_img)
        # JPEGイメージ用タグが存在しない場合は終了
        if (-1 == pos_key_s_img or -1 == pos_key_e_img):
            print("not exist jpeg")
            _xml_rcvstate = 0
            return

        value_img = _xml_rcvdata[pos_key_s_img+len(key_s_img):pos_key_e_img]
        # JPEGデータはBase64でエンコードされているので元に戻す
        img_savedata = base64.b64decode(value_img.encode())

        # 保存するファイル名を設定
        img_savefname = _img_savedir + "/" + value_date.replace(":", "-") + ".jpg"
        print(img_savefname)
        #ファイルに保存
        with open(img_savefname, 'bw') as fd:
            fd.write(img_savedata)

        # ステータスを元に戻す
        _xml_rcvstate = 0


##########
#   RTSP　エラー発生
#
#   Note:
##########
def on_error(ws, error):
    print(error)


##########
#   RTSP　通信終了
#
#   Note:
##########
def on_error(ws, error):
    print(error)
def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


##########
#   RTSP　通信開始
#
#   Note:
##########
def on_open(ws):
    print("Opened connection")
    # OPTIONS送信
    ws.send(f"OPTIONS {_rtsp_start_uri} RTSP/1.0\r\nCSeq: {_rtsp_cseq}\r\n\r\n")


##########
#   RTSP　Main処理
#
#   Note:
##########
if __name__ == "__main__":
    # JPEG保存用フォルダ作成
    try:
        os.mkdir(_img_savedir)
    except Exception as e:
        print("")

    # 通信認証情報取得        
    authInfo = digest_getAuthHeader(_cam_ip, _cam_id, _cam_pwd)

    # WebSocket通信開始
    _ws_h = websocket.WebSocketApp(
        _ws_uri,
        subprotocols = ['binary'], 
        header=[f"Authorization: {authInfo}"],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)

    _ws_h.run_forever(reconnect=5)

