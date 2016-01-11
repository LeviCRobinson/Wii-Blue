import wiiuse


class ButtonHandler:

    def __init__(self, wiimotes, first_wm, num_motes):
        self.wiimotes = wiimotes
        self.first_wm = first_wm
        self.num_motes = num_motes

    def press_event(self):
        remote = self.first_wm[0]
        for btn_name, btn in wiiuse.button.items():
            if wiiuse.is_just_pressed(remote, btn):
                return btn

    def release_event(self):
        remote = self.first_wm[0]

        for btn_name, btn in wiiuse.button.items():
            if wiiuse.is_released(remote, btn):
                return btn_name

    def motion_event(self):
        remote = self.first_wm[0]

        if wiiuse.using_acc(remote):
            print self.press_event()
            return (remote.orient.roll, remote.orient.pitch, remote.orient.yaw)
