import time, datetime
from socket import timeout
import sys
from decorator import decorator

from dogapi.common import SharedCounter

from v1 import *

class SimpleClient(object):
    """
    A high-level client for interacting with the Datadog API.
    """

    def __init__(self):
        self.api_key = None
        self.application_key = None
        self.max_timeouts = 3
        self.timeout_counter = SharedCounter()
        self.swallow = True

    @decorator
    def _swallow_exceptions(f, self, *args, **kwargs):
        if self.swallow is True:
            try:
                return f(self, *args, **kwargs)
            except Exception, e:
                self._report_error(str(e))
        else:
            return f(self, *args, **kwargs)

    def _report_error(self, message):
        if self.swallow:
            print >> sys.stderr, message
        else:
            raise Exception(message)

    #
    # Metric API

    @_swallow_exceptions
    def metric(self, name, value, host=None, device=None):
        """
        Submit a single data point to the metric API.

        :param name: name of the metric (e.g. ``"system.load.1"``)
        :type name: string

        :param value: data point value
        :type value: numeric

        :param host: optional host to scope the metric (e.g. ``"hostA.example.com"``)
        :type host: string

        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :raises: Exception on failure
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Metric API requires api and application keys")
        s = MetricService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        now = time.mktime(datetime.datetime.now().timetuple())
        r = s.post(name, [[now, value]], host=host, device=device)
        if r.has_key('errors'):
            self._report_error(r['errors'])

    @_swallow_exceptions
    def metrics(self, name, values, host=None, device=None):
        """
        Submit a series of data points to the metric API.

        :param name: name of the metric (e.g. ``"system.load.1"``)
        :type name: string

        :param values: data series. list of (POSIX timestamp, intever value) tuples. (e.g. ``[(1317652676, 15), (1317652706, 18), ...]``)
        :type values: list

        :param host: optional host to scope the metric (e.g. ``"hostA.example.com"``)
        :type host: string

        :param device: optional device to scope the metric (e.g. ``"eth0"``)
        :type device: string

        :raises: Exception on failure
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Metric API requires api and application keys")
        s = MetricService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        if device:
            r = s.post(name, values, host=host, device=device)
        else:
            r = s.post(name, values, host=host)
        if r.has_key('errors'):
            self._report_error(r['errors'])

    #
    # Comment API

    @_swallow_exceptions
    def comment(self, handle, message, comment_id=None, related_event_id=None):
        """
        Post or edit a comment.

        :param handle: user handle to post the comment as
        :type handle: string

        :param message: comment message
        :type message: string

        :param comment_id: if set, comment will be updated instead of creating a new comment
        :type comment_id: integer

        :param related_event_id: if set, comment will be posted as a reply to the specified comment or event
        :type related_event_id: integer

        :return: comment id
        :rtype: integer

        :raises:  Exception on failure
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Comment API requires api and application keys")
        s = CommentService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        if comment_id is None:
            r = s.post(handle, message, related_event_id)
        else:
            r = s.edit(comment_id, handle, message, related_event_id)
        if r.has_key('errors'):
            self._report_error(r['errors'])
        return r['comment']['id']

    @_swallow_exceptions
    def delete_comment(self, comment_id):
        """
        Delete a comment.

        :param comment_id: comment to delete
        :type comment_id: integer

        :raises: Exception on error
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Comment API requires api and application keys")
        s = CommentService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.delete(comment_id)
        if r.has_key('errors'):
            self._report_error(r['errors'])

    #
    # Cluster API

    @_swallow_exceptions
    def all_clusters(self):
        """
        Get a list of clusters for your org and their member hosts.

        :return: [ { 'cluster1': [ 'host1', 'host2', ... ] }, ... ]
        :rtype: list
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Cluster API requires api and application keys")
        s = ClusterService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.get_all()
        if r.has_key('errors'):
            self._report_error(r['errors'])
        return r['clusters']

    @_swallow_exceptions
    def host_clusters(self, host_id):
        """
        Get a list of clusters for the specified host by name or id.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :return: clusters the host belongs to
        :rtype: list
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Cluster API requires api and application keys")
        s = ClusterService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.get(host_id)
        if r.has_key('errors'):
            self._report_error(r['errors'])
        return r['clusters']

    @_swallow_exceptions
    def add_clusters(self, host_id, *args):
        """add_clusters(host_id, cluster1, [cluster2, [...]])
        Add a host to one or more clusters.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param clusterN: cluster name
        :type clusterN: string
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Cluster API requires api and application keys")
        s = ClusterService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.add(host_id, args)
        if r.has_key('errors'):
            self._report_error(r['errors'])

    @_swallow_exceptions
    def change_clusters(self, host_id, *args):
        """change_clusters(host_id, cluster1, [cluster2, [...]])
        Remove a host from all existing clusters and add it to one or more new clusters.

        :param host_id: id or name of the host
        :type host_id: integer or string

        :param clusterN: cluster name
        :type clusterN: string
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Cluster API requires api and application keys")
        s = ClusterService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.update(host_id, args)
        if r.has_key('errors'):
            self._report_error(r['errors'])

    @_swallow_exceptions
    def detatch_clusters(self, host_id):
        """
        Remove a host from all clusters.

        :param host_id: id or name of the host
        :type host_id: integer or string
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Cluster API requires api and application keys")
        s = ClusterService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.detatch(host_id)
        if r.has_key('errors'):
            self._report_error(r['errors'])

    #
    # Stream API

    @_swallow_exceptions
    def stream(self, start, end, priority=None, sources=None, tags=None):
        """
        Get an event stream, optionally filtered.

        :param start: start date for the stream query (POSIX timestamp)
        :type start: integer

        :param end: end date for the stream query (POSIX timestamp)
        :type end: integer

        :param priority: show only events of the given priority ("low" or "normal")
        :type priority: string

        :param sources: show only events for the give sources (see
                        https://github.com/DataDog/dogapi/wiki/Event
                        for an up-to-date list of available sources)
        :type sources: list of strings

        :param tags: show only events for the given tags
        :type tags: list of strings

        :return: list of events (see https://github.com/DataDog/dogapi/wiki/Event for structure)
        :rtype: decoded JSON
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Event API requires api and application keys")
        s = EventService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.query(start, end, priority, sources, tags)
        if r.has_key('errors'):
            self._report_error(r['errors'])
        return r['events']

    @_swallow_exceptions
    def get_event(self, id):
        """
        Get details for an individual event.

        :param id: numeric event id
        :type id: integer

        :return: event details (see https://github.com/DataDog/dogapi/wiki/Event for structure)
        :rtype: decoded JSON
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Event API requires api and application keys")
        s = EventService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.get(id)
        if r.has_key('errors'):
            self._report_error(r['errors'])
        return r['event']

    @_swallow_exceptions
    def event(self, title, text, date_happened=None, handle=None, priority=None, related_event_id=None, tags=None):
        """
        Post an event.

        :param title: title for the new event
        :type title: string

        :param text: event message
        :type text: string

        :param date_happened: when the event occurred. if unset defaults to the current time. (POSIX timestamp)
        :type date_happened: integer

        :param handle: user to post the event as. defaults to owner of the application key used to submit.
        :type handle: string

        :param priority: priority to post the event as. ("normal" or "low", defaults to "normal")
        :type priority: string

        :param related_event_id: post event as a child of the given event
        :type related_event_id: id

        :param tags: tags to post the event with
        :type tags: list of strings

        :return: new event id
        :rtype: integer
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Event API requires api and application keys")
        s = EventService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.post(title, text, date_happened, handle, priority, related_event_id, tags)
        if r.has_key('errors'):
            self._report_error(r['errors'])
        return r['event']['id']

    #
    # Dash API

    @_swallow_exceptions
    def dashboard(self, dash_id):
        """
        Get a dashboard definition.

        :param dash_id: id of the dash to get
        :type dash_id: integer

        :return: dashboard definition (see https://github.com/DataDog/dogapi/wiki/Dashboard for details)
        :rtype: decoded JSON
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
        s = DashService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.get(dash_id)
        if r.has_key('errors'):
            self._report_error(r['errors'])
        return r['dash']

    @_swallow_exceptions
    def create_dashboard(self, title, description, graphs):
        """
        Create a new dashboard.

        :param title: tile for the new dashboard
        :type title: string

        :param description: description of the new dashboard
        :type description: string

        :param graphs: list of graph objects for the dashboard (same format as contained in the dashboard object returned by :meth:`~dogapi.SimpleClient.dashboard`)
        :type graphs: decoded JSON

        :return: new dashboard's id
        :rtype: integer
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
        s = DashService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.create(title, description, graphs)
        if r.has_key('errors'):
            self._report_error(r['errors'])
        return r['dash']['id']

    @_swallow_exceptions
    def update_dashboard(self, dash_id, title, description, graphs):
        """
        Update an existing dashboard.

        :param dash_id: dash to update
        :type dash_id: integer

        :param title: new tile for the dashboard
        :type title: string

        :param description: new description for the dashboard
        :type description: string

        :param graphs: list of graph objects for the dashboard (same format as contained in the dashboard object returned by :meth:`~dogapi.SimpleClient.dashboard`). replaces existing graphs.
        :type graphs: decoded JSON

        :return: dashboard's id
        :rtype: integer
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
        s = DashService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.update(dash_id, title, description, graphs)
        if r.has_key('errors'):
            self._report_error(r['errors'])
        return r['dash']['id']

    @_swallow_exceptions
    def delete_dashboard(self, dash_id):
        """
        Delete a dashboard.

        :param dash_id: dash to delete
        :type dash_id: integer
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Dash API requires api and application keys")
        s = DashService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.delete(dash_id)
        if r.has_key('errors'):
            self._report_error(r['errors'])

    #
    # Search API

    @_swallow_exceptions
    def search(self, query):
        """
        Search datadog for hosts and metrics by name.

        :param query: search query can either be faceted to limit the results (e.g. ``"host:foo"``, or ``"metric:bar"``) or un-faceted, which will return results of all types (e.g. ``"baz"``)
        :type query: string

        :return: a dictionary maping each queried facet to a list of name strings
        :rtype: dictionary
        """
        if self.timeout_counter.counter >= self.max_timeouts:
            return None
        if self.api_key is None or self.application_key is None:
            self._report_error("Search API requires api and application keys")
        s = SearchService(self.api_key, self.application_key, timeout_counter=self.timeout_counter)
        r = s.query(query)
        if r.has_key('errors'):
            self._report_error(r['errors'])
        return r['results']
