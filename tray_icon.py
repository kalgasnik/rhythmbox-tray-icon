from gi.repository import Gtk, Gdk, Peas, GObject
import cairo

normalIconName = "rhythmbox"
playIconName = "media-playback-start"

class TrayIcon(GObject.Object, Peas.Activatable):

	__gtype_name = 'TrayIcon'
	object = GObject.property(type=GObject.Object)

	def popup_menu(self, icon, button, time, data = None):
		self.popup.popup(None, None, None, None, button, time)

	def toggle(self, icon, event, data = None):
		if event.button == 1: # left button
			if self.wind.get_visible():
				self.wind.hide()
			else:
				self.wind.show()
				self.wind.present()

	def play(self, widget):
		self.player.playpause(True) # does nothing argument

	def nextItem(self, widget):
		self.player.do_next()

	def previous(self, widget):
		self.player.do_previous()

 	def quit(self, widget):
		self.shell.quit()

	def hide_on_delete(self, widget, event):
		self.wind.hide()
		return True # don't actually delete

	def set_playing_icon(self, player, playing):
		if playing:
			self.icon.set_from_icon_name(playIconName)
		else:
			self.icon.set_from_icon_name(normalIconName)

	def do_activate(self):
		self.shell = self.object
		self.wind = self.shell.get_property("window")
		self.player = self.shell.props.shell_player

		self.wind.connect("delete-event", self.hide_on_delete)

		ui = Gtk.UIManager()
		ui.add_ui_from_string(
		"""
		<ui>
		  <popup name='PopupMenu'>
			<menuitem action='PlayPause' />
			<menuitem action='Next' />
			<menuitem action='Previous' />
			<separator />
			<menuitem action='Quit' />
		  </popup>
		</ui>
		""")

		ag = Gtk.ActionGroup("actions")
		ag.add_actions([
				("PlayPause",Gtk.STOCK_MEDIA_PLAY,"Play/Pause",None, None, self.play),
				("Next",Gtk.STOCK_MEDIA_NEXT,"Next",None, None, self.nextItem),
				("Previous",Gtk.STOCK_MEDIA_PREVIOUS,"Previous",None, None, self.previous),
				("Quit",None,"Quit",None, None, self.quit)
				])
		ui.insert_action_group(ag)
		self.popup = ui.get_widget("/PopupMenu")

		self.icon = Gtk.StatusIcon.new_from_icon_name(normalIconName)
		self.icon.connect("scroll-event", self.scroll)
		self.icon.connect("popup-menu", self.popup_menu)
		self.icon.connect("button-press-event", self.toggle)
		self.player.connect("playing-changed", self.set_playing_icon)

	def scroll(self, widget, event):
		if self.player.playpause(True):
			# scroll up for previous track
			if event.direction == Gdk.ScrollDirection.UP:
				self.previous(widget)
			# scroll down for next track
			elif event.direction == Gdk.ScrollDirection.DOWN:
				self.nextItem(widget)

	def do_deactivate(self):
		self.icon.set_visible(False)
		del self.icon
