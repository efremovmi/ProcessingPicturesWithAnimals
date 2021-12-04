from PySimpleGUIQt import *
import datetime
DEFAULT_PROGRESS_BAR_SIZE = (20, 20)
METER_REASON_CANCELLED = 'cancelled'
METER_REASON_CLOSED = 'closed'
METER_REASON_REACHED_MAX = 'finished'
METER_OK = True
METER_STOPPED = False

class QMeter(object):
    active_meters = {}
    exit_reasons = {}

    def __init__(self, title, current_value, max_value, key, *args, orientation='v', bar_color=(None, None),
                         button_color=(None, None), size=DEFAULT_PROGRESS_BAR_SIZE, border_width=None, grab_anywhere=False):
        self.start_time = datetime.datetime.utcnow()
        self.key = key
        self.orientation = orientation
        self.bar_color = bar_color
        self.size = size
        self.grab_anywhere = grab_anywhere
        self.button_color = button_color
        self.border_width = border_width
        self.title = title
        self.current_value = current_value
        self.max_value = max_value
        self.close_reason = None
        self.window = self.BuildWindow(*args)

    def BuildWindow(self, *args):
        layout = []
        if self.orientation.lower().startswith('h'):
            col = [
                *[[T(arg)] for arg in args],
                [T('', size=(70,5), key='_STATS_')],
                [ProgressBar(max_value=self.max_value, orientation='h', key='_PROG_', size=self.size)],[Cancel('Отмена', button_color=self.button_color), Stretch()]  ]
            layout += [Column(col)]
        else:
            col = [[ProgressBar(max_value=self.max_value, orientation='v', key='_PROG_', size=self.size)]]
            col2 = [
                *[[T(arg)] for arg in args],
                [T('', size=(70, 10), key='_STATS_')],[Cancel('Отмена', button_color=self.button_color), Stretch()] ]
            layout += [Column(col), Column(col2)]
        self.window = Window(self.title, grab_anywhere=self.grab_anywhere, border_depth=self.border_width)
        self.window.Layout([layout]).Finalize()

        return self.window

    def UpdateMeter(self, current_value, max_value):
        self.current_value = current_value
        self.max_value = max_value
        self.window.Element('_PROG_').UpdateBar(self.current_value, self.max_value)
        self.window.Element('_STATS_').Update('\n'.join(self.ComputeProgressStats()))
        event, values = self.window.Read(timeout=0)
        if event in('Отмена', None) or current_value >= max_value:
            self.window.Close()
            del(QMeter.active_meters[self.key])
            QMeter.exit_reasons[self.key] = METER_REASON_CANCELLED if event == 'Отмена' else METER_REASON_CLOSED if event is None else METER_REASON_REACHED_MAX
            return QMeter.exit_reasons[self.key]
        return METER_OK


    def ComputeProgressStats(self):
        utc = datetime.datetime.utcnow()
        time_delta = utc - self.start_time
        total_seconds = time_delta.total_seconds()
        if not total_seconds:
            total_seconds = 1
        try:
            time_per_item = total_seconds / self.current_value
        except:
            time_per_item = 1
        seconds_remaining = (self.max_value - self.current_value) * time_per_item
        time_remaining = str(datetime.timedelta(seconds=seconds_remaining))
        time_remaining_short = (time_remaining).split(".")[0]
        time_delta_short = str(time_delta).split(".")[0]
        total_time = time_delta + datetime.timedelta(seconds=seconds_remaining)
        total_time_short = str(total_time).split(".")[0]
        self.stat_messages = [
            '{} из {}'.format(self.current_value, self.max_value),
            '{} %'.format(100 * self.current_value // self.max_value),
            '',
            '{} Пройденное время'.format(time_delta_short),
            '{} Времени осталось'.format(time_remaining_short),
            '{} Суммарное время выполнения'.format(total_time_short)]
        return self.stat_messages


def OneLineProgressMeter(title, current_value, max_value, key, *args, orientation='v', bar_color=(None, None),
                         button_color=None, size=DEFAULT_PROGRESS_BAR_SIZE, border_width=None, grab_anywhere=False):
    if key not in QMeter.active_meters:
        meter = QMeter(title, current_value, max_value, key, *args, orientation=orientation, bar_color=bar_color,
                         button_color=button_color, size=size, border_width=border_width, grab_anywhere=grab_anywhere)
        QMeter.active_meters[key] = meter
    else:
        meter = QMeter.active_meters[key]

    rc = meter.UpdateMeter(current_value, max_value)
    OneLineProgressMeter.exit_reasons = getattr(OneLineProgressMeter,'exit_reasons', QMeter.exit_reasons)
    return rc == METER_OK

def OneLineProgressMeterCancel(key):
    try:
        meter = QMeter.active_meters[key]
        meter.window.Close()
        del(QMeter.active_meters[key])
        QMeter.exit_reasons[key] = METER_REASON_CANCELLED
    except:  # meter is already deleted
        return