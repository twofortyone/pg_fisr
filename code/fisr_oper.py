
        #Condicion de stop para operación
        #if (nodes == 0) and self.get_voltage_limits() == 0:
        #    is_terminal = True
        #    self.system.sys_start()
        #    self.system.system_data.open_dss.open_init()

    def agent_start()
        current_q = self.q[state, self.failure_actions]  # array with all q values for a given state
        action = self.argmax(current_q)

        self.prev_state = state
        self.prev_action = self.failure_actions[action]
        return self.failure_actions[action]