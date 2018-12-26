import os
import rospy
import rospkg
import sys


import geometry_msgs.msg
import dyros_jet_msgs.msg
import smach_msgs.msg as sm_msg
from std_msgs.msg import String, Int32
from qt_gui.plugin import Plugin
from python_qt_binding import loadUi, QtGui
from python_qt_binding.QtCore import Qt, QTimer, Slot
from python_qt_binding.QtWidgets import QWidget



class State_Setting(Plugin):

    def __init__(self, context):
               
        super(State_Setting, self).__init__(context)

        # Give QObjects reasonable names
        self.setObjectName('State_Setting_Gui')
        #rospy.init_node('hi_jet_task_ctrl',anonymous=False)
        self.smach_publisher = rospy.Publisher('/dyros_jet/smach/transition', String, queue_size=5)
        self.state_msg = ""
        self.shutdown_publisher = rospy.Publisher('/dyros_jet/shutdown_command',String, queue_size=1)
        self.hello_cnt_publisher = rospy.Publisher('/hello_cnt',Int32, queue_size=5)
        self.smach_subscriber = rospy.Subscriber("/dyros_jet/smach/container_status",sm_msg.SmachContainerStatus, self.stateCallback)
        

        #ui파일 만들었던거 불러오기
        self._widget = QWidget() # 얘를 사용해서 모든 버튼들을 정의해 줘야 하는것이다!!!!
        ui_file = os.path.join(rospkg.RosPack().get_path('dyros_jet_gui_ch'), 'resource', 'state_setting.ui')
        loadUi(ui_file, self._widget)
        self._widget.setObjectName('State_Setting')

    
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
            #self._widget.setWindowIcon(QtGui.QIcon(icon_file))
        # Add widget to the user interface
        context.add_widget(self._widget)
    
        #각각 버튼들과 함수들 연결
        for a in self._widget.buttonGroup.buttons():
            a.clicked.connect(self.stateButtonClicked)
        for a in self._widget.buttonGroup_2.buttons():
            a.clicked.connect(self.stateButtonClicked)
        self._widget.act_button.clicked.connect(self.activate)

        self.stage = 0


        self.state_name = [['mission','door','reach','open','push'],
            ['mission','valve','approach','close'],
            ['mission','egress','init','Do Egress','Standby','Hello :)','Guide >'],
            ['mission','Stair'],
            ['event','Handclap','Ready','Do','End'],
            ['event','Handshake','Turn','Ready','Do','End','Mot1','Mot2','Mot3','Return'],
            ['event','Hello','Ready','Do','End','Introduce','Intro End']]
                
    def stateButtonClicked(self):
        self.stage = 0
        self.finding()

    def finding(self):
        for i in range(7):
            if self._widget.sender().objectName() == self.state_name[i][1]:
                self.index = i
                self.combo()

    def combo(self):
        self._widget.comboBox.clear()
        self._widget.comboBox.addItem(self.state_name[self.index][self.stage])
    
    def activate(self):
        self.state = self._widget.comboBox.currentText()
        self.send_transition()
        self.stage = self.stage + 1
        self.combo()
        
    #해당 메세지 퍼블리시
    def send_transition(self):
        print(self.state)
        self.smach_publisher.publish(self.state)

    def stateCallback(self,data):
        current_state = data.active_states[0]
        self._widget.line_current_state.setText(current_state)















    
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

