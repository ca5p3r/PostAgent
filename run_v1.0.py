# APP FLAGS
importFlag = True
envVariables = True
appWindow = True
appSetting = True
widgFlag = True

# IMPORTS
try:
    from PyQt5 import QtWidgets, uic
    from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem, QShortcut
    from PyQt5.QtGui import *
    from PyQt5.QtGui import QKeySequence
    import psycopg2
    import json
    import sys
    import os
    import time
except ImportError as error:
    print('Error while importing modules: ', error)
    importFlag = False

# SETTINGS ENVIRONMENT VARIABLES
if importFlag:
    try:
        ui_path = os.path.dirname(
            os.path.abspath(__file__)) + os.path.sep + 'ui'
        icon_path = os.path.dirname(
            os.path.abspath(__file__)) + os.path.sep + 'icons'
        temp_path = os.path.dirname(
            os.path.abspath(__file__)) + os.path.sep + 'data'
    except Exception as error:
        print('Error while setting environment variables: ', error)
        envVariables = False

# SETTING GLOBAL VARIABLES
connection = False
modServerInfo = []
modServerIndex = 0
modServerListIndex = 0

# GUI SETTINGS
if importFlag and envVariables:
    try:
        app = QtWidgets.QApplication([])
        app.setApplicationDisplayName('PostAgent')
        app.setApplicationName('PostAgent')
        win = uic.loadUi(os.path.join(ui_path, "main.ui"))
        win.setWindowIcon(QIcon(os.path.join(icon_path, 'icon.ico')))
        win.addServer.setIcon(QIcon(os.path.join(icon_path, 'add.ico')))
        win.editServer.setIcon(QIcon(os.path.join(icon_path, 'edit.ico')))
        win.removeServer.setIcon(QIcon(os.path.join(icon_path, 'remove.ico')))
        win.cancelServer.setIcon(QIcon(os.path.join(icon_path, 'cancel.ico')))
        win.setFixedSize(1558, 907)
    except Exception as error:
        print('Error while initiating application window: ', error)
        appWindow = False

# READING JSON DATA
if importFlag and envVariables:
    try:
        with open(os.path.join(temp_path, 'data.json'), 'r', encoding='utf8') as json_file:
            contents = json.load(json_file)

        with open(os.path.join(temp_path, 'credentials.json'), 'r+') as cred:
            data = json.load(cred)
    except Exception as error:
        print('Error while reading application settings: ', error)
        appSetting = False

# SETTING MESSAGE BOX
if importFlag and appWindow and envVariables:
    try:
        msgBox = QMessageBox()
        msgBox.setWindowTitle('Warning')
        msgBox.setWindowIcon(QIcon(os.path.join(icon_path, 'warning.ico')))
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        executeShortcut = QShortcut(QKeySequence("F5"), win.executeButton)
    except Exception as error:
        print('Error while loading widget components: ', error)
        widgFlag = False

# LOAD SERVER LIST
if appSetting:
    for i in data['names']:
        win.serverList.addItem(i)

# HELPER FUNCTIONS


def connector():
    global connection
    try:
        connection = psycopg2.connect(host=win.hostField.text(),
                                      port=win.portField.text(),
                                      user=win.userField.text(),
                                      password=win.passField.text(),
                                      dbname=win.dbConnect.text(),
                                      connect_timeout=10)
    except Exception as error:
        error = error
        return connection, error
    else:
        error = ''
        return connection, error


def get_unique(alist):
    unique_list = []
    for item in alist:
        if item in unique_list:
            pass
        else:
            unique_list.append(item)
    return unique_list


def delete_server():
    msgBox.setText(contents['messages']['deleteWarning'])
    returnValue = msgBox.exec()
    if returnValue == QMessageBox.Yes:
        if not win.serverName.text():
            win.textBrowser.setText('\n'+contents['messages']['servNameReq'])
        else:
            data['names'].remove(win.serverName.text())
            data['servers'].remove(win.hostField.text())
            data['ports'].remove(win.portField.text())
            data['users'].remove(win.userField.text())
            data['passwords'].remove(win.passField.text())
            win.serverList.removeItem(win.serverList.currentIndex())
            with open(os.path.join(temp_path, 'credentials.json'), 'r+') as cred:
                cred.seek(0)
                json.dump(data, cred, indent=4)
                cred.truncate()
            win.serverList.setCurrentIndex(0)
    else:
        win.serverList.setCurrentIndex(0)


def edit_server():
    msgBox.setText(contents['messages']['editWarning'])
    returnValue = msgBox.exec()
    if returnValue == QMessageBox.Yes:
        if not win.serverName.text():
            win.textBrowser.setText('\n'+contents['messages']['servNameReq'])
        else:
            win.serverName.setEnabled(True)
            win.hostField.setEnabled(True)
            win.portField.setEnabled(True)
            win.userField.setEnabled(True)
            win.passField.setEnabled(True)
            win.editServer.setEnabled(False)
            win.addServer.setEnabled(False)
            win.removeServer.setEnabled(False)
            win.cancelServer.setEnabled(True)
            win.serverList.setEnabled(False)
            win.textBrowser.setText("")
            global modServerIndex, modServerListIndex
            modServerIndex = data["names"].index(win.serverName.text())
            modServerListIndex = win.serverList.currentIndex()
    else:
        win.serverList.setCurrentIndex(0)
        win.editServer.setChecked(False)


def add_server():
    win.serverList.setCurrentIndex(0)
    win.cancelServer.setEnabled(True)
    win.addServer.setEnabled(False)
    win.removeServer.setEnabled(False)
    win.serverList.setEnabled(False)
    win.serverName.setEnabled(True)
    win.hostField.setEnabled(True)
    win.portField.setEnabled(True)
    win.userField.setEnabled(True)
    win.passField.setEnabled(True)
    win.serverName.setText('')
    win.hostField.setText('')
    win.portField.setText('')
    win.userField.setText('')
    win.passField.setText('')


def cancel_server():
    win.serverList.setCurrentIndex(0)
    win.cancelServer.setEnabled(False)
    win.addServer.setEnabled(True)
    win.editServer.setEnabled(True)
    win.editServer.setChecked(False)
    win.removeServer.setEnabled(True)
    win.serverList.setEnabled(True)
    win.serverName.setEnabled(False)
    win.hostField.setEnabled(False)
    win.portField.setEnabled(False)
    win.userField.setEnabled(False)
    win.passField.setEnabled(False)
    win.serverTree.setEnabled(False)
    win.mainServerTree.setEnabled(False)
    win.serverTree.clear()
    win.mainServerTree.clear()

# LOAD SERVER INFO


def get_server_info():
    queryUser = contents['user']['userView']
    queryDB = contents['database']['dbView']
    connection, error = connector()
    if not connection:
        user_list = []
        database_list = []
        return user_list, database_list, error
    else:
        error = None
        connection.autocommit = True
        cursorUser = connection.cursor()
        cursorUser.execute(queryUser)
        cursorDB = connection.cursor()
        cursorDB.execute(queryDB)
        try:
            resultUser = cursorUser.fetchall()
            user_list = []
            resultDB = cursorDB.fetchall()
            database_list = []
            for i in range(0, len(resultDB)):
                database_list.append(resultDB[i][0])
            for i in range(0, len(resultUser)):
                user_list.append(resultUser[i][0])
        except psycopg2.ProgrammingError:
            win.textBrowser.setText('\n' + contents['messages']['success'])
        connection.close()
        cursorDB.close()
        cursorUser.close()
    return user_list, database_list, error

# LOAD SCHEMA INFO


def get_schema_info():
    querySchema = contents['special']['schema']
    queryEX = contents['extension']['exView']
    try:
        connection, error = connector()
        if (connection):
            connection.autocommit = True
            cursorSchema = connection.cursor()
            cursorSchema.execute(querySchema)
            cursorEX = connection.cursor()
            cursorEX.execute(queryEX)
            try:
                resultSchema = cursorSchema.fetchall()
                resultEX = cursorEX.fetchall()
                schema_list = []
                extension_list = []
                for i in range(0, len(resultEX)):
                    extension_list.append(resultEX[i][0])
                for i in range(0, len(resultSchema)):
                    schema_list.append(resultSchema[i][0])
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText('\n' + contents['messages']['success'])
            connection.close()
            cursorEX.close()
            cursorSchema.close()
    except Exception as Error:
        win.textBrowser.setText('\n' + str(Error))
    return schema_list, extension_list


def get_table_info(schemaName):
    queryTable = contents['special']['table'].format(schemaName)
    try:
        connection, error = connector()
        if (connection):
            connection.autocommit = True
            cursorTable = connection.cursor()
            cursorTable.execute(queryTable)
            try:
                resultTable = cursorTable.fetchall()
                table_list = []
                for i in range(0, len(resultTable)):
                    table_list.append(resultTable[i][0])
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText('\n' + contents['messages']['success'])
            connection.close()
            cursorTable.close()
    except Exception as Error:
        win.textBrowser.setText('\n' + str(Error))
    return table_list


def get_sequence_info(schemaName):
    sequenceInfo = contents['sequences']['seqView'].format(schemaName)
    try:
        connection, error = connector()
        if (connection):
            connection.autocommit = True
            cursorSeq = connection.cursor()
            cursorSeq.execute(sequenceInfo)
            try:
                resultSeq = cursorSeq.fetchall()
                sequence_list = []
                for i in range(0, len(resultSeq)):
                    sequence_list.append(resultSeq[i][0])
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText('\n' + contents['messages']['success'])
            connection.close()
            cursorSeq.close()
    except Exception as Error:
        win.textBrowser.setText('\n' + str(Error))
    return sequence_list


def get_column_info(schemaName, tableName):
    queryColumn = contents['special']['column'].format(schemaName, tableName)
    try:
        connection, error = connector()
        if (connection):
            connection.autocommit = True
            cursorColumn = connection.cursor()
            cursorColumn.execute(queryColumn)
            try:
                resultColumn = cursorColumn.fetchall()
                column_list = []
                for i in range(0, len(resultColumn)):
                    column_list.append(resultColumn[i][0])
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText('\n' + contents['messages']['success'])
            connection.close()
            cursorColumn.close()
    except Exception as Error:
        win.textBrowser.setText('\n' + str(Error))
    return column_list

# DIALOGS FUNCTIONS


def connectDialog():
    msgBox.setText(contents['messages']['connectWarning'])
    returnValue = msgBox.exec()
    if returnValue == QMessageBox.Yes:
        serverConnect()
    else:
        pass


def disconnectDialog():
    msgBox.setText(contents['messages']['disconnectWarning'])
    returnValue = msgBox.exec()
    if returnValue == QMessageBox.Yes:
        serverDisconnect()
    else:
        pass

# HELP MENU FUNCTIONS


def getAbout():
    win.textBrowser.setText('')
    win.textBrowser.setText(contents['extras']['about'])


def getAuthor():
    win.textBrowser.setText('')
    win.textBrowser.setText(contents['extras']['author'])


def getCredits():
    win.textBrowser.setText('')
    win.textBrowser.setText(contents['extras']['credits'])

# NAVIGATION TRIGGERS FUNCTIONS


def navToDB():
    win.tabsWidget.setCurrentIndex(0)


def navToUS():
    win.tabsWidget.setCurrentIndex(1)


def navToSC():
    win.tabsWidget.setCurrentIndex(2)


def navToSE():
    win.tabsWidget.setCurrentIndex(3)


def navToTA():
    win.tabsWidget.setCurrentIndex(4)


def navToAT():
    win.tabsWidget.setCurrentIndex(5)


def navToIE():
    win.tabsWidget.setCurrentIndex(6)


def navToBR():
    win.tabsWidget.setCurrentIndex(7)

# MAIN TOOLS FUNCTIONS


def querier():
    start_time = time.time()
    query = win.queryEditor.toPlainText()
    try:
        connection, error = connector()
        if (connection):
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(query)
            try:
                result = cursor.fetchall()
                end_time = time.time()
                runtime = end_time - start_time
                win.textBrowser.setText('')
                win.textBrowser.setText(
                    'Runtime: {0} seconds\n'.format(str(round(runtime, 4))) + str(result))
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText('\n' + contents['messages']['success'])
            connection.close()
            cursor.close()
    except Exception as Error:
        win.textBrowser.setText('\n' + str(Error))


def clearHistory():
    win.textBrowser.setText('')


def clearFields():
    if win.connectButton.isEnabled():
        win.serverList.setCurrentIndex(0)
    win.queryEditor.setText('')
    win.dbName.setText('')
    win.dbOwner.setText('')
    win.dbNewName.setText('')
    win.dbNewOwner.setText('')
    win.exName.setText('')
    win.userName.setText('')
    win.userPass.setText('')
    win.userDB.setText('')
    win.schemaName.setText('')
    win.schemaOwner.setText('')
    win.newSchema.setText('')
    win.schemaNewOwner.setText('')
    win.cbLogin.setChecked(False)
    win.cbSuper.setChecked(False)
    win.cbRole.setChecked(False)
    win.cbDB.setChecked(False)
    win.cbInherit.setChecked(False)
    win.cbReplication.setChecked(False)
    win.schemaDropCasc.setChecked(False)
    win.grantUsage.setChecked(False)
    win.grantCreate.setChecked(False)
    win.serverTree.clear()
    win.mainServerTree.clear()


def refresh():
    if win.connectButton.isEnabled():
        pass
    else:
        clearFields()
        serverConnect()
        set_initial_view()

# COMBOBOX TRIGGERS FUNCTIONS


def serverComboChanged():
    win.databaseList.setEnabled(False)
    win.databaseList.clear()
    win.databaseList.addItem('Select database')
    win.checkConnection.setEnabled(True)
    win.connectButton.setEnabled(False)
    choice = win.serverList.currentText()
    if choice == 'Select server':
        win.serverName.setText('')
        win.hostField.setText('')
        win.portField.setText('')
        win.userField.setText('')
        win.passField.setText('')
        win.dbConnect.setText('')
    else:
        itemIndex = data['names'].index(choice)
        win.serverName.setText(data['names'][itemIndex])
        win.hostField.setText(data['servers'][itemIndex])
        win.portField.setText(data['ports'][itemIndex])
        win.userField.setText(data['users'][itemIndex])
        win.passField.setText(data['passwords'][itemIndex])


def dbListComboChanged():
    if win.databaseList.currentText() == 'Select database':
        win.dbConnect.setText('')
    else:
        win.dbConnect.setText(win.databaseList.currentText())


def dbComboChanged():
    if win.dbOptions.currentText() == "Select opertation":
        win.dbName.setEnabled(False)
        win.dbOwner.setEnabled(False)
        win.dbNewName.setEnabled(False)
        win.dbNewOwner.setEnabled(False)
        win.exName.setEnabled(False)
        win.dbRun.setEnabled(False)
    elif win.dbOptions.currentText() == "Create database":
        win.dbName.setEnabled(True)
        win.dbOwner.setEnabled(True)
        win.dbNewName.setEnabled(False)
        win.dbNewOwner.setEnabled(False)
        win.exName.setEnabled(False)
        win.dbRun.setEnabled(True)
    elif win.dbOptions.currentText() == "Alter database":
        win.dbName.setEnabled(True)
        win.dbOwner.setEnabled(False)
        win.dbNewName.setEnabled(True)
        win.dbNewOwner.setEnabled(True)
        win.exName.setEnabled(False)
        win.dbRun.setEnabled(True)
    elif win.dbOptions.currentText() == "Create extension":
        win.dbName.setEnabled(False)
        win.dbOwner.setEnabled(False)
        win.dbNewName.setEnabled(False)
        win.dbNewOwner.setEnabled(False)
        win.exName.setEnabled(True)
        win.dbRun.setEnabled(True)
    elif win.dbOptions.currentText() == "Drop extension":
        msgBox.setText(contents['messages']['deleteWarning'])
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            win.dbName.setEnabled(False)
            win.dbOwner.setEnabled(False)
            win.dbNewName.setEnabled(False)
            win.dbNewOwner.setEnabled(False)
            win.exName.setEnabled(True)
            win.dbRun.setEnabled(True)
        else:
            win.dbOptions.setCurrentIndex(0)
    elif win.dbOptions.currentText() == "Drop database":
        msgBox.setText(contents['messages']['deleteWarning'])
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            win.dbName.setEnabled(True)
            win.dbOwner.setEnabled(False)
            win.dbNewName.setEnabled(False)
            win.dbNewOwner.setEnabled(False)
            win.exName.setEnabled(False)
            win.dbRun.setEnabled(True)
        else:
            win.dbOptions.setCurrentIndex(0)


def userComboChanged():
    if win.userOptions.currentText() == "Select opertation":
        win.userName.setEnabled(False)
        win.userPass.setEnabled(False)
        win.cbLogin.setEnabled(False)
        win.cbSuper.setEnabled(False)
        win.cbRole.setEnabled(False)
        win.cbDB.setEnabled(False)
        win.cbInherit.setEnabled(False)
        win.cbReplication.setEnabled(False)
        win.userExecute.setEnabled(False)
    elif win.userOptions.currentText() == "Create new user":
        win.userName.setEnabled(True)
        win.userPass.setEnabled(True)
        win.cbLogin.setEnabled(True)
        win.cbSuper.setEnabled(True)
        win.cbRole.setEnabled(True)
        win.cbDB.setEnabled(True)
        win.cbInherit.setEnabled(True)
        win.cbReplication.setEnabled(True)
        win.userExecute.setEnabled(True)
    elif win.userOptions.currentText() == "Edit user":
        win.userName.setEnabled(True)
        win.userPass.setEnabled(True)
        win.cbLogin.setEnabled(True)
        win.cbSuper.setEnabled(True)
        win.cbRole.setEnabled(True)
        win.cbDB.setEnabled(True)
        win.cbInherit.setEnabled(True)
        win.cbReplication.setEnabled(True)
        win.userExecute.setEnabled(True)
    elif win.userOptions.currentText() == "Delete user":
        msgBox.setText(contents['messages']['deleteWarning'])
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            win.userName.setEnabled(True)
            win.userPass.setEnabled(False)
            win.cbLogin.setEnabled(False)
            win.cbSuper.setEnabled(False)
            win.cbRole.setEnabled(False)
            win.cbDB.setEnabled(False)
            win.cbInherit.setEnabled(False)
            win.cbReplication.setEnabled(False)
            win.userExecute.setEnabled(True)
        else:
            win.userOptions.setCurrentIndex(0)
    elif win.userOptions.currentText() == "Grant access to database":
        win.userName.setEnabled(True)
        win.userPass.setEnabled(False)
        win.cbLogin.setEnabled(False)
        win.cbSuper.setEnabled(False)
        win.cbRole.setEnabled(False)
        win.cbDB.setEnabled(False)
        win.cbInherit.setEnabled(False)
        win.cbReplication.setEnabled(False)
        win.userExecute.setEnabled(True)
    elif win.userOptions.currentText() == "Revoke permissions":
        win.userName.setEnabled(True)
        win.userPass.setEnabled(False)
        win.cbLogin.setEnabled(False)
        win.cbSuper.setEnabled(False)
        win.cbRole.setEnabled(False)
        win.cbDB.setEnabled(False)
        win.cbInherit.setEnabled(False)
        win.cbReplication.setEnabled(False)
        win.userExecute.setEnabled(True)


def schemaComboChanged():
    if win.schemaOptions.currentText() == "Select opertation":
        win.schemaName.setEnabled(False)
        win.schemaOwner.setEnabled(False)
        win.newSchema.setEnabled(False)
        win.schemaNewOwner.setEnabled(False)
        win.schemaDropCasc.setEnabled(False)
        win.grantUsage.setEnabled(False)
        win.grantCreate.setEnabled(False)
        win.schemaRun.setEnabled(False)
    elif win.schemaOptions.currentText() == "Create schema":
        win.schemaName.setEnabled(True)
        win.schemaOwner.setEnabled(True)
        win.newSchema.setEnabled(False)
        win.schemaNewOwner.setEnabled(False)
        win.schemaDropCasc.setEnabled(False)
        win.grantUsage.setEnabled(False)
        win.grantCreate.setEnabled(False)
        win.schemaRun.setEnabled(True)
    elif win.schemaOptions.currentText() == "Alter schema":
        win.schemaName.setEnabled(True)
        win.schemaOwner.setEnabled(False)
        win.newSchema.setEnabled(True)
        win.schemaNewOwner.setEnabled(True)
        win.schemaDropCasc.setEnabled(False)
        win.grantUsage.setEnabled(False)
        win.grantCreate.setEnabled(False)
        win.schemaRun.setEnabled(True)
    elif win.schemaOptions.currentText() == "Grant access to user":
        win.schemaName.setEnabled(True)
        win.schemaOwner.setEnabled(True)
        win.newSchema.setEnabled(False)
        win.schemaNewOwner.setEnabled(False)
        win.schemaDropCasc.setEnabled(False)
        win.grantUsage.setEnabled(True)
        win.grantCreate.setEnabled(True)
        win.schemaRun.setEnabled(True)
    elif win.schemaOptions.currentText() == "Delete schema":
        msgBox.setText(contents['messages']['deleteWarning'])
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            win.schemaName.setEnabled(True)
            win.schemaOwner.setEnabled(False)
            win.newSchema.setEnabled(False)
            win.schemaNewOwner.setEnabled(False)
            win.schemaDropCasc.setEnabled(True)
            win.schemaRun.setEnabled(True)
            win.grantUsage.setEnabled(False)
            win.grantCreate.setEnabled(False)
        else:
            win.schemaOptions.setCurrentIndex(0)


def sequenceComboChanged():
    if win.seqOptions.currentText() == "Select operation":
        win.seqName.setEnabled(False)
        win.seqOwner.setEnabled(False)
        win.seqOwnerColumn.setEnabled(False)
        win.seqSchema.setEnabled(False)
        win.seqIncrement.setEnabled(False)
        win.seqStart.setEnabled(False)
        win.seqMinimum.setEnabled(False)
        win.seqMaximum.setEnabled(False)
        win.revokeSeq.setEnabled(False)
        win.seqRun.setEnabled(False)
        win.loadSeq.setEnabled(False)
        win.newSeqName.setEnabled(False)
        win.newSeqSchema.setEnabled(False)
        win.newSeqOwner.setEnabled(False)
        win.newSeqOwnerColumn.setEnabled(False)
    elif win.seqOptions.currentText() == "Create sequence":
        win.seqName.setEnabled(True)
        win.seqOwner.setEnabled(True)
        win.seqOwnerColumn.setEnabled(True)
        win.seqSchema.setEnabled(True)
        win.seqIncrement.setEnabled(True)
        win.seqStart.setEnabled(True)
        win.revokeSeq.setEnabled(False)
        win.seqMinimum.setEnabled(True)
        win.seqMaximum.setEnabled(True)
        win.seqRun.setEnabled(True)
        win.loadSeq.setEnabled(False)
        win.newSeqName.setEnabled(False)
        win.newSeqSchema.setEnabled(False)
        win.newSeqOwner.setEnabled(False)
        win.newSeqOwnerColumn.setEnabled(False)
    elif win.seqOptions.currentText() == "Alter sequence":
        win.seqName.setEnabled(True)
        win.seqOwner.setEnabled(False)
        win.seqOwnerColumn.setEnabled(False)
        win.seqSchema.setEnabled(True)
        win.seqIncrement.setEnabled(False)
        win.seqStart.setEnabled(False)
        win.seqMinimum.setEnabled(False)
        win.seqMaximum.setEnabled(False)
        win.revokeSeq.setEnabled(False)
        win.seqRun.setEnabled(False)
        win.loadSeq.setEnabled(True)
        win.newSeqName.setEnabled(False)
        win.newSeqSchema.setEnabled(False)
        win.newSeqOwner.setEnabled(False)
        win.newSeqOwnerColumn.setEnabled(False)
    elif win.seqOptions.currentText() == "Drop sequence":
        msgBox.setText(contents['messages']['deleteWarning'])
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            win.seqName.setEnabled(True)
            win.seqOwner.setEnabled(False)
            win.seqOwnerColumn.setEnabled(False)
            win.seqSchema.setEnabled(True)
            win.seqIncrement.setEnabled(False)
            win.seqStart.setEnabled(False)
            win.seqMinimum.setEnabled(False)
            win.seqMaximum.setEnabled(False)
            win.revokeSeq.setEnabled(False)
            win.seqRun.setEnabled(True)
            win.loadSeq.setEnabled(False)
            win.newSeqName.setEnabled(False)
            win.newSeqSchema.setEnabled(False)
            win.newSeqOwner.setEnabled(False)
            win.newSeqOwnerColumn.setEnabled(False)
        else:
            win.seqOptions.setCurrentIndex(0)


def tableComboChanged():
    if win.tableOptions.currentText() == "Select opertation":
        win.tableSchema.setEnabled(False)
        win.tableName.setEnabled(False)
        win.tableOwner.setEnabled(False)
        win.tableNewName.setEnabled(False)
        win.tableNewOwner.setEnabled(False)
        win.tableNewSchema.setEnabled(False)
        win.copyToTable.setEnabled(False)
        win.columnsWidget.setEnabled(False)
        win.contentsWidget.setEnabled(False)
        win.columnsNumber.setEnabled(False)
        win.confirmTabNumb.setEnabled(False)
        win.delColumn.setEnabled(False)
        win.tableDropCasc.setEnabled(False)
        win.tableClustered.setEnabled(False)
        win.tabSeq.setEnabled(False)
        win.getStructure.setEnabled(False)
        win.rowCount.setEnabled(False)
        win.getContents.setEnabled(False)
        win.addRow.setEnabled(False)
        win.tableRun.setEnabled(False)
    elif win.tableOptions.currentText() == "Create table":
        win.tableSchema.setEnabled(True)
        win.tableName.setEnabled(True)
        win.tableOwner.setEnabled(True)
        win.tableNewName.setEnabled(True)
        win.tableNewOwner.setEnabled(True)
        win.tableNewSchema.setEnabled(True)
        win.copyToTable.setEnabled(True)
        win.columnsWidget.setEnabled(True)
        win.contentsWidget.setEnabled(True)
        win.columnsNumber.setEnabled(True)
        win.confirmTabNumb.setEnabled(True)
        win.delColumn.setEnabled(True)
        win.tableDropCasc.setEnabled(True)
        win.tableClustered.setEnabled(True)
        win.tabSeq.setEnabled(True)
        win.getStructure.setEnabled(True)
        win.rowCount.setEnabled(True)
        win.getContents.setEnabled(True)
        win.addRow.setEnabled(True)
        win.tableRun.setEnabled(True)
    elif win.tableOptions.currentText() == "Alter table structure":
        win.tableSchema.setEnabled(False)
        win.tableName.setEnabled(False)
        win.tableOwner.setEnabled(False)
        win.tableNewName.setEnabled(False)
        win.tableNewOwner.setEnabled(False)
        win.tableNewSchema.setEnabled(False)
        win.copyToTable.setEnabled(False)
        win.columnsWidget.setEnabled(False)
        win.contentsWidget.setEnabled(False)
        win.columnsNumber.setEnabled(False)
        win.confirmTabNumb.setEnabled(False)
        win.delColumn.setEnabled(False)
        win.tableDropCasc.setEnabled(False)
        win.tableClustered.setEnabled(False)
        win.tabSeq.setEnabled(False)
        win.getStructure.setEnabled(False)
        win.rowCount.setEnabled(False)
        win.getContents.setEnabled(False)
        win.addRow.setEnabled(False)
        win.tableRun.setEnabled(False)
    elif win.tableOptions.currentText() == "Alter table contents":
        win.tableSchema.setEnabled(False)
        win.tableName.setEnabled(False)
        win.tableOwner.setEnabled(False)
        win.tableNewName.setEnabled(False)
        win.tableNewOwner.setEnabled(False)
        win.tableNewSchema.setEnabled(False)
        win.copyToTable.setEnabled(False)
        win.columnsWidget.setEnabled(False)
        win.contentsWidget.setEnabled(False)
        win.columnsNumber.setEnabled(False)
        win.confirmTabNumb.setEnabled(False)
        win.delColumn.setEnabled(False)
        win.tableDropCasc.setEnabled(False)
        win.tableClustered.setEnabled(False)
        win.tabSeq.setEnabled(False)
        win.getStructure.setEnabled(False)
        win.rowCount.setEnabled(False)
        win.getContents.setEnabled(False)
        win.addRow.setEnabled(False)
        win.tableRun.setEnabled(False)
    elif win.tableOptions.currentText() == "Count table rows":
        win.tableSchema.setEnabled(False)
        win.tableName.setEnabled(False)
        win.tableOwner.setEnabled(False)
        win.tableNewName.setEnabled(False)
        win.tableNewOwner.setEnabled(False)
        win.tableNewSchema.setEnabled(False)
        win.copyToTable.setEnabled(False)
        win.columnsWidget.setEnabled(False)
        win.contentsWidget.setEnabled(False)
        win.columnsNumber.setEnabled(False)
        win.confirmTabNumb.setEnabled(False)
        win.delColumn.setEnabled(False)
        win.tableDropCasc.setEnabled(False)
        win.tableClustered.setEnabled(False)
        win.tabSeq.setEnabled(False)
        win.getStructure.setEnabled(False)
        win.rowCount.setEnabled(False)
        win.getContents.setEnabled(False)
        win.addRow.setEnabled(False)
        win.tableRun.setEnabled(False)
    elif win.tableOptions.currentText() == "Truncate table":
        msgBox.setText(contents['messages']['truncateWarning'])
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            win.tableSchema.setEnabled(False)
            win.tableName.setEnabled(False)
            win.tableOwner.setEnabled(False)
            win.tableNewName.setEnabled(False)
            win.tableNewOwner.setEnabled(False)
            win.tableNewSchema.setEnabled(False)
            win.copyToTable.setEnabled(False)
            win.columnsWidget.setEnabled(False)
            win.contentsWidget.setEnabled(False)
            win.columnsNumber.setEnabled(False)
            win.confirmTabNumb.setEnabled(False)
            win.delColumn.setEnabled(False)
            win.tableDropCasc.setEnabled(False)
            win.tableClustered.setEnabled(False)
            win.tabSeq.setEnabled(False)
            win.getStructure.setEnabled(False)
            win.rowCount.setEnabled(False)
            win.getContents.setEnabled(False)
            win.addRow.setEnabled(False)
            win.tableRun.setEnabled(False)
        else:
            win.tableOptions.setCurrentIndex(0)
    elif win.tableOptions.currentText() == "Drop table":
        msgBox.setText(contents['messages']['deleteWarning'])
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            win.tableSchema.setEnabled(False)
            win.tableName.setEnabled(False)
            win.tableOwner.setEnabled(False)
            win.tableNewName.setEnabled(False)
            win.tableNewOwner.setEnabled(False)
            win.tableNewSchema.setEnabled(False)
            win.copyToTable.setEnabled(False)
            win.columnsWidget.setEnabled(False)
            win.contentsWidget.setEnabled(False)
            win.columnsNumber.setEnabled(False)
            win.confirmTabNumb.setEnabled(False)
            win.delColumn.setEnabled(False)
            win.tableDropCasc.setEnabled(False)
            win.tableClustered.setEnabled(False)
            win.tabSeq.setEnabled(False)
            win.getStructure.setEnabled(False)
            win.rowCount.setEnabled(False)
            win.getContents.setEnabled(False)
            win.addRow.setEnabled(False)
            win.tableRun.setEnabled(False)
        else:
            win.tableOptions.setCurrentIndex(0)
    elif win.tableOptions.currentText() == "Copy table to schema/table":
        win.tableSchema.setEnabled(True)
        win.tableName.setEnabled(True)
        win.tableOwner.setEnabled(False)
        win.tableNewName.setEnabled(False)
        win.tableNewOwner.setEnabled(False)
        win.tableNewSchema.setEnabled(True)
        win.copyToTable.setEnabled(True)
        win.columnsWidget.setEnabled(False)
        win.contentsWidget.setEnabled(False)
        win.columnsNumber.setEnabled(False)
        win.confirmTabNumb.setEnabled(False)
        win.delColumn.setEnabled(False)
        win.tableDropCasc.setEnabled(False)
        win.tableClustered.setEnabled(False)
        win.tabSeq.setEnabled(False)
        win.getStructure.setEnabled(False)
        win.rowCount.setEnabled(False)
        win.getContents.setEnabled(False)
        win.addRow.setEnabled(False)
        win.tableRun.setEnabled(True)

# DATABASE WINDOW FUNCTIONS


def serverConnect():
    start_time = time.time()
    if not win.serverName.text():
        win.textBrowser.setText('\n'+contents['messages']['servNameReq'])
    else:
        user_list, database_list, error = get_server_info()
        if error is not None:
            win.textBrowser.setText(str(error))
        else:
            global modServerInfo
            if win.editServer.isChecked():
                modServerInfo = [win.serverName.text(), win.hostField.text(
                ), win.portField.text(), win.userField.text(), win.passField.text()]
            win.mainServerTree.setEnabled(True)
            win.connectButton.setEnabled(True)
            win.checkConnection.setEnabled(False)
            win.cancelServer.setEnabled(False)
            win.serverName.setEnabled(False)
            win.hostField.setEnabled(False)
            win.portField.setEnabled(False)
            win.userField.setEnabled(False)
            win.passField.setEnabled(False)
            win.serverList.setEnabled(False)
            win.addServer.setEnabled(False)
            win.removeServer.setEnabled(False)
            win.cancelServer.setEnabled(True)
            databasesTree = QTreeWidgetItem()
            databasesTree.setText(0, 'All databases')
            databasesTree.setIcon(
                0, QIcon(os.path.join(icon_path, 'database.ico')))
            win.mainServerTree.addTopLevelItem(databasesTree)
            win.databaseList.clear()
            win.databaseList.addItem('Select database')
            for item in database_list:
                win.databaseList.addItem(item)
                databaseNode = QTreeWidgetItem(databasesTree)
                databaseNode.setText(0, item)
                databaseNode.setIcon(
                    0, QIcon(os.path.join(icon_path, 'database.ico')))
                win.mainServerTree.topLevelItem(0).addChild(databaseNode)
            usersItem = QTreeWidgetItem()
            usersItem.setText(0, 'Server users')
            usersItem.setIcon(0, QIcon(os.path.join(icon_path, 'user.ico')))
            win.mainServerTree.addTopLevelItem(usersItem)
            for user in user_list:
                userItem = QTreeWidgetItem(usersItem)
                userItem.setText(0, user)
                userItem.setIcon(0, QIcon(os.path.join(icon_path, 'user.ico')))
                win.mainServerTree.topLevelItem(1).addChild(userItem)
            win.databaseList.setEnabled(True)
        end_time = time.time()
        runtime = end_time - start_time
        win.textBrowser.setText('')
        win.textBrowser.setText(
            '\n' + contents['server']['check'] + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')


def set_initial_view():
    start_time = time.time()
    if win.dbConnect.text() == '':
        win.textBrowser.setText('\n'+contents['database']['required'])
    else:
        schemas_list, extension_list = get_schema_info()
        win.addServer.setEnabled(False)
        win.editServer.setEnabled(False)
        win.removeServer.setEnabled(False)
        win.cancelServer.setEnabled(False)
        win.checkConnection.setEnabled(False)
        win.databaseList.setEnabled(False)
        win.tabsWidget.setTabEnabled(1, True)
        win.tabsWidget.setTabEnabled(2, True)
        win.tabsWidget.setTabEnabled(3, True)
        win.tabsWidget.setTabEnabled(4, True)
        win.tabsWidget.setTabEnabled(5, True)
        win.tabsWidget.setTabEnabled(6, True)
        win.tabsWidget.setTabEnabled(7, True)
        win.navigateTo.setEnabled(True)
        win.serverList.setEnabled(False)
        win.serverTree.setEnabled(True)
        win.serverName.setEnabled(False)
        win.hostField.setEnabled(False)
        win.portField.setEnabled(False)
        win.userField.setEnabled(False)
        win.passField.setEnabled(False)
        win.dbConnect.setEnabled(False)
        win.connectButton.setEnabled(False)
        win.disconnectButton.setEnabled(True)
        win.isClustered.setEnabled(True)
        win.serverVersion.setEnabled(True)
        win.queryEditor.setEnabled(True)
        win.executeButton.setEnabled(True)
        win.dbOptions.setEnabled(True)
        win.userOptions.setEnabled(True)
        win.schemaOptions.setEnabled(True)
        win.seqOptions.setEnabled(True)
        win.tableOptions.setEnabled(True)
        if win.editServer.isChecked():
            data['names'][modServerIndex] = modServerInfo[0]
            data['servers'][modServerIndex] = modServerInfo[1]
            data['ports'][modServerIndex] = modServerInfo[2]
            data['users'][modServerIndex] = modServerInfo[3]
            data['passwords'][modServerIndex] = modServerInfo[4]
            win.serverList.setItemText(modServerListIndex, modServerInfo[0])
        else:
            if win.hostField.text() == '':
                win.hostField.setText('localhost')
            if win.portField.text() == '':
                win.portField.setText('5432')
            if win.serverName.text() in data['names']:
                pass
            else:
                data['names'].append(win.serverName.text())
                data['servers'].append(win.hostField.text())
                data['ports'].append(win.portField.text())
                data['users'].append(win.userField.text())
                data['passwords'].append(win.passField.text())
                win.serverList.addItem(win.serverName.text())
        with open(os.path.join(temp_path, 'credentials.json'), 'r+') as cred:
            cred.seek(0)
            json.dump(data, cred, indent=4)
            cred.truncate()
        serverItem = QTreeWidgetItem()
        serverItem.setText(0, 'Connected <=> ' + win.serverList.currentText() +
                           '::' + win.databaseList.currentText())
        serverItem.setIcon(0, QIcon(os.path.join(icon_path, 'database.ico')))
        win.serverTree.addTopLevelItem(serverItem)
        extensionsItem = QTreeWidgetItem(serverItem)
        extensionsItem.setText(0, 'Database extensions')
        extensionsItem.setIcon(
            0, QIcon(os.path.join(icon_path, 'extension.ico')))
        win.serverTree.topLevelItem(0).addChild(extensionsItem)
        for extension in extension_list:
            extensionItem = QTreeWidgetItem(extensionsItem)
            extensionItem.setText(0, extension)
            extensionItem.setIcon(
                0, QIcon(os.path.join(icon_path, 'extension.ico')))
            win.serverTree.topLevelItem(0).addChild(extensionItem)
        schemasItem = QTreeWidgetItem(serverItem)
        schemasItem.setText(0, 'Schemas')
        schemasItem.setIcon(0, QIcon(os.path.join(icon_path, 'schema.ico')))
        win.serverTree.topLevelItem(0).addChild(schemasItem)
        for i in range(0, len(schemas_list)):
            schemaItem = QTreeWidgetItem(schemasItem)
            schemaItem.setText(0, schemas_list[i])
            schemaItem.setIcon(0, QIcon(os.path.join(icon_path, 'schema.ico')))
            win.serverTree.topLevelItem(0).child(1).addChild(schemaItem)
            tablesItem = QTreeWidgetItem(schemaItem)
            tablesItem.setText(0, 'Tables')
            tablesItem.setIcon(0, QIcon(os.path.join(icon_path, 'table.ico')))
            win.serverTree.topLevelItem(0).child(
                1).child(i).addChild(tablesItem)
            sequencesItem = QTreeWidgetItem(schemaItem)
            sequencesItem.setText(0, 'Sequences')
            sequencesItem.setIcon(
                0, QIcon(os.path.join(icon_path, 'sequence.ico')))
            win.serverTree.topLevelItem(0).child(
                1).child(i).addChild(sequencesItem)
        end_time = time.time()
        runtime = end_time - start_time
        win.textBrowser.setText('')
        win.textBrowser.setText(
            'Query: ' + str(round(runtime, 4)) + ' seoncds')


def draw_tree_item():
    start_time = time.time()
    level_index = []
    level_text = []
    current_item = win.serverTree.currentItem()
    current_index = win.serverTree.indexFromItem(current_item)
    if current_index.isValid():
        level_index.append(current_index.row())
        level_text.append(current_index.data())
    # Iterate through all the item's parents
    while current_index.isValid():
        current_item = win.serverTree.itemFromIndex(current_index.parent())
        # Get the parent of the item and find the index of it's parent until we reach the top
        current_index = win.serverTree.indexFromItem(current_item)
        if current_index.isValid():
            level_index.append(current_index.row())
            level_text.append(current_index.data())
    # Once done getting indexes, reverse_list
    level_index = level_index[::-1]
    level_text = level_text[::-1]
    if len(level_index) == 4:
        if level_text[3] == 'Tables':
            tables_list = get_table_info(level_text[2])
            for i in range(len(tables_list)):
                tableItem = QTreeWidgetItem()
                tableItem.setText(0, tables_list[i])
                tableItem.setIcon(
                    0, QIcon(os.path.join(icon_path, 'table.ico')))
                win.serverTree.topLevelItem(0).child(1).child(
                    level_index[2]).child(0).addChild(tableItem)
                colsItem = QTreeWidgetItem(tableItem)
                colsItem.setText(0, 'Columns')
                colsItem.setIcon(
                    0, QIcon(os.path.join(icon_path, 'column.ico')))
                win.serverTree.topLevelItem(0).child(1).child(
                    level_index[2]).child(0).child(i).addChild(colsItem)
        elif level_text[3] == 'Sequences':
            sequence_list = get_sequence_info(level_text[2])
            for sequence in sequence_list:
                sequenceItem = QTreeWidgetItem()
                sequenceItem.setText(0, sequence)
                sequenceItem.setIcon(
                    0, QIcon(os.path.join(icon_path, 'sequence.ico')))
                win.serverTree.topLevelItem(0).child(1).child(
                    level_index[2]).child(1).addChild(sequenceItem)
    elif len(level_index) == 6:
        column_list = get_column_info(level_text[2], level_text[4])
        for column in column_list:
            columnItem = QTreeWidgetItem()
            columnItem.setText(0, column)
            columnItem.setIcon(
                0, QIcon(os.path.join(icon_path, 'column.ico')))
            win.serverTree.topLevelItem(0).child(1).child(
                level_index[2]).child(0).child(level_index[4]).child(0).addChild(columnItem)
    end_time = time.time()
    runtime = end_time - start_time
    win.textBrowser.setText('')
    win.textBrowser.setText('Query: ' + str(round(runtime, 4)) + ' seoncds')


def serverDisconnect():
    win.databaseList.setEnabled(True)
    win.textBrowser.setText('')
    win.textBrowser.setText('\n' + contents['server']['disconnected'])
    win.connectButton.setEnabled(True)
    win.tabsWidget.setTabEnabled(1, False)
    win.tabsWidget.setTabEnabled(2, False)
    win.tabsWidget.setTabEnabled(3, False)
    win.tabsWidget.setTabEnabled(4, False)
    win.tabsWidget.setTabEnabled(5, False)
    win.tabsWidget.setTabEnabled(6, False)
    win.tabsWidget.setTabEnabled(7, False)
    win.navigateTo.setEnabled(False)
    win.userOptions.setCurrentIndex(0)
    win.schemaOptions.setCurrentIndex(0)
    win.dbOptions.setCurrentIndex(0)
    win.tableOptions.setCurrentIndex(0)
    win.seqOptions.setCurrentIndex(0)
    win.serverTree.setEnabled(False)
    win.isClustered.setEnabled(False)
    win.serverVersion.setEnabled(False)
    win.disconnectButton.setEnabled(False)
    win.queryEditor.setEnabled(False)
    win.executeButton.setEnabled(False)
    win.dbOptions.setEnabled(False)
    win.userOptions.setEnabled(False)
    win.schemaOptions.setEnabled(False)
    win.seqOptions.setEnabled(False)
    win.tableOptions.setEnabled(False)
    win.cancelServer.setEnabled(True)
    win.serverTree.clear()


def isClustered():
    start_time = time.time()
    query = contents['server']['version']
    try:
        connection, error = connector()
        if (connection):
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(query)
            try:
                result = cursor.fetchall()
                result = str(result)
                end_time = time.time()
                runtime = end_time - start_time
                if 'XL' in result:
                    win.textBrowser.setText('\n' + contents['server']['clustered'].format(
                        win.hostField.text()) + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')
                else:
                    win.textBrowser.setText('\n' + contents['server']['notClustered'].format(
                        win.hostField.text()) + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText('\n' + contents['messages']['success'])
            connection.close()
            cursor.close()
    except Exception as Error:
        win.textBrowser.setText('\n' + str(Error))


def getVersion():
    start_time = time.time()
    query = contents['server']['version']
    try:
        connection, error = connector()
        if (connection):
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(query)
            try:
                win.textBrowser.setText("")
                result = cursor.fetchall()
                for itemList in result:
                    for itemTuble in itemList:
                        final = itemTuble.replace(', ', '\n')
                end_time = time.time()
                runtime = end_time - start_time
                win.textBrowser.setText(
                    '\n' + final + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText('\n' + contents['messages']['success'])
            connection.close()
            cursor.close()
    except Exception as Error:
        win.textBrowser.setText('\n' + str(Error))


def runDBOperation():
    start_time = time.time()
    dropResult = str(win.dbOptions.currentText())
    if dropResult == "Select opertation":
        win.dbName.setEnabled(False)
        win.exName.setEnabled(False)
        win.dbRun.setEnabled(False)
        query = None
    elif dropResult == "Create database":
        if win.dbOwner.text() == '':
            win.dbOwner.setText('postgres')
        if win.dbName.text() == '':
            win.dbName.setText('postgres')
        query = contents['database']['createDBWithOwner'].format(
            win.dbName.text(), win.dbOwner.text())
    elif dropResult == "Alter database":
        if win.dbNewName.text() == '' and win.dbNewOwner.text() == '':
            win.textBrowser.setText('\n' + contents['messages']['reqFields'])
            query = None
        elif win.dbNewName.text() == '':
            query = contents['database']['alterDBOwner'].format(
                win.dbName.text(), win.dbNewOwner.text())
        elif win.dbNewOwner.text() == '':
            query = contents['database']['alterDBName'].format(
                win.dbName.text(), win.dbNewName.text())
        else:
            query = contents['database']['alterDB'].format(
                win.dbName.text(), win.dbNewName.text(), win.dbNewOwner.text())
    elif dropResult == "Create extension":
        query = contents['extension']['createEX'].format(win.exName.text())
    elif dropResult == "Drop extension":
        query = contents['extension']['dropEX'].format(win.exName.text())
    elif dropResult == "Drop database":
        query = contents['database']['dropDB'].format(win.dbName.text())
    try:
        connection, error = connector()
        if connection:
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(query)
            win.queryEditor.setText(query)
            try:
                result = cursor.fetchall()
                end_time = time.time()
                runtime = end_time - start_time
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText(
                    '\n' + contents['messages']['success'] + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')
            connection.close()
            cursor.close()
    except Exception as Error:
        win.textBrowser.setText(
            '\n' + str(Error) + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')

# USER WINDOW FUNCTIONS


def runUserOperation():
    start_time = time.time()
    dropResult = str(win.userOptions.currentText())
    options = []
    if win.cbLogin.isChecked():
        options.append(str(contents['user']['T_optionsU'][0]))
    else:
        options.append(str(contents['user']['F_optionsU'][0]))
    if win.cbSuper.isChecked():
        options.append(str(contents['user']['T_optionsU'][1]))
    else:
        options.append(str(contents['user']['F_optionsU'][1]))
    if win.cbRole.isChecked():
        options.append(str(contents['user']['T_optionsU'][2]))
    else:
        options.append(str(contents['user']['F_optionsU'][2]))
    if win.cbDB.isChecked():
        options.append(str(contents['user']['T_optionsU'][3]))
    else:
        options.append(str(contents['user']['F_optionsU'][3]))
    if win.cbInherit.isChecked():
        options.append(str(contents['user']['T_optionsU'][4]))
    else:
        options.append(str(contents['user']['F_optionsU'][4]))
    if win.cbReplication.isChecked():
        options.append(str(contents['user']['T_optionsU'][5]))
    else:
        options.append(str(contents['user']['F_optionsU'][5]))
    options = ' '.join(options)
    if dropResult == "Select opertation":
        win.userName.setEnabled(False)
        win.userPass.setEnabled(False)
        win.cbLogin.setEnabled(False)
        win.cbSuper.setEnabled(False)
        win.cbRole.setEnabled(False)
        win.cbDB.setEnabled(False)
        win.cbInherit.setEnabled(False)
        win.cbReplication.setEnabled(False)
        win.userExecute.setEnabled(False)
        query = None
    elif dropResult == "Create new user":
        if win.userPass.text() == '':
            win.textBrowser.setText('\n' + contents['messages']['reqFields'])
            query = None
        else:
            query = contents['user']['createU'].format(
                win.userName.text(), options, win.userPass.text())
    elif dropResult == "Edit user":
        if win.userPass.text() == '':
            query = contents['user']['alterU'].format(
                win.userName.text(), options)
        else:
            query = contents['user']['alterUWithP'].format(
                win.userName.text(), options, win.userPass.text())
    elif dropResult == "Delete user":
        query = contents['user']['dropU'].format(win.userName.text())
    elif dropResult == "Grant access to database":
        query = contents['user']['grantU'].format(
            win.userDB.text(), win.userName.text())
    elif dropResult == "Revoke permissions":
        query = contents['user']['reassign'].format(win.userName.text(
        )) + '\n' + contents['user']['dropUserObject'].format(win.userName.text())
    try:
        connection, error = connector()
        if connection and query is not None:
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(query)
            try:
                result = cursor.fetchall()
                end_time = time.time()
                runtime = end_time - start_time
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText(
                    '\n' + contents['messages']['success'] + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')
            win.queryEditor.setText(query)
            connection.close()
            cursor.close()
    except Exception as Error:
        win.textBrowser.setText(
            '\n' + str(Error) + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')

# SCHEMA WINDOW FUNCTIONS


def runSchemaOperation():
    start_time = time.time()
    dropResult = str(win.schemaOptions.currentText())
    if dropResult == "Select opertation":
        win.schemaName.setEnabled(False)
        win.schemaOwner.setEnabled(False)
        win.newSchema.setEnabled(False)
        win.schemaNewOwner.setEnabled(False)
        win.schemaDropCasc.setEnabled(False)
        win.grantUsage.setEnabled(False)
        win.grantCreate.setEnabled(False)
        query = None
    elif dropResult == "Create schema":
        if win.schemaOwner.text() == '':
            win.schemaOwner.setText('postgres')
        query = contents['schema']['createSchWithOwner'].format(
            win.schemaName.text(), win.schemaOwner.text())
    elif dropResult == "Alter schema":
        if win.newSchema.text() == '' and win.schemaNewOwner.text() == '':
            win.textBrowser.setText('\n' + contents['messages']['reqFields'])
            query = None
        elif win.newSchema.text() == '':
            query = contents['schema']['alterSchemaOwner'].format(
                win.schemaName.text(), win.schemaNewOwner.text())
        elif win.dbNewOwner.text() == '':
            query = contents['schema']['alterSchemaName'].format(
                win.schemaName.text(), win.newSchema.text())
        else:
            query = contents['schema']['alterSchema'].format(
                win.schemaName.text(), win.newSchema.text(), win.schemaNewOwner.text())
    elif dropResult == "Grant access to user":
        if not win.grantUsage.isChecked() and not win.grantCreate.isChecked():
            win.textBrowser.setText('\n' + contents['messages']['reqCheck'])
            query = None
        elif not win.grantUsage.isChecked():
            query = contents['schema']['grantCreate'].format(
                win.schemaName.text(), win.schemaOwner.text())
        elif not win.grantCreate.isChecked():
            query = contents['schema']['grantUsage'].format(
                win.schemaName.text(), win.schemaOwner.text())
        else:
            query = contents['schema']['grantAll'].format(
                win.schemaName.text(), win.schemaOwner.text())
    elif dropResult == "Delete schema":
        if win.schemaDropCasc.isChecked():
            query = contents['schema']['dropCasSchema'].format(
                win.schemaName.text())
        else:
            query = contents['schema']['dropSchema'].format(
                win.schemaName.text())
    try:
        connection, error = connector()
        if connection:
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(query)
            win.queryEditor.setText(query)
            try:
                result = cursor.fetchall()
                end_time = time.time()
                runtime = end_time - start_time
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText(
                    '\n' + contents['messages']['success'] + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')
            connection.close()
            cursor.close()
    except Exception as Error:
        win.textBrowser.setText(
            '\n' + str(Error) + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')

# SEQUENCES WINDWO FUNCTIONS


def runSequenceOperation():
    start_time = time.time()
    dropResult = str(win.seqOptions.currentText())
    if dropResult == "Select operation":
        pass
        query = None
    elif dropResult == "Create sequence":
        status = True
        if win.seqName.text() == '':
            win.textBrowser.setText(contents['sequences']['reqName'])
        else:
            seqName = win.seqName.text()
        if win.seqSchema.text() == '':
            seqSchema = 'public'
        else:
            seqSchema = win.seqSchema.text()
        if win.seqOwner.text() != '' and win.seqOwnerColumn.text() != '':
            owner = 'OWNED BY {0}.{1}.{2}'.format(
                seqSchema, win.seqOwner.text(), win.seqOwnerColumn.text())
        elif win.seqOwner.text() == '' and win.seqOwnerColumn.text() == '':
            owner = ''
        else:
            win.textBrowser.setText(contents['sequences']['reqOwner'])
            owner = ''
            status = False
        if win.seqStart.text() == '':
            seqStart = 1
        else:
            try:
                if isinstance(int(win.seqStart.text()), int):
                    seqStart = win.seqStart.text()
            except Exception as error:
                win.textBrowser.setText(contents['sequences']['seqIneger'])
                status = False
        if win.seqIncrement.text() == '':
            seqIncrement = 1
        else:
            try:
                if isinstance(int(win.seqIncrement.text()), int):
                    seqIncrement = win.seqIncrement.text()
            except Exception as error:
                win.textBrowser.setText(contents['sequences']['seqIneger'])
                status = False
        if win.seqMinimum.text() == '':
            seqMinimum = 'NO MINVALUE'
        else:
            try:
                if isinstance(int(win.seqMinimum.text()), int):
                    seqMinimum = 'MINVALUE ' + win.seqMinimum.text()
            except Exception as error:
                win.textBrowser.setText(contents['sequences']['seqIneger'])
                status = False
        if win.seqMaximum.text() == '':
            seqMaximum = 'NO MAXVALUE'
        else:
            try:
                if isinstance(int(win.seqMaximum.text()), int):
                    seqMaximum = 'MAXVALUE ' + win.seqMaximum.text()
            except Exception as error:
                win.textBrowser.setText(contents['sequences']['seqIneger'])
                status = False
        query = contents['sequences']['createSequence'].format(
            seqSchema, seqName, seqIncrement, seqMinimum, seqMaximum, seqStart, owner)
    elif dropResult == "Alter sequence":
        status = True
        if win.newSeqName.text() == '':
            newSeqName = ''
        else:
            newSeqName = 'ALTER SEQUENCE IF EXISTS {0}.{1} RENAME TO '.format(
                win.seqSchema.text(), win.seqName.text()) + win.newSeqName.text() + ';'
        if win.newSeqSchema.text() == '':
            newSeqSchema = ''
        else:
            newSeqSchema = 'ALTER SEQUENCE IF EXISTS {0}.{1} SET SCHEMA '.format(
                win.seqSchema.text(), win.seqName.text()) + win.newSeqSchema.text() + ';'
        if win.revokeSeq.isChecked():
            owner = 'OWNED BY NONE'
        else:
            if win.newSeqOwner.text() != '' and win.newSeqOwnerColumn.text() != '':
                if win.newSeqName.text() == '':
                    seqSchema = win.seqName.text()
                else:
                    seqSchema = win.newSeqName.text()
                owner = 'OWNED BY {0}.{1}.{2}'.format(
                    seqSchema, win.newSeqOwner.text(), win.newSeqOwnerColumn.text())
            elif win.newSeqOwner.text() == '' and win.newSeqOwnerColumn.text() == '':
                owner = ''
            else:
                win.textBrowser.setText(contents['sequences']['reqOwner'])
                owner = ''
                status = False
        if win.seqStart.text() == '':
            seqStart = 1
        else:
            try:
                if isinstance(int(win.seqStart.text()), int):
                    seqStart = win.seqStart.text()
            except Exception as error:
                win.textBrowser.setText(contents['sequences']['seqIneger'])
                status = False
        if win.seqIncrement.text() == '':
            seqIncrement = 1
        else:
            try:
                if isinstance(int(win.seqIncrement.text()), int):
                    seqIncrement = win.seqIncrement.text()
            except Exception as error:
                win.textBrowser.setText(contents['sequences']['seqIneger'])
                status = False
        if win.seqMinimum.text() == '':
            seqMinimum = 'NO MINVALUE'
        else:
            try:
                if isinstance(int(win.seqMinimum.text()), int):
                    seqMinimum = 'MINVALUE ' + win.seqMinimum.text()
            except Exception as error:
                win.textBrowser.setText(contents['sequences']['seqIneger'])
                status = False
        if win.seqMaximum.text() == '':
            seqMaximum = 'NO MAXVALUE'
        else:
            try:
                if isinstance(int(win.seqMaximum.text()), int):
                    seqMaximum = 'MAXVALUE ' + win.seqMaximum.text()
            except Exception as error:
                win.textBrowser.setText(contents['sequences']['seqIneger'])
                status = False
        query = contents['sequences']['alterSequence'].format(win.seqSchema.text(), win.seqName.text(
        ), seqIncrement, seqMinimum, seqMaximum, seqStart, owner, newSeqName, newSeqSchema)
    elif dropResult == "Drop sequence":
        status = True
        if win.seqName.text() == '':
            win.textBrowser.setText(contents['sequences']['reqName'])
        else:
            if win.seqSchema.text() == '':
                seqSchema = 'public'
            else:
                seqSchema = win.seqSchema.text()
            seqName = win.seqName.text()
        query = contents['sequences']['dropSequence'].format(
            seqSchema, seqName)
    if status:
        connection, error = connector()
        if connection:
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(query)
            win.queryEditor.setText(query)
            try:
                result = cursor.fetchall()
                end_time = time.time()
                runtime = end_time - start_time
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText(
                    '\n' + contents['messages']['success'] + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')
            connection.close()
            cursor.close()


def load_seq_info():
    start_time = time.time()
    if win.seqName.text() == '':
        win.textBrowser.setText(contents['sequences']['reqName'])
    else:
        if win.seqSchema.text() == '':
            win.seqSchema.setText('public')
        query = contents['sequences']['loadSequence'].format(
            win.seqSchema.text(), win.seqName.text())
        connection, error = connector()
        if connection:
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(query)
            win.queryEditor.setText(query)
            try:
                result = cursor.fetchall()
                end_time = time.time()
                runtime = end_time - start_time
                for value in result:
                    win.seqStart.setText(str(value[0]))
                    win.seqMinimum.setText(value[1])
                    win.seqMaximum.setText(value[2])
                    win.seqIncrement.setText(value[3])
            except psycopg2.ProgrammingError as Error:
                win.textBrowser.setText(
                    '\n' + contents['messages']['success'] + '\nQuery: ' + str(round(runtime, 4)) + ' seoncds')
            connection.close()
            cursor.close()
        win.seqStart.setEnabled(True)
        win.seqMinimum.setEnabled(True)
        win.seqMaximum.setEnabled(True)
        win.seqIncrement.setEnabled(True)
        win.newSeqName.setEnabled(True)
        win.newSeqSchema.setEnabled(True)
        win.newSeqOwner.setEnabled(True)
        win.revokeSeq.setEnabled(True)
        win.newSeqOwnerColumn.setEnabled(True)
        win.seqName.setEnabled(False)
        win.seqSchema.setEnabled(False)
        win.loadSeq.setEnabled(False)
        win.seqRun.setEnabled(True)

# TABLE WINDOW FUNCTIONS


def setTableColumns():
    spinBoxValue = win.columnsNumber.value()
    win.columnsWidget.setRowCount(spinBoxValue)


def createComboWidget():
    if not win.confirmTabNumb.isChecked():
        win.columnsWidget.setEnabled(False)
        win.columnsNumber.setEnabled(True)
        win.confirmTabNumb.setText('Lock number')
    else:
        win.columnsWidget.setEnabled(True)
        win.columnsNumber.setEnabled(False)
        win.confirmTabNumb.setText('Unlock number')
        for i in range(win.columnsNumber.value()):
            dataTypeComboValues = contents['combobox']['dataTypes']
            logicComboValues = contents['combobox']['logic']
            comboBox1 = QtWidgets.QComboBox()
            comboBox2 = QtWidgets.QComboBox()
            comboBox3 = QtWidgets.QComboBox()
            for value in dataTypeComboValues:
                comboBox1.addItem(value)
            for value in logicComboValues:
                comboBox2.addItem(value)
            for value in logicComboValues:
                comboBox3.addItem(value)
            win.columnsWidget.setCellWidget(i, 1, comboBox1)
            win.columnsWidget.setCellWidget(i, 4, comboBox2)
            win.columnsWidget.setCellWidget(i, 5, comboBox3)
            win.columnsWidget.resizeColumnsToContents()


# MAIN FUNCTION
if __name__ == '__main__':
    if importFlag and envVariables and appWindow and appSetting and widgFlag:
        # INITIATE TABS VISIBILITY
        win.tabsWidget.setTabEnabled(1, False)
        win.tabsWidget.setTabEnabled(2, False)
        win.tabsWidget.setTabEnabled(3, False)
        win.tabsWidget.setTabEnabled(4, False)
        win.tabsWidget.setTabEnabled(5, False)
        win.tabsWidget.setTabEnabled(6, False)
        win.tabsWidget.setTabEnabled(7, False)
        # INITIATE MAIN FUNCTIONS
        win.clearBoxes.clicked.connect(clearFields)
        win.clearHistory.clicked.connect(clearHistory)
        win.executeButton.clicked.connect(querier)
        executeShortcut.activated.connect(querier)
        win.refresh.clicked.connect(refresh)
        # INITIATE COMBOBOX CHANGED TRIGGERS
        win.serverList.currentTextChanged.connect(serverComboChanged)
        win.databaseList.currentTextChanged.connect(dbListComboChanged)
        win.dbOptions.currentTextChanged.connect(dbComboChanged)
        win.userOptions.currentTextChanged.connect(userComboChanged)
        win.schemaOptions.currentTextChanged.connect(schemaComboChanged)
        win.tableOptions.currentTextChanged.connect(tableComboChanged)
        win.seqOptions.currentTextChanged.connect(sequenceComboChanged)
        # INITIATE NAVIGATION TRIGGERS
        win.exitOption.triggered.connect(sys.exit)
        win.aboutOption.triggered.connect(getAbout)
        win.authorOption.triggered.connect(getAuthor)
        win.creditsOption.triggered.connect(getCredits)
        win.databaseOption.triggered.connect(navToDB)
        win.userOption.triggered.connect(navToUS)
        win.schemaOption.triggered.connect(navToSC)
        win.tableOption.triggered.connect(navToTA)
        win.seqOption.triggered.connect(navToSE)
        win.importOption.triggered.connect(navToIE)
        win.toolsOption.triggered.connect(navToAT)
        win.backupOption.triggered.connect(navToBR)
        # INITIATE DATABASE FUNCTIONS
        win.cancelServer.clicked.connect(cancel_server)
        win.addServer.clicked.connect(add_server)
        win.editServer.clicked.connect(edit_server)
        win.removeServer.clicked.connect(delete_server)
        win.checkConnection.clicked.connect(connectDialog)
        win.disconnectButton.clicked.connect(disconnectDialog)
        win.connectButton.clicked.connect(set_initial_view)
        win.isClustered.clicked.connect(isClustered)
        win.serverVersion.clicked.connect(getVersion)
        win.dbRun.clicked.connect(runDBOperation)
        # INITIATE TREE VIEW TRIGGERS
        win.serverTree.doubleClicked.connect(draw_tree_item)
        # INITIATE USER FUNCTIONS
        win.userExecute.clicked.connect(runUserOperation)
        # INITIATE SCHEMA FUNCTIONS
        win.schemaRun.clicked.connect(runSchemaOperation)
        # INITIATE SEQUENCES FUNCTIONS
        win.seqRun.clicked.connect(runSequenceOperation)
        win.loadSeq.clicked.connect(load_seq_info)
        # INITIATE SPINBOX TRIGGERS
        win.columnsNumber.valueChanged.connect(setTableColumns)
        # INITIATE TABLE FUNCTIONS
        win.confirmTabNumb.toggled.connect(createComboWidget)
        # win.tableRun.clicked.connect(runTableOperation)
        # INITIATE GUI WINDOW
        win.show()
        app.exec()
    else:
        print('Application could not be started!')
