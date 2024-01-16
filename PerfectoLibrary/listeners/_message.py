class Messages(object):

    def _get_json_file(self):
        return self.JsonFile

    def _set_json_file(self, json_file):
        self.json_file = json_file

    def _get_custom_error(self):
        return self.custom_error

    def _set_custom_error(self, custom_error):
        self.custom_error = custom_error

    def _get_stack_trace_errors(self):
        return self.stack_trace_errors

    def _set_stack_trace_errors(self, error):
        self.stack_trace_errors = error

    def _get_custom_fields(self):
        return self.custom_fields

    def _set_custom_fields(self, custom_fields):
        self.custom_fields = custom_fields

    def _get_tags(self):
        return self.tags

    def _set_tags(self, tags):
        self.tags = tags
