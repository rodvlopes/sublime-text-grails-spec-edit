import sublime, sublime_plugin, os, os.path

class RopenCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):

		viewFile = self.view.file_name()

		if viewFile.find('/target/') > -1:
			projectPath = viewFile.split('target/')[0]
			self.view.run_command("expand_selection", {"to": "brackets"})
			self.open_source(projectPath)
		elif viewFile.find('/grails-app/') > -1:
			projectPath = viewFile.split('grails-app/')[0]
			viewFileBasename = os.path.basename(os.path.basename(viewFile))
			testType = ''
			if args and args['integration']:
				testType = 'Int'
			testFile = viewFileBasename.replace('.groovy', testType+'Spec.groovy') 
			self.open_test_source(projectPath, testFile)
		elif viewFile.find('/test/') > -1:
			projectPath = viewFile.split('test/')[0]
			viewFileBasename = os.path.basename(os.path.basename(viewFile))
			self.open_test_result(projectPath, viewFileBasename)


		
		#view.find("\(\w+\.groovy:")
		#http://www.sublimetext.com/docs/2/api_reference.html
		#http://code.tutsplus.com/tutorials/how-to-create-a-sublime-text-2-plugin--net-22685
		#https://github.com/SublimeText/CTags/blob/development/ctagsplugin.py


	def open_test_result(self, projectPath, testFile):
		window = sublime.active_window()
		testResultFilePtrn = '.'+testFile.replace('.groovy', '.txt')

		for root, subFolders, files in os.walk(projectPath):
				for f in files:
					if f.find(testResultFilePtrn) > -1:
						window.open_file(root+'/'+f)



	def open_test_source(self, projectPath, testFile):
		window = sublime.active_window()

		for root, subFolders, files in os.walk(projectPath):
				if testFile in files:
					window.open_file(root+'/'+testFile)



	def open_source(self, projectPath):
		sels = self.view.sel()
		window = sublime.active_window()
		ON_LOAD = self.get_onload()

		for sel in sels:
			strSel = self.view.substr(sel)
			fileName, lineNum = strSel.split(':')
			
			for root, subFolders, files in os.walk(projectPath):
				if fileName in files:
					targetView = window.open_file(root+'/'+fileName)
					ON_LOAD.position_view(targetView, lineNum)



	def get_onload(self):
		for cb in sublime_plugin.all_callbacks['on_load']:
			if cb.__class__.__name__ == 'RopenCommandEvents':
				return cb
					



class RopenCommandEvents(sublime_plugin.EventListener):

	stack = []

	def on_load(self, view):
		if (self.stack):
			v,ln = self.stack.pop()
			self.position_immediately(view,ln)

	def position_view(self, view, lineNum):
		if view.is_loading():
			self.stack.append( (view, lineNum) )
		else:
			self.position_immediately(view,lineNum)

	def position_immediately(self, view, lineNum):
		position = view.text_point(int(lineNum)-1, 0)
		view.sel().clear()
		view.sel().add(sublime.Region(position))
		view.show(position)
