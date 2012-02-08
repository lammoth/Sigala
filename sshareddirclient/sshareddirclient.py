#!/usr/bin/python
# -*- coding: utf-8 -*-
## \namespace sshareddirclient
import os
import sys
import socket
import urllib

from PyQt4 import QtGui
from PyQt4 import QtCore
import davclient

from sigala.sshareddirclient import sshareddirclient_resources
from sigala.common.settings import SHARED_PRIVATE
from sigala.common.settings import VALID_CHARS


##\class SSharedDirClient
# \brief Webdav explorer main class
class SSharedDirClient(QtGui.QWidget):
	##\fn __init__(self, parent = None, data = None)
	# \brief Class constructor, create webdav connection and GUI Webdav explorer client
	# \param[in] data: Connection data (ip, port, user, password, nick and group)
	def __init__(self, parent = None, data = None):
		QtGui.QWidget.__init__(self, parent)

		data['group'] = self.sanitize(data['group'])
		data['nick'] = self.sanitize(data['nick'])

		self.remotedir = os.path.sep + SHARED_PRIVATE + os.path.sep + data['group'] + os.path.sep + data['nick']
		self.davbackend = clientDAVBackend(data)
		self.setWindowTitle("Sigala - Carpeta Compartida")
		self.resize(560, 520)
		self.setMinimumSize(560, 520)
		self.upspace = uploadWidget(parent = self, wdb = self.davbackend, remotedir = self.remotedir)
		self.expwebdav = explorerDAV(parent = self, wdb = self.davbackend)

		vboxmain = QtGui.QVBoxLayout()
		self.setLayout(vboxmain)
		hboxup = QtGui.QHBoxLayout()
		hboxup.addWidget(self.upspace)
		remotelistbutton = QtGui.QPushButton("", self)
		self.connect(remotelistbutton, QtCore.SIGNAL("clicked()"), self.remote_list_file)
		remotelistbutton.setStyleSheet("background-color: rgb(112, 112, 112); background-image: url(:img/images/remote-list-file.png); background-repeat: no-repeat; background-position: center")
		remotelistbutton.setMaximumSize(100, 100)
		hboxup.addWidget(remotelistbutton)

		vboxmain.addLayout(hboxup)
		vboxmain.addWidget(self.expwebdav)

	def remote_list_file(self):
		self.listfilewindow = QtGui.QWidget()
		self.listfilewindow.setWindowTitle('Archivos subidos')
		self.listfilewindow.resize(460, 500)
		self.listfilewindow.setMinimumSize(460, 500)
		vbox = QtGui.QVBoxLayout()
		self.listfilewindow.setLayout(vbox)
		filelistupload = explorerDAV(parent = self.listfilewindow, wdb = self.davbackend, userdir = self.remotedir, viewmode = 1)
		vbox.addWidget(filelistupload)
		self.listfilewindow.show()

	def sanitize(self, data):
		data = data.replace(' ', '_')
		for a,b in ( ('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ñ', 'n'),
					('Á', 'A'), ('É', 'E'), ('Í', 'I'), ('Ó', 'O'), ('Ú', 'U'), ('Ñ', 'N') ):
			data=data.replace(a, b)
		data = str(filter(lambda k: k in VALID_CHARS, data)).lower()
		return data


##\class uploadWidget
# \brief Upload file widget
class uploadWidget(QtGui.QFrame):
	##\fn __init__(self, parent = None, wdb = None)
	# \brief Create upload widget
	# \param[in] wdb: Webdav connection backend
	# \param[in] remotedir: User remote directory in webdav server
	def __init__(self, parent = None, wdb = None, remotedir = None):
		QtGui.QFrame.__init__(self, parent)
		self.davbackend = wdb
		self.remotedir = remotedir
		self.setMinimumSize(400, 100)
		self.setFrameShape(QtGui.QFrame.StyledPanel)
		self.setFrameShadow(QtGui.QFrame.Raised)
		self.setStyleSheet("background-color: rgb(112, 112, 112);")
		self.setLineWidth(1)
		self.setMidLineWidth(1)
		self.setAcceptDrops(True)
		vbox = QtGui.QVBoxLayout()
		self.setLayout(vbox)
		vbox.setAlignment(QtCore.Qt.AlignHCenter)
		vbox.setAlignment(QtCore.Qt.AlignVCenter)
		label = QtGui.QLabel('Arrastrar y soltar a este espacio\nlos archivos que desea subir')
		label.setStyleSheet("font: bold 14px; color: rgb(255, 255, 255);")
		label.setAlignment(QtCore.Qt.AlignHCenter)
		vbox.addWidget(label)


	##\fn dragEnterEvent(self, event)
	# \brief dragEnterEvent overload
	def dragEnterEvent(self, event):
		event.acceptProposedAction()

	##\fn dropEvent(self, event)
	# \brief dropEvent overload
	def dropEvent(self, event):
		event.accept()
		pathfiles = str(event.mimeData().text()).replace('file://','').split('\n')
		error = False
		for pathfile in pathfiles:
			if pathfile == '':
				continue
			try:
				filename = pathfile.split('/')[-1]
				fich = open(urllib.unquote(pathfile.strip()), 'r')
				cont = fich.readline()
				if cont == "":
					infouploadi=QtGui.QMessageBox.warning(self, 'Error', '<b>No es posible subir archivos sin contenido</b>', QtGui.QMessageBox.Ok)
					error = True
					fich.close()
					continue
				fich.seek(0, os.SEEK_SET)
				self.davbackend.upload_file(self.remotedir + os.path.sep + self.sanitize(filename), fich)
				fich.close()
			except IOError, msg:
				print msg
				infouploadi=QtGui.QMessageBox.warning(self, 'Error', '<b>El archivo o archivos no han podido ser enviados</b>', QtGui.QMessageBox.Ok)
				error = True
		if not error:
			infouploadi=QtGui.QMessageBox.information(self, 'Terminado', 'Archivos subidos correctamente', QtGui.QMessageBox.Ok)

	def sanitize(self, data):
		data = data.replace(' ', '_')
		for a,b in ( ('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ñ', 'n'),
					('Á', 'A'), ('É', 'E'), ('Í', 'I'), ('Ó', 'O'), ('Ú', 'U'), ('Ñ', 'N') ):
			data=data.replace(a, b)
		#data = str(filter(lambda k: k in VALID_CHARS, data)).lower()
		return data

##\class explorerDAV
# \brief Webdabav file browser
class explorerDAV(QtGui.QWidget):
	##\fn __init__(self, parent = None, wdb = None, userdir = None, viewmode = 0)
	# \brief Create gui explorer
	# \param[in] wdb: WebDav connection backend
	# \param[in] userdir: user remote directory (only for viewmode = 1)
	# \param[in] viewmode: webdav client explorer viewmode, 0 is normal mode, 1 is minimal mode(only user remote file list)
	def __init__(self, parent = None, wdb = None, userdir = None, viewmode = 0):
		QtGui.QWidget.__init__(self, parent)
		self.davbackend = wdb

		vboxexp = QtGui.QVBoxLayout()
		self.setLayout(vboxexp)

		if viewmode == 0:
			label = QtGui.QLabel("Ficheros Compartidos", self)
		else:
			label = QtGui.QLabel("Ficheros Subidos", self)
		label.setStyleSheet("font: bold 14px; color: rgb(0, 0, 0);")
		vboxexp.addWidget(label)

		if viewmode == 0:
			hboxbuttonsexp = QtGui.QHBoxLayout()
			vboxexp.addLayout(hboxbuttonsexp)
			hboxbuttonsexp.setAlignment(QtCore.Qt.AlignLeft)
			upicon = QtGui.QIcon()
			upicon.addPixmap(QtGui.QPixmap(":img/images/up.png"))
			reloadicon = QtGui.QIcon()
			reloadicon.addPixmap(QtGui.QPixmap(":img/images/refresh.png"))
			homeicon = QtGui.QIcon()
			homeicon.addPixmap(QtGui.QPixmap(":img/images/home.png"))
			viewicons = QtGui.QIcon()
			viewicons.addPixmap(QtGui.QPixmap(":img/images/view-list-icons.png"))
			viewlist = QtGui.QIcon()
			viewlist.addPixmap(QtGui.QPixmap(":img/images/view-list-details.png"))
			upbutton = QtGui.QPushButton(upicon, "", self)
			self.connect(upbutton, QtCore.SIGNAL("clicked()"), self.up_level)
			upbutton.setMinimumSize(32, 32)
			reloadbutton = QtGui.QPushButton(reloadicon, "", self)
			self.connect(reloadbutton, QtCore.SIGNAL("clicked()"), self.reload_dir)
			reloadbutton.setMinimumSize(32, 32)
			homebutton = QtGui.QPushButton(homeicon, "", self)
			self.connect(homebutton, QtCore.SIGNAL("clicked()"), self.goto_init)
			homebutton.setMinimumSize(32, 32)
			viewiconsbutton = QtGui.QPushButton(viewicons, "", self)
			self.connect(viewiconsbutton, QtCore.SIGNAL("clicked()"), self.set_icons_view)
			viewiconsbutton.setMinimumSize(32, 32)
			viewlistbutton = QtGui.QPushButton(viewlist, "", self)
			self.connect(viewlistbutton, QtCore.SIGNAL("clicked()"), self.set_list_view)
			viewlistbutton.setMinimumSize(32, 32)
			hboxbuttonsexp.addWidget(upbutton)
			hboxbuttonsexp.addWidget(reloadbutton)
			hboxbuttonsexp.addWidget(homebutton)
			hboxbuttonsexp.addWidget(viewiconsbutton)
			hboxbuttonsexp.addWidget(viewlistbutton)

		self.filespace = QtGui.QListWidget()
		self.filespace.setMovement(0)
		self.filespace.setViewportMargins(5, 5, 5, 5)
		if viewmode == 0:
			self.set_icons_view()
		else:
			self.set_list_view()
		self.filespace.setSortingEnabled(True)
		self.connect(self.filespace, QtCore.SIGNAL("itemActivated(QListWidgetItem *)"), self.enter_dir)
		vboxexp.addWidget(self.filespace)

		if viewmode == 0:
			hboxbuttons = QtGui.QHBoxLayout()
			downloadicon = QtGui.QIcon()
			downloadicon.addPixmap(QtGui.QPixmap(":img/images/download.png"))
			downloadbutton = QtGui.QPushButton(downloadicon, "Descargar fichero", self)
			self.connect(downloadbutton, QtCore.SIGNAL("clicked()"), self.download_target_selection)
			downloadbutton.setMaximumSize(180, 64)
			hboxbuttons.addWidget(downloadbutton)
			vboxexp.addLayout(hboxbuttons)

		resp = self.davbackend.dir_access('/')
		if resp == '-1':
			print "No hay que ejecutar la aplicacion"
		else:
			if viewmode == 0:
				self.current_dir = '/'
				self.level = 3
				self.fill_explorer()
			else:
				self.current_dir = userdir
				self.level = 6
				self.fill_explorer()

	##\fn fill_explorer(self)
	# \fn Load webdav directory based in self.current_dir and self.level
	def fill_explorer(self):
		self.filespace.clear()
		resp = self.davbackend.dir_access(self.current_dir)
		if resp == '-1':
			return '-1'
		for elem in resp.keys():
			string = elem.split('/')[self.level:]
			try:
				if string[0] == SHARED_PRIVATE:
					continue
				icon = QtGui.QIcon()
				if resp[elem]['getcontenttype'] == 'httpd/unix-directory' and string[0]:
					icon.addPixmap(QtGui.QPixmap(":mimetype/mimetypes/mimetype-folder.png"))
					item_type = 0
				else:
					icon.addPixmap(self.mime_type(string[0]))
					item_type = 1
				item = explorerItem(icon, unicode(urllib.unquote(string[0]), 'utf-8').encode('latin-1'))
				item.set_type(item_type)
				self.filespace.addItem(item)

			except IndexError, msg:
				continue
			except KeyError, msg:
				continue
	##\fn reload_dir(self)
	# \brief Reload current directory
	def reload_dir(self):
		self.fill_explorer()

	##\fn goto_init(self)
	# \brief Go to initial webdav directory
	def goto_init(self):
		self.current_dir = '/'
		self.level = 3
		self.fill_explorer()

	##\fn up_level(self)
	# \brief Up a one level dir on webdav explorer
	def up_level(self):
		if self.level == 3:
			return
		string = self.current_dir.split('/')
		string = string[1:-2]
		self.current_dir = '/'
		for i in range(0,len(string)):
			self.current_dir = self.current_dir + string[i] + '/'
		self.level = self.level - 1
		self.fill_explorer()

	##\fn enter_dir(self)
	# \brief Access to directory selected
	def enter_dir(self):
		selected_item = self.filespace.currentItem()
		if selected_item is not None:
			row = self.filespace.row(selected_item)
			item = self.filespace.item(row)
			if item.item_type == 1:
				return False
			else:
				self.level = self.level + 1
				self.current_dir = self.current_dir + item.text() + os.path.sep
				self.fill_explorer()
	##\fn download_target_selection(self)
	# \brief Download file selected in explorer
	def download_target_selection(self):
		selected_item = self.filespace.currentItem()
		if selected_item is not None:
			row = self.filespace.row(selected_item)
			item = self.filespace.item(row)
			if item.item_type == 0:
				return False
			else:
				name = self.current_dir + item.text()
				name.replace(' ','%20')
				target = os.environ.get('HOME') + os.path.sep + item.text()
				filename = QtGui.QFileDialog.getSaveFileName(self, 'Guardar Como', target, 'All files (*)')
				try:
					fich = open(filename, 'w')
					fich.write(self.davbackend.download_file(name))
					fich.close()
				except socket.error, msg:
					fich.close()
					os.remove(filename)

	def mime_type(self, name):
		ext = name.split('.')[-1]
		if ext == 'html' or ext == 'htm':
			return QtGui.QPixmap(":mimetype/mimetypes/mimetype-html.png")
		elif ext == 'png' or ext == 'jpg' or ext == 'jpeg' or ext == 'gif' or ext == 'bmp':
			return QtGui.QPixmap(":mimetype/mimetypes/mimetype-image.png")
		elif ext == 'mp3' or ext == 'ogg' or ext == 'wma':
			return QtGui.QPixmap(":mimetype/mimetypes/mimetype-audio.png")
		elif ext == 'ods':
			return QtGui.QPixmap(":mimetype/mimetypes/mimetype-oocalc.png")
		elif ext == 'odp':
			return QtGui.QPixmap(":mimetype/mimetypes/mimetype-ooimpress.png")
		elif ext == 'odt':
			return QtGui.QPixmap(":mimetype/mimetypes/mimetype-oowriter.png")
		elif ext == 'pdf':
			return QtGui.QPixmap(":mimetype/mimetypes/mimetype-pdf.png")
		elif ext == 'txt':
			return QtGui.QPixmap(":mimetype/mimetypes/mimetype-txt.png")
		elif ext == 'avi' or ext == 'mpg' or ext == 'mpeg' or ext == 'mov' or ext == 'flv' or ext == 'wmv':
			return QtGui.QPixmap(":mimetype/mimetypes/mimetype-video.png")
		elif ext == 'zip' or ext == 'gz' or ext == 'bz' or ext == 'bz2' or ext == 'rar':
			return QtGui.QPixmap(":mimetype/mimetypes/mimetype-zip.png")
		else:
			return QtGui.QPixmap(":mimetype/mimetypes/mimetype-file.png")

	def set_icons_view(self):
		self.filespace.setViewMode(1)
		self.filespace.setGridSize(QtCore.QSize(120, 58))

	def set_list_view(self):
		self.filespace.setViewMode(0)
		self.filespace.setGridSize(QtCore.QSize(120, 30))

##\class explorer_element
# \brief
class explorerItem(QtGui.QListWidgetItem):
	def set_type(self, item_type):
		self.item_type = item_type

##\class clientDAVBackend
# \brief Manage the webdav client connection
class clientDAVBackend:
	##\fn __init__(self, data, remotedir)
	# \brief Configure connection with parameters IP, port, user and password
	# \param[in] data: client data configuration
	def __init__(self, data):
		self.connection = davclient.DAVClient('http://%s:%s' % (data['IP'], data['port']))
		self.connection.set_basic_auth(data['user'], data['password'])
		remotegroupdir = os.path.sep + SHARED_PRIVATE + os.path.sep + data['group']
		remoteuserdir = remotegroupdir + os.path.sep + data['nick']
		self.connection.mkcol(remotegroupdir)
		self.connection.mkcol(remoteuserdir)

	##\fn dir_access(self, dir)
	# \brief Access to remote webdav directory
	# \param[in] dir: directory to access
	# \param[out] Directory data accessed
	def dir_access(self, dir):
		try:
			return self.connection.propfind(dir, depth = 1)
		except:
			print "Error de conexion con servidor WebDav"
			return '-1'

	##\fn download_file(self, path)
	# \brief Download file in webdav server path
	# \param[in] path: path to file to download
	def download_file(self, path):
		print path
		return self.connection.get(path)

	def upload_file(self, name, data):
		self.connection.put(name, f = data)

#app = QtGui.QApplication(sys.argv)
#datos = {"IP": "10.227.255.167", "port": "8008", "user": "usuario", "password": "usuario" }
#wdclient = SSharedDirClient(data = datos)
#wdclient.show()

#sys.exit(app.exec_())
