# door_notifications.py

import appdaemon.appapi as appapi

#
# App to send notification when a door left open for too long
#
# Args: (set these in appdaemon.cfg)
# ttl = # of seconds to wait until notified
#
#
# EXAMPLE appdaemon.cfg entry below
# 
# # Apps
# 
# [door_notifications]
# module = door_notifications
# class = DoorMonitor
# ttl = 15
#

class DoorMonitor(appapi.AppDaemon):

    def initialize(self):
        self.door_entities = ['binary_sensor.door_sensor1', 'binary_sensor.door_sensor2', 
                              'binary_sensor.door_sensor3', 'binary_sensor.door_sensor4']

        self.door_timer_library = {}

        for door in self.door_entities:
            self.listen_state(self.tracker, entity=door)

    def tracker(self, entity, attribute, old, new, kwargs):
        try:
            self.cancel_timer(self.door_timer_library[entity])
        except KeyError:
            self.log('Tried to cancel a timer for {}, but none existed!'.format(entity), 
                     level='DEBUG')

        if new == 'on':
            self.door_timer_library[entity] = self.run_in(self.notifier, 
                                                          seconds=int(self.args['ttl']), 
                                                          entity_name=entity)

    def notifier(self, kwargs):
        friendly_name = self.get_state(kwargs['entity_name'], attribute='friendly_name')

        title = "Message from HASS!"
        message = "{} has been open for more than {} seconds.".format(friendly_name,
                                                                      self.args['ttl'])

        self.call_service('notify/notify', title=title, message=message)
