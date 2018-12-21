import os
import rospy
import rospkg
import sys

import geometry_msgs.msg
import dyros_jet_msgs.msg
from std_msgs.msg import String
from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtCore import Qt, QTimer, Slot
from python_qt_binding.QtGui import QQuaternion, QVector3D
from python_qt_binding.QtWidgets import QWidget




class Task_Control_Relative(Plugin):

    def __init__(self, context):
               
        super(Task_Control_Relative, self).__init__(context)

        # Give QObjects reasonable names
        self.setObjectName('Task_Control_Relative')
        #rospy.init_node('hi_jet_task_ctrl',anonymous=False)
        self.task_cmd_publisher = rospy.Publisher('/dyros_jet/task_command', dyros_jet_msgs.msg.TaskCommand, queue_size=5)
        self.task_cmd_msg_ = dyros_jet_msgs.msg.TaskCommand()
        

        #ui파일 만들었던거 불러오기
        self._widget = QWidget() # 얘를 사용해서 모든 버튼들을 정의해 줘야 하는것이다!!!!
        ui_file = os.path.join(rospkg.RosPack().get_path('dyros_jet_gui_ch'), 'resource', 'task_control_relative.ui')
        loadUi(ui_file, self._widget)
        self._widget.setObjectName('Task_Control_Relative')

    
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
            self._widget.setWindowIcon(QtGui.QIcon(icon_file))
        # Add widget to the user interface
        context.add_widget(self._widget)
    
        #각각 버튼들과 함수들 연결
        for a in self._widget.buttonGroup.buttons():
            a.clicked.connect(self.task_radio_clicked_1)
        for a in self._widget.buttonGroup_2.buttons():
            a.clicked.connect(self.task_radio_clicked_2)
        for a in self._widget.buttonGroup_3.buttons():
            a.clicked.connect(self.task_radio_clicked_3)
        self._widget.pushButton_minus.clicked.connect(self.taskCtrlMinusClicked)
        self._widget.pushButton_plus.clicked.connect(self.taskCtrlPlusClicked)
                
    #클릭 받으면 무조건 메세지로 변화시킴
    def task_radio_clicked_1(self):
        self.msg_1 = self.sender().text()
    def task_radio_clicked_2(self):
        self.msg_2 = self.sender().text()
    def task_radio_clicked_3(self):
        self.msg_3 = self.sender().text()

    #마이너스가 눌렸을때
    def taskCtrlMinusClicked(self):
        msg_total = self.msg_1 + self.msg_2 + self.msg_3
        print(msg_total)
        self.spin_num = self._widget.doubleSpinBox.value()
        print(self.spin_num)
        self.calculate()

    #플러스가 눌렸을때
    def taskCtrlPlusClicked(self):
        msg_total = self.msg_1 + self.msg_2 + self.msg_3
        print(msg_total)
        self.spin_num = self._widget.doubleSpinBox.value()
        print(self.spin_num)
        self.calculate()

    #메세지 초기화 및 크기 설정
    def init_msg(self):
        for i in range(4):
            self.task_cmd_msg_.end_effector[i] = False
            self.task_cmd_msg_.mode[i] = 0
            self.task_cmd_msg_.duration[i] = 0
            self.task_cmd_msg_.pose[i].position.x = 0
            self.task_cmd_msg_.pose[i].position.y = 0
            self.task_cmd_msg_.pose[i].position.z = 0
            self.task_cmd_msg_.pose[i].orientation.x = 0
            self.task_cmd_msg_.pose[i].orientation.y = 0
            self.task_cmd_msg_.pose[i].orientation.z = 0
            self.task_cmd_msg_.pose[i].orientation.w = 0

    #메인 계산
    def calculate(self):
        self.init_msg()


        #어디쪽으로 컨트롤 할것인지 결정
        if self.msg_1 == "Left":
            if self.msg_2 == "Arm":
                arr_num = 2
            elif self.msg_2 == "Leg":
                arr_num = 0
        elif self.msg_1 == "Right":
            if self.msg_2 == "Arm":
                arr_num = 3
            elif self.msg_2 == "Leg":
                arr_num = 1
        pos = self.spin_num
        axis = QVector3D
        quat = QQuaternion
        offset = 1.0

        self.task_cmd_msg_.end_effector[arr_num] = True
        self.task_cmd_msg_.mode[arr_num] = 0
        self.task_cmd_msg_.duration[arr_num] = 1 + pos/15.0*offset

        if "X" in self.msg_3:
            self.task_cmd_msg_.pose[arr_num].position.x = pos / 100.0
        if "Y" in self.msg_3:
            self.task_cmd_msg_.pose[arr_num].position.y = pos / 100.0
        if "Z" in self.msg_3:
            self.task_cmd_msg_.pose[arr_num].position.z = pos / 100.0

        if "Roll" in self.msg_3:
            axis = QVector3D(1,0,0)
            self.task_cmd_msg_.pose[arr_num].orientation.x = quat.fromAxisAndAngle(axis,pos).x()
            self.task_cmd_msg_.pose[arr_num].orientation.y = quat.fromAxisAndAngle(axis,pos).y()
            self.task_cmd_msg_.pose[arr_num].orientation.z = quat.fromAxisAndAngle(axis,pos).z()
            self.task_cmd_msg_.pose[arr_num].orientation.w = quat.fromAxisAndAngle(axis,pos).scalar()
        
        if "Pitch" in self.msg_3:
            axis = QVector3D(0,1,0)
            self.task_cmd_msg_.pose[arr_num].orientation.x = quat.fromAxisAndAngle(axis,pos).x()
            self.task_cmd_msg_.pose[arr_num].orientation.y = quat.fromAxisAndAngle(axis,pos).y()
            self.task_cmd_msg_.pose[arr_num].orientation.z = quat.fromAxisAndAngle(axis,pos).z()
            self.task_cmd_msg_.pose[arr_num].orientation.w = quat.fromAxisAndAngle(axis,pos).scalar()
           
        if "Yaw" in self.msg_3:
            axis = QVector3D(0,0,1)
            self.task_cmd_msg_.pose[arr_num].orientation.x = quat.fromAxisAndAngle(axis,pos).x()
            self.task_cmd_msg_.pose[arr_num].orientation.y = quat.fromAxisAndAngle(axis,pos).y()
            self.task_cmd_msg_.pose[arr_num].orientation.z = quat.fromAxisAndAngle(axis,pos).z()
            self.task_cmd_msg_.pose[arr_num].orientation.w = quat.fromAxisAndAngle(axis,pos).scalar()
            
        self.send_task_ctrl()


    #해당 메세지 퍼블리시
    def send_task_ctrl(self):
        print(self.task_cmd_msg_)
        self.task_cmd_publisher.publish(self.task_cmd_msg_)

    
    
    def shutdown_plugin(self):
        # TODO unregister all publishers here
        self._unregister_publisher()
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        #TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass
    
    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog

