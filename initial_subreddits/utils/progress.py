import datetime
import sys
from itertools import cycle

kSpinner = cycle(['-', '\\', '|', '/'])
def init_progbar(total_lines):
    setattr(report_progress, 'total_lines', total_lines)
    setattr(report_progress, 'lines_seen', 0)
    setattr(report_progress, 'prevprogreport', 0) # fraction finished at last report

    starttime = prevtime = nowtime = datetime.datetime.now()
    setattr(report_progress, 'starttime', starttime) # time of execution start
    setattr(report_progress, 'prevtime', prevtime) # time of last time-triggered status report
    setattr(report_progress, 'nowtime', nowtime) # current time
    setattr(report_progress, 'spinchar', kSpinner.next())

kOneTenthSec = datetime.timedelta(0, 0, 1000000/15)
kProgIncrement = 0.0001
kBarLen = 20
def report_progress():
    global kOneSec
    global kProgIncrement
    report_progress.lines_seen += 1
    report_progress.nowtime = datetime.datetime.now()

    progress = float(report_progress.lines_seen)/report_progress.total_lines

    exec_t = report_progress.nowtime - report_progress.starttime
    delta_t = report_progress.nowtime - report_progress.prevtime

    # If we have progressed by 0.01% since last report, or if 0.1s has passed, update progbar
    if progress - report_progress.prevprogreport >= kProgIncrement or delta_t >= kOneTenthSec or progress >= 1:
        nbars = int(kBarLen * progress)
        if delta_t >= kOneTenthSec:
            report_progress.prevtime = report_progress.nowtime
            report_progress.spinchar = kSpinner.next()
        if progress == 1:
            report_progress.spinchar = ''
        nspaces = kBarLen - nbars - len(report_progress.spinchar)

        percentage = '({0:6.2f}%)'.format(100 * progress)

        days = exec_t.days
        seconds = exec_t.seconds
        hours = seconds//3600; seconds -= 3600*hours
        minutes = seconds/60; seconds -= 60*minutes
        timestr = '({0}:{1}:{2}:{3})'.format(days, str(hours).zfill(2), str(minutes).zfill(2), 
                                             str(seconds).zfill(2))
        
        sys.stdout.write('\r')
        sys.stdout.write('Progress: [{0}{1}{2}] {3} {4}'.format('=' * nbars, report_progress.spinchar, ' ' * nspaces, percentage, timestr))
        sys.stdout.flush()

        report_progress.prevprogreport = round(progress, 4)    


def report_finished():
    sys.stdout.write('\r')
    sys.stdout.write('Progress: [{0}] (100.00%)'.format('=' * kBarLen))
    sys.stdout.flush()
    print('')
