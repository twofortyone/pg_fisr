import cominterface
com = cominterface.Opendss('D:\Bus_37\ieee37.dss')
#print(com.get_path(), com.get_version())

com.solve()
com.send_command('show powers')

voltages = com.get_voltages()

print(voltages)
