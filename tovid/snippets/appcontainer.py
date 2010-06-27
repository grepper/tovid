import commands
import shlex
from Tkinter import *
from subprocess import Popen, PIPE
from tkMessageBox import *
from sys import argv
from os import path, mkfifo
from tempfile import mkdtemp
import time

class AppContainer(Frame):
    """A frame container for an external application.
       master: the container frame will be packed into this widget
       height: the height of the application
       width:  the width of the application
       callback: called on application exit (AppContainer is 'destroyed' then)

       After creating a container instance, call container.get_id()
       to find out the X11 id of the container(ie. for xterm -into id)
       Then call container.run(command), where command is the command
       that starts the external app.
       This file can be run standalone, and uses the example at the bottom
    """       
    
    def __init__(self, master, width, height, callback=None):
        Frame.__init__(self, master)
        self.master = master
        self.width = width 
        self.height = height
        self.callback = callback
        self.is_running = BooleanVar()
        self.is_running.set(False)
        self.draw()

    def draw(self):
        """Pack self in self.master"""
        self.pack(fill='both', expand=1)

    def get_id(self):
        """Create and pack container frame,
           then get X11 identifier for it (converted to base 10).
           Return the identifier
        """
        self.frame = Frame(self.master, container=1, borderwidth=1,
                              width=self.width, height=self.height)
        id = self.tk.call('winfo', 'id', self.frame)
        self.frame_id = '%s' %int(id, 16)
        return self.frame_id

    def run(self, command):
        """Execute self.command, call the callback from self.master"""
        self.is_running.set(True)
        self.frame.pack()
        cmd = Popen(command, stderr=PIPE, stdout=PIPE)
        self.after(200, self.poll())
        self.callback()

    def poll(self):
        """When the container app stops running, call callback from self.master"""
        # only poll if app still running
        if self.is_running.get() == 1:
            if not self.tk.call('winfo', 'exists', self.frame):
                self.is_running.set(False)
                # call function in master when app exits
                if self.callback:
                    self.callback()
            self.after(200, self.poll)


###############################################################################
#                      demo of AppContainer with xterm                        #
###############################################################################
if __name__ == '__main__':

    def demo(app):
        def callback():
            """Called upon creation and exiting of container app,
               Set a BooleanVar() to track whether the app is running.
            """
            if container.is_running.get() == True:
                app_is_running.set(True)
                
            else:
                app_is_running.set(False)
                root_frame.pack_forget()
                label.pack(side='top', fill='both', expand=1)
                label.configure(text='application has exited')
                button.pack(side='bottom')

        def execute():
            label.pack_forget()
            button.pack_forget()
            root_frame.pack(fill='both', expand=1)
            xid = container.get_id()
            font = '-misc-fixed-medium-r-normal--13-100-100-100-c-70-iso8859-1'
            if app == 'xterm':
                geometry = '80x40+0+0'
                command = 'xterm -geometry %s -fn %s  -into %s &' \
                  %(geometry, font, xid)

            elif app == 'mplayer':
                def send_command(text):
                    cmd = commands.getstatusoutput('echo %s > %s' %(text, cmd_pipe))
                    #pipe =  open(cmd_pipe, 'w')
                    #pipe.write(text)
                    #pipe.close()
 
                def set_chapter(event=None):
                    send_command('edl_mark')

                def exit_mplayer():
                    # send bogus edl command so mplayer sends last edl_mark 
                    send_command('edl_mark')
                    # send quit and destroy frame
                    send_command('quit')
                    container.frame.destroy()
                    # need a sleep to make sure mplayer gives up its data
                    time.sleep(1)
                    f = open(editlist)
                    c = f.read()
                    f.close()
                    # convert text from opened file to HH:MM:SS
                    times = [ float(t) for t in shlex.split(c) if not t == '0' ]
                    # remove bogus edl_mark
                    times.pop(-1)
                    # insert mandatory 1st chapter
                    times.insert(0, 0.0)
                    chapters = []
                    for t in times:
                        chapters.append(time.strftime('%H:%M:%S', time.gmtime(t)))
                    time_codes = "'%s'" %','.join(chapters)
                    print '-chapters %s' %time_codes

                dir = mkdtemp(prefix='tovid-')
                cmd_pipe = path.join(dir, 'slave.fifo')
                mkfifo(cmd_pipe)
                editlist = path.join(dir, 'editlist')
                command = 'mplayer -nomouseinput -xy 400 \
                -slave -input file=%s -edlout  \
                %s -wid %s %s > /tmp/mplayer.log 2>&1' %(cmd_pipe, editlist, xid, media_file)
                but_frame = Frame(root_frame)
                but_frame.pack(side='bottom')
                b1 = Button(but_frame, command=set_chapter, text='set chapter')
                b1.pack(side='left')
                b2 = Button(but_frame, command=exit_mplayer, text='Exit')
                b2.pack(side='left')
                
            command = shlex.split(command)
            print ' '.join(command)
            container.frame.configure(width=600, height=450)
            container.run(command)

        def confirm_exit():
            if app_is_running.get() == 1:
                if app == 'xterm':
                    text = "Close the xterm by typing 'exit', before exiting this demo"
                elif app == 'mplayer':
                    text = "Close mplayer first, before exiting this demo"
                showerror(message=text)
                return
            quit()


        root = Tk()
        root.minsize(660, 600)
        # bindings for exit
        root.protocol("WM_DELETE_WINDOW", confirm_exit)
        root.bind('<Control-q>', confirm_exit)
        root.title('AppContainer demo')
        # run button
        button = Button(root, text='Run application', command=execute)
        button.pack(side='bottom')
        # frame for container
        root_frame = Frame(root)
        # label to show when container app not running
        label = Label(root, text='')
        # BooleanVar that tracks if container app is running through callback()
        app_is_running = BooleanVar()
        app_is_running.set(False)
        # initialize but don't pack the container class
        container = AppContainer(root_frame, 640, 480, callback)
        try:
            root.mainloop()
        except KeyboardInterrupt:
            print 'KeyboardInterrupt'
    if len(argv) < 2:
        demo('xterm')
    # setting chapters with mplayer demo - coming soon
    elif path.exists(argv[1]):
        media_file = argv[1]
        demo('mplayer')
