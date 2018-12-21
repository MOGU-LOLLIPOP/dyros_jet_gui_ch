# !/usr/bin/env python
# -*-coding:utf-8-*-


 #matching = [s for s in dir(PyQt5.QtWidgets.QRadioButton) if "abled" in s] -> 해당 기능 있는지 살펴보는 구문
import os
import sys


import rospy
import rospkg


from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *
from PyQt5 import uic 

import dyros_jet_msgs.msg


joint_ctrl_ui = uic.loadUiType("joint_control_try.ui")[0]




class Joint_Ctrl(QMainWindow, joint_ctrl_ui):
    def __init__(self):
        super(Joint_Ctrl,self).__init__()
        self.setupUi(self)

        self.joint_ctrl_publisher = rospy.Publisher("/dyros_jet/joint_command",dyros_jet_msgs.msg.JointCommand, queue_size=5)
        rospy.init_node('ch_joint_ctrl', anonymous=True)
        self.joint_cmd_msg_ = dyros_jet_msgs.msg.JointCommand()
        #이게 키포인트! self.joint_cmd_msg_의 리스트 길이를 정의해준다!!!
        for i in range(32):
            self.joint_cmd_msg_.name.append("")
            self.joint_cmd_msg_.position.append(0)
            self.joint_cmd_msg_.duration.append(0)
        print(len(self.joint_cmd_msg_.position))

        self.joint_state_subscriber = rospy.Subscriber("/dyros_jet/joint_state",dyros_jet_msgs.msg.JointState, self.jointStateCallback)

        self.arranged_jointName = ["HeadYaw", "HeadPitch"
                   , "WaistPitch", "WaistYaw"
                   , "R_ShoulderPitch", "R_ShoulderRoll", "R_ShoulderYaw", "R_ElbowRoll", "R_WristYaw", "R_WristRoll", "R_HandYaw", "R_Gripper"
                   , "L_ShoulderPitch", "L_ShoulderRoll", "L_ShoulderYaw", "L_ElbowRoll", "L_WristYaw", "L_WristRoll", "L_HandYaw", "L_Gripper"
                   , "R_HipYaw", "R_HipRoll", "R_HipPitch", "R_KneePitch", "R_AnklePitch", "R_AnkleRoll"
                   , "L_HipYaw", "L_HipRoll", "L_HipPitch", "L_KneePitch", "L_AnklePitch", "L_AnkleRoll"]


        #버튼 그룹으로 묶어서 1, 2, 3번 그룹에 해당하는 함수로 연결 - for문 사용
        for a in self.buttonGroup.buttons():
            a.clicked.connect(self.head_waist_radio_clicked_1)
        for a in self.buttonGroup_2.buttons():
            a.clicked.connect(self.head_waist_radio_clicked_2)
        for a in self.buttonGroup_3.buttons():
            a.clicked.connect(self.head_waist_radio_clicked_3)

        self.button_joint_ctrl_minus_1.clicked.connect(self.jointCtrlMinusClicked)
        self.button_joint_ctrl_minus_2.clicked.connect(self.jointCtrlMinusClicked)
        self.button_joint_ctrl_minus_3.clicked.connect(self.jointCtrlMinusClicked)

        self.button_joint_ctrl_plus_1.clicked.connect(self.jointCtrlPlusClicked)
        self.button_joint_ctrl_plus_2.clicked.connect(self.jointCtrlPlusClicked)
        self.button_joint_ctrl_plus_3.clicked.connect(self.jointCtrlPlusClicked)

        self.button_joint_ctrl_set_1.clicked.connect(self.jointCtrlSetClicked)
        self.button_joint_ctrl_set_2.clicked.connect(self.jointCtrlSetClicked)
        self.button_joint_ctrl_set_3.clicked.connect(self.jointCtrlSetClicked)


        self.msg = ["","",""]
        self.sending_msg=[""]
        self.joint_msg_=[]


    #첫번째 열 선택 시 실행 함수
    def head_waist_radio_clicked_1(self):
        #신호를 받으면, 메세지 구성하기
        if self.sender():
            self.msg[0] = str(self.sender().text())

        self.enabling_only_avaiable()
        self.create_msg()

    
    #두번째 열 선택 시 실행 함수
    def head_waist_radio_clicked_2(self):
        self.msg[2] = ""
        #신호를 받으면, 메세지 구성하기
        if self.sender():
            self.msg[1] = str(self.sender().text())
        #여기서도 중간단계가 선택되면 머리와 허리 체크 해제
        self.buttonGroup.setExclusive(False)
        self.radioButton_1.setChecked(False)
        self.radioButton_2.setChecked(False)
        self.buttonGroup.setExclusive(True)

        self.group_3_Init()
        self.enabling_only_avaiable()
        self.create_msg()


    #세번째 열 선택 시 실행 함수
    def head_waist_radio_clicked_3(self):
        #신호를 받으면, 메세지 구성하기
        if self.sender():
            self.msg[2] = str(self.sender().text())
        self.create_msg()



    #각각 조인트마다 가능한 기능만 선택할 수 있게 도와주는 함수 - 불가능 기능 메세지 형성 방지
    def enabling_only_avaiable(self):
        if self.sender().text() == "Shoulder":
            self.radioButton_17.setDisabled(False)
            self.radioButton_18.setDisabled(False)
            self.radioButton_19.setDisabled(False)

        if self.sender().text() == "Wrist":
            self.radioButton_18.setDisabled(False)
            self.radioButton_19.setDisabled(False)

        if self.sender().text() == "Hand":
            self.radioButton_18.setDisabled(False)

        if self.sender().text() == "Elbow":
            self.radioButton_19.setDisabled(False)

        if self.sender().text() == "Hip":
            self.radioButton_20.setDisabled(False)
            self.radioButton_21.setDisabled(False)
            self.radioButton_22.setDisabled(False)
        
        if self.sender().text() == "Knee":
            self.radioButton_20.setDisabled(False)

        if self.sender().text() == "Ankle":
            self.radioButton_20.setDisabled(False)
            self.radioButton_22.setDisabled(False)

        if self.sender().text() == "Head" or self.sender().text() == "Waist": #머리와 허리는 중간단계가 필요 없으므로, 해당 버튼 클릭시 중간 버튼들 클릭된것 초기화
            self.msg[1]=""
            self.buttonGroup_2.setExclusive(False) #2번째 버튼 그룹 중복체크 활성화
            for a in self.buttonGroup_2.buttons():
                a.setChecked(False)
            self.buttonGroup_2.setExclusive(True) #2번째 버튼 그룹 중복체크 비활성화
            self.group_3_Init()
            self.radioButton_15.setDisabled(False)
            self.radioButton_16.setDisabled(False)
        

    #세번쨰 Roll, Pitch, Yaw 박스들을 초기화 시킴 - 기능 중복 방지
    def group_3_Init(self):
        self.buttonGroup_3.setExclusive(False)
        for a in self.buttonGroup_3.buttons():
            a.setDisabled(True)
            a.setChecked(False)
        self.buttonGroup_3.setExclusive(True)


    #모든 메세지 합치기
    def create_msg(self):
        self.sending_msg = self.msg[0]+self.msg[1]+self.msg[2]
        self.statusBar.showMessage(self.sending_msg+" is selected")



    #입력받은 라디오 버튼의 idex찾아내기
    def finding_id(self):
        try: 
            self.id = self.arranged_jointName.index(self.sending_msg)
            print(self.id)
        except :
            QMessageBox.about(self,"warning","function is not available")
            pass

    #TODO 각 버튼마다 어떤값을 보낼지 그거 결정하기
    #각 버튼 눌렀을때 반응하는 코드
    def jointCtrlMinusClicked(self):
        self.finding_id()
        self.send_joint_ctrl(-1)
        print(self.sending_msg, " is sending -")

    def jointCtrlPlusClicked(self):
        self.finding_id()
        self.send_joint_ctrl(1)
        print(self.sending_msg, " is sending +")

    def jointCtrlSetClicked(self):
        self.finding_id()
        if self.sender().objectName() == "button_joint_ctrl_set_1":
            deg = self.doubleSpin_joint_ctrl_1.value()
        if self.sender().objectName() == "button_joint_ctrl_set_2":
            deg = self.doubleSpin_joint_ctrl_2.value()
        if self.sender().objectName() == "button_joint_ctrl_set_3":
            deg = self.doubleSpin_joint_ctrl_3.value()
        self.send_joint_ctrl(deg)
        print(self.sending_msg, " is sending ", deg)


    #TODO 이거 지금 msg형태가 확인이 안되고 있는데, 이거 확인해서 알맞은 데이터 형태로 바꾸기
    def jointStateCallback(self,data):
        self.joint_msg_= data
	    #TODO self.jointStateUpdated()


    #보내는 메세지 형태 짜기
    def send_joint_ctrl(self,angle):
        rad = angle / 57.295791433
        offset = 0.5
        current_position = self.joint_msg_.angle[self.id]

        self.joint_cmd_msg_.position[self.id]=current_position + rad
        if angle > 0:
            self.joint_cmd_msg_.duration[self.id] = 0.5 + rad*offset
        else : 
            self.joint_cmd_msg_.duration[self.id] = 0.5 - rad*offset
        self.joint_cmd_msg_.name[self.id] = self.sending_msg
        self.joint_ctrl_publisher.publish(self.joint_cmd_msg_)
        self.joint_cmd_msg_.name[self.id]=""
    """
    def shutdown_plugin(self):
        # TODO unregister all publishers here
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog

    """

app = QApplication(sys.argv)
Window = Joint_Ctrl()
Window.show()
app.exec_()
