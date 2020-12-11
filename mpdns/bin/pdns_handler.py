import splunk.admin as admin

# If no default value is specified, use ""
fields = {
    "api_url": {},
    "api_key": {},
    "proxy": {},
}


class ConfigApp(admin.MConfigHandler):
    """
    Set up supported arguments
    """

    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            for field in fields:
                self.supportedArgs.addOptArg(field)

    """
    Read the initial values of the parameters from the custom file
    pdns.conf, and write them to the setup page.

    If the app has never been set up,
    use .../app_name/default/pdns.conf.

    If app has been set up, looks at
    .../local/pdns.conf first, then looks at
    .../default/pdns.conf only if there is no value for a field in
    .../local/pdns.conf

    For text fields, if the conf file says None, set to the empty string.
    """

    def handleList(self, confInfo):
        confDict = self.readConf("pdns")
        if confDict is not None:
            for stanza, settings in confDict.items():
                for key, val in settings.items():
                    if not val:
                        val = fields[key].get("default", "")
                    confInfo[stanza].append(key, val)

    def handleEdit(self, confInfo):
        """
        After user clicks Save on setup page, take updated parameters,
        normalize them, and save them somewhere
        """

        name = self.callerArgs.id
        args = self.callerArgs

        for field in fields:
            if not self.callerArgs.data[field][0]:
                self.callerArgs.data[field][0] = fields[field].get("default", "")

        """
        Since we are using a conf file to store parameters,
        write them to the [config] stanza in pdns/local/pdns.conf
        """

        self.writeConf("pdns", "config", self.callerArgs.data)


# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)
