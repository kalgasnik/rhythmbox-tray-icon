import rb
from gi.repository import Gtk, Gio, GObject, PeasGtk

class TrayIconConfig(GObject.Object, PeasGtk.Configurable):

	__gtype_name__ = 'TrayIconConfig'
	object = GObject.property(type=GObject.Object)

	options = \
	{
		'normal-icon': ('normal_icon', 'text', Gio.SettingsBindFlags.DEFAULT),
		'play-icon': ('play_icon', 'text', Gio.SettingsBindFlags.DEFAULT),
		'merge-play-icon': ('merge_play_icon', 'active', Gio.SettingsBindFlags.DEFAULT)
	}

	def do_create_configure_widget(self):
		self.settings = Gio.Settings("org.gnome.rhythmbox.plugins.trayicon")
		self.builder = Gtk.Builder()
		self.builder.add_from_file(rb.find_plugin_file(self, "trayicon-prefs.ui"))

		for key, (name, prop, flags) in self.options.items():
			self.settings.bind(key, self.builder.get_object(name), prop, flags)

		return self.builder.get_object("trayicon-prefs")

GObject.type_register(TrayIconConfig)