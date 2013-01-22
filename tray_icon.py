from gi.repository import Gtk, Gio, Gdk, GdkPixbuf, Peas, GObject
import os

from config import TrayIconConfig

default_icon_size = 32

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
		icon = self.play_icon if playing else self.normal_icon
		if type(icon) is str:
			self.icon.set_from_icon_name(icon)
		else:
			self.icon.set_from_pixbuf(icon)

	def do_activate(self):
		self.shell = self.object
		self.wind = self.shell.get_property("window")
		self.player = self.shell.props.shell_player
		self.settings = Gio.Settings("org.gnome.rhythmbox.plugins.trayicon")

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

		self.icon = Gtk.StatusIcon()
		self.update_icons()		
		self.icon.connect("scroll-event", self.scroll)
		self.icon.connect("popup-menu", self.popup_menu)
		self.icon.connect("button-press-event", self.toggle)
		self.player.connect("playing-changed", self.set_playing_icon)
		self.settings.connect("changed::", lambda settings, key: self.update_icons())
		Gtk.IconTheme.get_default().connect("changed", lambda theme: self.update_icons())

	def read_icon(self, name, icon_as_pixbuf):
		if os.path.isabs(name):
			return GdkPixbuf.Pixbuf.new_from_file(name)
		elif icon_as_pixbuf:
			return Gtk.IconTheme.get_default().load_icon(name, default_icon_size, 0)
		elif Gtk.IconTheme.get_default().has_icon(name):
			return name
		else:
			return None

	def update_icons(self):
		merge = self.settings.get_boolean('merge-play-icon')
		normal_name = self.settings.get_string('normal-icon')
		play_name = self.settings.get_string('play-icon')
		
		try:
			self.normal_icon = self.read_icon(normal_name, merge)
			self.play_icon = self.read_icon(play_name, merge)
		except GObject.GError:
			return
		
		if self.normal_icon is None or self.play_icon is None:
			return

		if merge:
			play_icon = self.normal_icon.copy()
			scalex, scaley = float(self.normal_icon.props.width)/self.play_icon.props.width, float(self.normal_icon.props.height)/self.play_icon.props.height
			self.play_icon.composite(play_icon, 0, 0, self.normal_icon.props.width, self.normal_icon.props.height, 0, 0, scalex, scaley, GdkPixbuf.InterpType.HYPER, 255)
			self.play_icon = play_icon

		self.set_playing_icon(self.player, self.player.props.playing)

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