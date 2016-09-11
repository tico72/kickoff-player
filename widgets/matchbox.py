import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GObject, Pango
from widgets.streambox import StreamBox
from helpers.gtk import add_widget_class, image_from_path, remove_widget_children


class MatchBox(Gtk.FlowBoxChild):

	__gtype_name__ = 'MatchBox'

	fixture = GObject.property(type=object, flags=GObject.PARAM_READWRITE)
	callback = GObject.property(type=object, flags=GObject.PARAM_READWRITE)
	filter_name = GObject.property(type=str, flags=GObject.PARAM_READWRITE)

	def __init__(self, *args, **kwargs):
		Gtk.FlowBoxChild.__init__(self, *args, **kwargs)

		self.fixture = self.get_property('fixture')
		self.callback = self.get_property('callback')
		self.filter_name = self.get_property('filter-name')

		self.outer_box = self.do_outer_box()
		self.teams_box = None
		self.details_box = None

		self.set_valign(Gtk.Align.START)
		self.connect('realize', self.on_realized)
		self.connect('notify::fixture', self.on_fixture_updated)

		add_widget_class(self, 'event-item')

		self.show()

	def on_realized(self, *_args):
		self.filter_name = getattr(self.fixture, 'competition').name
		self.update_outer_box()

	def on_fixture_updated(self, *_args):
		self.teams_box.set_property('fixture', self.fixture)
		self.details_box.set_property('fixture', self.fixture)

	def do_outer_box(self):
		box = Gtk.Box()
		box.set_orientation(Gtk.Orientation.VERTICAL)

		return box

	def update_outer_box(self):
		self.teams_box = MatchTeamsBox(fixture=self.fixture)
		self.outer_box.pack_start(self.teams_box, True, True, 0)

		self.details_box = MatchDetailsBox(fixture=self.fixture, callback=self.callback)
		self.outer_box.pack_start(self.details_box, True, True, 1)

		self.outer_box.show()
		self.add(self.outer_box)


class MatchTeamsBox(Gtk.Box):

	__gtype_name__ = 'MatchTeamsBox'

	fixture = GObject.property(type=object, flags=GObject.PARAM_READWRITE)

	def __init__(self, *args, **kwargs):
		Gtk.Box.__init__(self, *args, **kwargs)

		self.fixture = self.get_property('fixture')

		self.home_crest = self.do_team_crest()
		self.home_name = self.do_team_name()
		self.home_box = self.do_team_box('home')

		self.away_crest = self.do_team_crest()
		self.away_name = self.do_team_name()
		self.away_box = self.do_team_box('away')

		self.score = self.do_score_label()
		self.score_box = self.do_score_box()

		self.set_orientation(Gtk.Orientation.HORIZONTAL)
		self.set_homogeneous(True)

		self.connect('realize', self.on_realized)
		self.connect('notify::fixture', self.on_fixture_updated)

		self.show()

	def on_realized(self, *_args):
		self.update_team_crest('home')
		self.update_team_name('home')
		self.pack_start(self.home_box, True, True, 0)

		self.update_score_label()
		self.pack_start(self.score_box, True, True, 1)

		self.update_team_crest('away')
		self.update_team_name('away')
		self.pack_start(self.away_box, True, True, 2)

	def on_fixture_updated(self, *_args):
		self.update_score_label()

	def do_column_box(self):
		box = Gtk.Box()
		box.set_orientation(Gtk.Orientation.VERTICAL)
		box.set_spacing(10)
		box.set_margin_top(10)
		box.set_margin_bottom(10)
		box.set_margin_left(10)
		box.set_margin_right(10)
		box.show()

		return box

	def do_team_box(self, team):
		crest = getattr(self, team + '_crest')
		tname = getattr(self, team + '_name')

		box = self.do_column_box()
		box.pack_start(crest, True, True, 0)
		box.pack_start(tname, True, True, 1)
		box.show()

		return box

	def do_team_name(self):
		label = Gtk.Label('Team Name')
		label.set_max_width_chars(25)
		label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		label.set_margin_left(5)
		label.set_margin_right(5)

		add_widget_class(label, 'team-name')

		return label

	def update_team_name(self, team):
		tname = getattr(self.fixture, team + '_team').name
		label = getattr(self, team + '_name')
		label.set_label(tname)
		label.set_tooltip_text(tname)
		label.show()

	def do_team_crest(self):
		image = image_from_path(path='images/team-emblem.svg')
		image.set_halign(Gtk.Align.CENTER)
		image.set_valign(Gtk.Align.CENTER)

		return image

	def update_team_crest(self, team):
		crest = getattr(self.fixture, team + '_team').crest
		image = getattr(self, team + '_crest')
		image_from_path(path=crest, image=image)
		image.show()

	def do_score_box(self):
		box = self.do_column_box()
		box.pack_start(self.score, True, True, 0)
		box.show()

		return box

	def do_score_label(self):
		label = Gtk.Label('None')
		label.set_justify(Gtk.Justification.CENTER)
		label.set_halign(Gtk.Align.CENTER)
		label.set_valign(Gtk.Align.CENTER)

		add_widget_class(label, 'event-date')

		return label

	def update_score_label(self):
		if getattr(self.fixture, 'past'):
			add_widget_class(self.score, 'event-score')

		if getattr(self.fixture, 'today'):
			add_widget_class(self.score, 'event-today')

		if getattr(self.fixture, 'live'):
			add_widget_class(self.score, 'event-live')

		score = getattr(self.fixture, 'score')
		self.score.set_label(score)
		self.score.show()


class MatchDetailsBox(Gtk.Box):

	__gtype_name__ = 'MatchDetailsBox'

	fixture = GObject.property(type=object, flags=GObject.PARAM_READWRITE)
	callback = GObject.property(type=object, flags=GObject.PARAM_READWRITE)

	def __init__(self, *args, **kwargs):
		Gtk.Box.__init__(self, *args, **kwargs)

		self.fixture = self.get_property('fixture')
		self.callback = self.get_property('callback')

		self.event_count = 0
		self.count_label = self.do_count_label()
		self.available_label = self.do_available_label()
		self.more_button = self.do_more_button()

		self.set_orientation(Gtk.Orientation.HORIZONTAL)
		self.connect('realize', self.on_realized)
		self.connect('notify::fixture', self.on_fixture_updated)

		add_widget_class(self, 'event-item-streams')

		self.show()

	def on_realized(self, *_args):
		self.on_fixture_updated()

		self.pack_start(self.count_label, False, False, 0)
		self.pack_start(self.available_label, False, False, 1)
		self.pack_end(self.more_button, False, False, 2)

	def on_fixture_updated(self, *_args):
		self.event_count = getattr(self.fixture, 'events').count()

		self.update_count_label()
		self.update_more_button()

	def do_available_label(self):
		label = Gtk.Label('Streams available')
		label.set_halign(Gtk.Align.START)
		label.show()

		return label

	def do_count_label(self):
		label = Gtk.Label('0')
		label.set_margin_right(10)

		add_widget_class(label, 'event-item-counter')

		return label

	def update_count_label(self):
		count = str(self.event_count)
		self.count_label.set_label(count)

		if self.event_count == 0:
			add_widget_class(self.count_label, 'no-streams')

		self.count_label.show()

	def do_more_button(self):
		kwargs = { 'icon_name': 'media-playback-start-symbolic', 'size': Gtk.IconSize.BUTTON }
		button = Gtk.Button.new_from_icon_name(**kwargs)

		add_widget_class(button, 'event-item-details')

		return button

	def update_more_button(self):
		self.more_button.connect('clicked', self.on_more_button_clicked, self.fixture)

		if self.event_count == 0:
			self.more_button.set_opacity(0.5)
		else:
			self.more_button.set_opacity(1)

		self.more_button.show()

	def on_more_button_clicked(self, _widget, fixture):
		self.callback(fixture)


class MatchStreamsBox(Gtk.ListBoxRow):

	__gtype_name__ = 'MatchStreamsBox'

	fixture = GObject.property(type=object, flags=GObject.PARAM_READWRITE)
	callback = GObject.property(type=object, flags=GObject.PARAM_READWRITE)

	def __init__(self, *args, **kwargs):
		Gtk.ListBoxRow.__init__(self, *args, **kwargs)

		self.fixture = self.get_property('fixture')
		self.callback = self.get_property('callback')
		self.events = None

		self.connect('realize', self.on_realized)
		self.connect('notify::fixture', self.on_fixture_updated)

		add_widget_class(self, 'stream-item')

		self.show()

	def on_realized(self, *_args):
		self.events = getattr(self.fixture, 'events')
		self.do_fixture_streams()

	def on_fixture_updated(self, *_args):
		self.events = getattr(self.fixture, 'events')
		self.update_fixture_streams()

	def do_nostreams_label(self):
		label = Gtk.Label('No streams available...')
		label.set_margin_top(7)
		label.set_margin_bottom(10)
		label.show()

		add_widget_class(label, 'stream-unknown')

		return label

	def do_fixture_streams(self):
		if self.events.count() == 0:
			label = self.do_nostreams_label()
			self.add(label)

		for event in self.events:
			streambox = StreamBox(stream=event.stream, callback=self.callback, compact=True)
			self.add(streambox)

	def update_fixture_streams(self):
		remove_widget_children(self)
		self.do_fixture_streams()