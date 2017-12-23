import datetime

class event(object):
    '''
    Data Abstraction that we will use to denote an events
    '''
    def __init__(self, values):
        self.speaker_name = values[0]
        self.event_title = values[1]
        self.speaker_title = values[2]
        self.date = values[3]
        self.time = values[4]
        self.venue = values[5]
        self.web_event_description = values[10]
        self.speaker_bio = values[11]

        #the start and end times of the event as stored as datetime objects
        self.event_start, self.event_end = self.format_date(self.date, self.time)

    def format_date(self, date_str, time_str):
        '''
        Reads in the date and time strings inputted by the user

        Returns datetime objects corresponding to the start and end times of the event
        '''

        date_lst = date_str.split("/")
        time_lst = time_str.split(":")

        #creates our event time
        event_time = datetime.datetime(int(date_lst[2]), int(date_lst[0]), int(date_lst[1]),
            hour=int(time_lst[0]), minute=int(time_lst[1][:2]))

        #handles events being in AM or PM
        t_shift = time_lst[1][2:].strip()
        if t_shift == 'PM' or t_shift == 'P.M.' or t_shift == 'P.M':
            event_time = event_time + datetime.timedelta(hours=12)
        elif t_shift != 'AM' and t_shift != 'A.M.' and t_shift != 'A.M':
            raise SyntaxError ('Please indicate correctly if a time in A.M or P.M')

        #events are one and a half hours long
        start = event_time
        end = event_time+datetime.timedelta(hours=1, minutes = 30)

        return start, end
