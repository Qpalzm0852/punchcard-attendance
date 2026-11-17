import base64
import os

import wx
import wx.xrc
import wx.grid
import _thread
import cv2
import json
import sqlite3
import time
import requests


class MySignFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"人脸打卡识别系统", pos=wx.DefaultPosition,
                          size=wx.Size(1000, 700), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.init_data()
        self.initMenu()
    
    def init_data(self):
        self.on = True  # 注册标识变量
        self.reg_msg = None  # 注册时显示信息
        self.del_msg = None  # 删除时显示信息
        self.search_msg = None  # 查询时显示信息
        self.command = None  # 当前执行的命令
        self.sql_name = 'my_Punch.db'  # 数据库名字
        self.recognize = True  # 打卡
        self.registration = False  # 注册
        self.search = True  # 查询
        self.c = None  # 定义游标
        self.conn = None  # 连接名
        self.user_id = []  # 用户ID
        self.user_name = []  # 用户名
        self.time_1 = []  # 上班时间
        self.logcat_late = []  # 打卡时间
        self.time_2 = []  # 下班时间
        self.dur_time = []  # 持续时间

    def initMenu(self):
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_notebook1 = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_panel1 = wx.Panel(self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.btnSign = wx.Button(self.m_panel1, wx.ID_ANY, u"打卡", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.btnSign, 0, wx.ALL, 5)

        # 使用wx.Image()添加背景图片
        self.imageBackgroud = wx.Image(500, 400)
        # 当id的值为-1或者wx.ID_ANY时，系统会随机分配一个id
        self.bmpSign = wx.StaticBitmap(self.m_panel1, wx.ID_ANY, wx.Bitmap(self.imageBackgroud), wx.Point(0, 40))
        bSizer2.Add(self.bmpSign, 0, wx.ALL, 5)

        self.m_panel1.SetSizer(bSizer2)
        self.m_panel1.Layout()
        bSizer2.Fit(self.m_panel1)
        self.m_notebook1.AddPage(self.m_panel1, u"员工打卡", True)
        self.m_panel2 = wx.Panel(self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        self.txtRegisterNum = wx.TextCtrl(self.m_panel2, wx.ID_ANY, u"工号", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer3.Add(self.txtRegisterNum, 0, wx.ALL, 5)

        self.txtName = wx.TextCtrl(self.m_panel2, wx.ID_ANY, u"姓名", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer3.Add(self.txtName, 0, wx.ALL, 5)

        self.btnRegister = wx.Button(self.m_panel2, wx.ID_ANY, u"注册", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer3.Add(self.btnRegister, 0, wx.ALL, 5)

        # 使用wx.Image()添加背景图片
        self.imageBackgroud1 = wx.Image(500, 400)
        self.bmpRegister = wx.StaticBitmap(self.m_panel2, -1, wx.Bitmap(self.imageBackgroud1), wx.Point(0, 60))
        bSizer3.Add(self.bmpRegister, 0, wx.ALL, 5)

        self.m_panel2.SetSizer(bSizer3)
        self.m_panel2.Layout()
        bSizer3.Fit(self.m_panel2)
        self.m_notebook1.AddPage(self.m_panel2, u"人脸注册", False)
        self.m_panel3 = wx.Panel(self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        self.txtDeleteNum = wx.TextCtrl(self.m_panel3, wx.ID_ANY, u"工号", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer4.Add(self.txtDeleteNum, 0, wx.ALL, 5)

        self.btnDelete = wx.Button(self.m_panel3, wx.ID_ANY, u"删除", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer4.Add(self.btnDelete, 0, wx.ALL, 5)

        self.m_panel3.SetSizer(bSizer4)
        self.m_panel3.Layout()
        bSizer4.Fit(self.m_panel3)
        self.m_notebook1.AddPage(self.m_panel3, u"人脸删除", False)
        self.m_panel4 = wx.Panel(self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        self.btnSearch = wx.Button(self.m_panel4, wx.ID_ANY, u"查询", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer5.Add(self.btnSearch, 0, wx.ALL, 5)

        self.m_panel4.SetSizer(bSizer5)
        self.m_panel4.Layout()
        bSizer5.Fit(self.m_panel4)
        self.m_notebook1.AddPage(self.m_panel4, u"信息查询", False)

        bSizer1.Add(self.m_notebook1, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)

        # 按钮事件绑定
        self.btnSign.Bind(wx.EVT_BUTTON, self.sign_face)
        self.btnRegister.Bind(wx.EVT_BUTTON, self.register_face)
        self.btnDelete.Bind(wx.EVT_BUTTON, self.delete_face)
        self.btnSearch.Bind(wx.EVT_BUTTON, self.search_info)

    # 用户打卡
    def sign_face(self, event):
        # 创建子线程，按钮调用这个方法，
        self.command = 'search'
        self.start_camera_worker()

    # 注册用户信息
    def register_face(self, event):
        self.command = 'registration'
        self.start_camera_worker()

    def start_camera_worker(self):
        self.btnSign.Disable()
        self.btnRegister.Disable()
        self.btnDelete.Disable()
        self.btnSearch.Disable()
        _thread.start_new_thread(self.face_tracking, ())

    # 删除人脸信息
    def delete_face(self, event):
        var = self.txtDeleteNum.GetValue()
        try:
            self.face_getlist(var)
        except (requests.RequestException, KeyError, ValueError):
            self.del_msg = 'Check the face service configuration and connection.'
        finally:
            if self.conn is not None:
                self.conn.close()
        wx.MessageBox(self.del_msg, 'message', wx.OK | wx.ICON_INFORMATION)

    # 打卡信息查询
    def search_info(self, event):
        self.Query_data()
        grid = wx.grid.Grid(self, pos=(10, 80), size=(968, 560))
        grid.CreateGrid(100, 6)
        for i in range(100):
            for j in range(6):
                grid.SetCellAlignment(i, j, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        grid.SetColLabelValue(0, "工号")  # 第一列标签
        grid.SetColLabelValue(1, "姓名")
        grid.SetColLabelValue(2, "上班打卡时间")
        grid.SetColLabelValue(3, "是否迟到")
        grid.SetColLabelValue(4, "下班打卡时间")
        grid.SetColLabelValue(5, "工作时长(h)")

        grid.SetColSize(0, 100)
        grid.SetColSize(1, 100)
        grid.SetColSize(2, 150)
        grid.SetColSize(3, 150)
        grid.SetColSize(4, 150)
        grid.SetColSize(5, 150)

        grid.SetCellTextColour(3, 3, wx.GREEN)
        for i, id in enumerate(self.user_id[:grid.GetNumberRows()]):
            grid.SetCellValue(i, 0, str(id))
            grid.SetCellValue(i, 1, self.user_name[i])
            grid.SetCellValue(i, 2, self.time_1[i])
            grid.SetCellValue(i, 3, self.logcat_late[i])
            grid.SetCellValue(i, 4, self.time_2[i])
            grid.SetCellValue(i, 5, str(self.dur_time[i]))

    """
	*********************数据库操作start******************************
	"""
    """
	    数据库连接
	"""

    def connect_sql(self):
        conn = sqlite3.connect(self.sql_name)
        print("Opened database successfully!")
        c = conn.cursor()
        self.c = c
        self.conn = conn

    """
	    创建数据表
	"""

    def create_table(self):
        c, conn = self.c, self.conn
        c.execute('''CREATE TABLE if not exists attendance
	           (user_id CHAR(50) PRIMARY KEY     NOT NULL,
	           user_name      CHAR(50)    NOT NULL,
	           sign_in_time Datetime,
	           checking_state  CHAR(10) NOT NULL,
	           sign_out_time Datetime,
	           working_time float);''')
        conn.commit()

    """
	    查询数据库中的数据
	"""

    def Query_data(self):
        self.user_id = []
        self.user_name = []
        self.time_1 = []
        self.logcat_late = []
        self.time_2 = []
        self.dur_time = []
        self.connect_sql()
        self.create_table()
        c, conn = self.c, self.conn
        c.execute("select * from attendance")
        #         print(c.fetchall())

        for i in c.fetchall():
            self.user_id.append(i[0])
            self.user_name.append(i[1])
            if i[2] == None:
                self.time_1.append('None')
            else:
                self.time_1.append(i[2])
            self.logcat_late.append(i[3])
            if i[4] == None:
                self.time_2.append('None')
            else:
                self.time_2.append(i[4])
            if i[5] == None:
                self.dur_time.append('None')
            else:
                self.dur_time.append(i[5])
        self.conn.close()

    """
	*********************数据库操作end******************************
	"""

    """
	    获取access_tokens
	"""

    def access_tokens(self):
        response = requests.get(
            "https://aip.baidubce.com/oauth/2.0/token",
            params={
                "grant_type": "client_credentials",
                "client_id": os.environ["BAIDU_FACE_API_KEY"],
                "client_secret": os.environ["BAIDU_FACE_SECRET_KEY"],
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    """
	    获取追踪到图片的BASE64格式并返回参数列表
	"""

    def imgdata(self, image_bytes, name=None, user_list=None):
        pic = base64.b64encode(image_bytes)

        # 人脸搜索params
        if name == 'face_search':
            params = json.dumps({"image": str(pic, 'utf-8'),
                                 "image_type": "BASE64", "group_id_list": os.environ["BAIDU_FACE_GROUP_ID"], "quality_control": "LOW",
                                 "liveness_control": "NORMAL"})
        # 人脸注册params
        elif name == 'face_registration':
            params = json.dumps({"image": str(pic, 'utf-8'), "image_type": "BASE64",
                                 "group_id": os.environ["BAIDU_FACE_GROUP_ID"], "user_id": user_list[0], "user_info": user_list[1],
                                 "quality_control": "LOW", "liveness_control": "NORMAL"})
        # 人脸质量检测params
        else:
            params = json.dumps(
                {"image": str(pic, 'utf-8'), "image_type": "BASE64", "face_type": "LIVE", "quality_control": "LOW"})
        return params

    '''
	    调用人脸质量检测API
	'''

    def picture_quality(self, image_bytes):
        access_token = self.access_tokens()
        assert access_token != None, 'access_token is None'
        params = self.imgdata(image_bytes)
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers, timeout=15).json()
        if response['error_msg'] == 'SUCCESS':
            score = response['result']['face_list'][0]['face_probability']
            print(score, type(score))
            if (type(score) == float) | (type(score) == int):
                if score >= 0.8:
                    self.recognize = False
                else:
                    self.recognize = True
                    print(score)

        else:
            self.recognize = True
            print(response['error_msg'])

    """
	    调用人脸注册API
	"""

    def face_registration(self, image_bytes, user):
        c, conn = self.c, self.conn
        c.execute("select user_id from attendance where user_id=?", (user[0],))
        conn.commit()
        l = c.fetchone()
        if l is not None:
            self.reg_msg = 'You are already enrolled.'
            self.on = False
        else:
            access_token = self.access_tokens()
            params = self.imgdata(image_bytes, 'face_registration', user)
            response = requests.post(
                'https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add',
                params={'access_token': access_token},
                data=params,
                headers={'content-type': 'application/json'},
                timeout=15,
            ).json()
            if response['error_msg'] == 'SUCCESS':
                c.execute(
                    "insert into attendance(user_id,user_name,checking_state) values(?,?,'未打卡')",
                    (user[0], user[1]),
                )
                conn.commit()
                self.registration = True
                self.reg_msg = 'Enrollment succeeded.'
            elif response['error_msg'] == 'face already exist':
                self.reg_msg = 'This face already exists in the configured group.'
            else:
                self.reg_msg = 'Face enrollment failed.'
            self.on = False
        self.c.close()

    '''
	获取用户人脸列表并删除
	'''

    def face_getlist(self, user_id):
        self.connect_sql()
        self.create_table()
        c, conn = self.c, self.conn
        c.execute("DELETE FROM attendance where user_id=?", (user_id,))
        conn.commit()
        access_token = self.access_tokens()
        assert access_token != None, 'access_token is None'

        # 人脸删除
        def face_delete(user_idx, face_token):
            request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/face/delete"

            params = json.dumps({"user_id": user_idx, "group_id": os.environ["BAIDU_FACE_GROUP_ID"], "face_token": face_token})
            request_url = request_url + "?access_token=" + access_token
            headers = {'content-type': 'application/json'}
            response = requests.post(request_url, data=params, headers=headers, timeout=15).json()
            if response['error_code'] == 0:
                del_msg = "删除成功"
            else:
                del_msg = response['error_msg']
            print(del_msg)
            self.del_msg = del_msg

        # 获取用户的face_token
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/face/getlist"
        params = json.dumps({"user_id": user_id, "group_id": os.environ["BAIDU_FACE_GROUP_ID"]})
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers, timeout=15).json()
        if response['error_msg'] == 'SUCCESS':
            for i in response['result']['face_list']:
                face_token = i['face_token']
                face_delete(user_id, face_token)
        else:
            self.del_msg = response['error_msg']
            print(response['error_msg'])

        self.c.close()

    """
	    调用人脸搜索API
	"""

    def face_search(self, image_bytes):
        c, conn = self.c, self.conn
        access_token = self.access_tokens()
        assert access_token != None, 'access_token is None'
        params = self.imgdata(image_bytes, 'face_search')
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers, timeout=15).json()
        if response['error_msg'] == 'SUCCESS':
            self.search = False
            user_id = response['result']['user_list'][0]['user_id']
            times = time.time()
            this_time = time.localtime(times)
            punch_time = "{}-{}-{} {}:{}:{}".format(this_time.tm_year, this_time.tm_mon, this_time.tm_mday,
                                                    this_time.tm_hour, this_time.tm_min, this_time.tm_sec)
            c.execute("select checking_state from attendance where user_id=?", (user_id,))
            record = c.fetchone()
            if record is None:
                self.search_msg = 'No local attendance record for this face.'
                self.on = False
                return
            if record[0] == '未打卡':
                print('上班打卡')
                if this_time.tm_hour >= 8:
                    stats = '是'
                    self.search_msg = '上班打卡成功!您迟到了!'
                    print('迟到了')
                else:
                    stats = '否'
                    self.search_msg = '上班打卡成功!'
                c.execute("update attendance set sign_in_time=?, checking_state=? where user_id=?",
                          (punch_time, stats, user_id))
                conn.commit()
            else:
                c.execute("select sign_in_time from attendance where user_id=?", (user_id,))
                start = time.mktime(time.strptime(c.fetchone()[0], "%Y-%m-%d %H:%M:%S"))
                during_time = round((times - start) / 60 / 60, 2)
                c.execute(
                    "update attendance set sign_out_time=?, working_time=? where user_id=?",
                    (punch_time, during_time, user_id))
                conn.commit()
                print('下班打卡')
                self.search_msg = '下班打卡成功,今日上班时长为{}小时'.format(during_time)

            self.on = False

        elif response['error_msg'] == 'match user is not found':
            self.search = False
            self.search_msg = '请您先进行注册!'
            print('请您先进行注册!')
            self.on = False
        else:
            self.search = False
            self.search_msg = response['error_msg']
            self.on = False
        self.c.close()

    """
	    使用OpenCV实现人脸追踪
	"""

    def face_tracking(self):
        command = self.command
        user = None
        cap = None
        bitmap = self.bmpSign if command == 'search' else self.bmpRegister
        background = self.imageBackgroud if command == 'search' else self.imageBackgroud1
        try:
            self.connect_sql()
            self.create_table()
            if command == 'registration':
                user = [self.txtRegisterNum.GetValue().strip(), self.txtName.GetValue().strip()]
                if not all(user):
                    wx.CallAfter(wx.MessageBox, 'Enter an employee ID and name.', 'Registration')
                    return
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                wx.CallAfter(wx.MessageBox, 'Could not open the camera.', 'PunchCard')
                return
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 450)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 450)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
            next_request = time.monotonic() + 3
            while self.on:
                ok, frame = cap.read()
                if not ok:
                    wx.CallAfter(wx.MessageBox, 'Could not read the camera.', 'PunchCard')
                    return
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray)
                if len(faces) and time.monotonic() >= next_request:
                    x, y, width, height = max(faces, key=lambda face: face[2] * face[3])
                    crop = frame[y:y + height, x:x + width]
                    encoded, buffer = cv2.imencode('.jpg', crop)
                    if encoded:
                        image_bytes = buffer.tobytes()
                        if self.recognize:
                            self.picture_quality(image_bytes)
                            if self.recognize:
                                next_request = time.monotonic() + 1
                        if not self.recognize:
                            if command == 'search':
                                self.face_search(image_bytes)
                            else:
                                self.face_registration(image_bytes, user)
                for x, y, width, height in faces:
                    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width = rgb.shape[:2]
                wx.CallAfter(self.show_preview, bitmap, width, height, rgb.tobytes())
            message = self.search_msg if command == 'search' else self.reg_msg
            if message:
                wx.CallAfter(wx.MessageBox, message, 'PunchCard')
        except (requests.RequestException, KeyError, ValueError):
            wx.CallAfter(wx.MessageBox, 'Check the face service configuration and connection.', 'PunchCard')
        finally:
            if cap is not None:
                cap.release()
            if self.conn is not None:
                self.conn.close()
            wx.CallAfter(self.finish_preview, bitmap, background)

    @staticmethod
    def show_preview(bitmap, width, height, rgb):
        bitmap.SetBitmap(wx.Bitmap.FromBuffer(width, height, rgb))

    def finish_preview(self, bitmap, background):
        self.init_data()
        bitmap.SetBitmap(wx.Bitmap(background))
        self.btnSign.Show()
        self.btnSign.Enable()
        self.btnRegister.Enable()
        self.btnDelete.Enable()
        self.btnSearch.Enable()


if __name__ == '__main__':
    app = wx.App()
    frame = MySignFrame(parent=None)
    frame.Show()
    app.MainLoop()
