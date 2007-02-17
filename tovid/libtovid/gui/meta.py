#! /usr/bin/env python
# meta.py

"""This module defines several Tkinter "meta widgets".
"""

__all__ = [
    'Metawidget',
    'Choice',
    'Color',
    'Filename',
    'Flag',
    'Font',
    'Text',
    'List',
    'Number',
    'Optional',
    'OptionFrame',
    'PlainLabel',
    'Panel',
    'Application']

import os
import shlex
from libtovid import log
# Tkinter
import Tkinter as tk
import tkFileDialog
import tkColorChooser
import tkSimpleDialog

### --------------------------------------------------------------------
### Custom widgets
### --------------------------------------------------------------------

class Metawidget (tk.Frame):
    """A base class for extended special-purpose widgets.

    A Metawidget may contain any number of other widgets, and store a
    single variable value. Presumably, a subclass will link self.variable
    to one or more control widgets, via the variable/textvariable attribute.
    
    See the Metawidget subclasses below for examples of how self.variable,
    get() and set() are used.
    """
    def __init__(self, master=None, vartype=str):
        """Create a Metawidget with the given master and variable type.

            master:   Tkinter widget that will contain this Metawidget
            vartype:  Type of stored variable (str, bool, int, float, list)
        """
        tk.Frame.__init__(self, master)
        vartypes = {
            str: tk.StringVar,
            bool: tk.BooleanVar,
            int: tk.IntVar,
            float: tk.DoubleVar,
            list: tk.Variable}
        # Create an appropriate Tkinter variable type
        if vartype in vartypes:
            self.variable = vartypes[vartype]()
        # Or use a generic Variable
        else:
            self.variable = tk.Variable()

    def get(self):
        """Return the value of the Metawidget's variable."""
        return self.variable.get()

    def set(self, value):
        """Set the Metawidget's variable to the given value."""
        self.variable.set(value)

    def enable(self, enabled=True):
        """Enable or disable all sub-widgets."""
        if enabled:
            newstate = 'normal'
        else:
            newstate = 'disabled'
        for widget in self.children.values():
            widget.config(state=newstate)

    def disable(self):
        """Disable all sub-widgets."""
        self.enable(False)


### --------------------------------------------------------------------

class Flag (Metawidget):
    """A widget for controlling a yes/no value."""
    def __init__(self,
                 master=None,
                 label="Debug",
                 default=False):
        """Create a Flag widget with the given label and default value.

            master:   Tkinter widget that will contain this Flag
            label:    Text label for the flag
            default:  Default value (True or False)
        """
        Metawidget.__init__(self, master, bool)
        self.variable.set(default)
        # Create and pack widgets
        self.check = tk.Checkbutton(self, text=label, variable=self.variable)
        self.check.pack(side='left')

### --------------------------------------------------------------------

class Choice (Metawidget):
    """A widget for choosing one of several options.
    """
    def __init__(self,
                 master=None,
                 label="Choices",
                 choices='A|B',
                 default=None):
        """Initialize Choice widget with the given label and list of choices.

            master:   Tkinter widget that will contain this Choice
            label:    Text label for the choices
            choices:  Available choices, in string form: 'one|two|three'
                      or list form: ['one', 'two', 'three']
            default:  Default choice, or None to use first choice in list
        """
        # TODO: Allow alternative choice styles (listbox, combobox?)
        Metawidget.__init__(self, master, str)
        # If choices is a string, split on '|'
        if type(choices) == str:
            choices = choices.split('|')
        # Use first choice if default wasn't provided
        if default is None:
            default = choices[0]
        self.variable.set(default)
        # Create and pack widgets
        self.label = tk.Label(self, text=label)
        self.label.pack(side='left')
        self.rb = {}
        for choice in choices:
            self.rb[choice] = tk.Radiobutton(self, text=choice, value=choice,
                                             variable=self.variable)
            self.rb[choice].pack(side='left')

### --------------------------------------------------------------------

class Number (Metawidget):
    """A widget for choosing or entering a number"""
    def __init__(self,
                 master=None,
                 label="Number",
                 min=1,
                 max=10,
                 style='spin',
                 default=None):
        """Create a number-setting widget.
        
            master:   Tkinter widget that will contain this Number
            label:    Text label describing the meaning of the number
            min, max: Range of allowable numbers (inclusive)
            style:    'spin' for a spinbox, or 'scale' for a slider
            default:  Default value, or None to use minimum
        """
        # TODO: Multiple styles (entry, spinbox, scale)
        Metawidget.__init__(self, master, int)
        self.style = style
        # Use min if default wasn't provided
        if default is None:
            default = min
        self.variable.set(default)
        # Create and pack widgets
        self.label = tk.Label(self, name='label', text=label)
        self.label.pack(side='left')
        if self.style == 'spin':
            self.number = tk.Spinbox(self, from_=min, to=max, width=4,
                                     textvariable=self.variable)
            self.number.pack(side='left')
        else: # 'scale'
            self.number = tk.Scale(self, from_=min, to=max,
                                   tickinterval=max-min,
                                   variable=self.variable, orient='horizontal')
            self.number.pack(side='left', fill='x', expand=True)

    def enable(self, enabled=True):
        """Enable or disable all sub-widgets. Overridden to make Scale widget
        look disabled."""
        Metawidget.enable(self, enabled)
        if self.style == 'scale':
            if enabled:
                self.number['fg'] = 'black'
                self.number['troughcolor'] = 'white'
            else:
                self.number['fg'] = '#A3A3A3'
                self.number['troughcolor'] = '#D9D9D9'
                

### --------------------------------------------------------------------

class Text (Metawidget):
    """A widget for entering a line of text"""
    def __init__(self,
                 master=None,
                 label="Text",
                 default=''):
        Metawidget.__init__(self, master, str)
        self.variable.set(default)
        # Create and pack widgets
        self.label = tk.Label(self, text=label, justify=tk.LEFT)
        self.entry = tk.Entry(self, textvariable=self.variable)
        self.label.pack(side='left')
        self.entry.pack(side='left', fill='x', expand=True)

### --------------------------------------------------------------------

class List (Text):
    """A widget for entering a space-separated list of text items"""
    def __init__(self,
                 master=None,
                 label="List",
                 default=''):
        Text.__init__(self, master, label, default)

    def get(self):
        """Split text into a list at whitespace boundaries."""
        text = Text.get(self)
        return shlex.split(text)

    def set(self, listvalue):
        """Set a value to a list, joined with spaces."""
        text = ' '.join(listvalue)
        Text.set(self, text)

### --------------------------------------------------------------------

class Filename (Metawidget):
    """A widget for entering or browsing for a filename
    """
    def __init__(self,
                 master=None,
                 label='Filename',
                 type='load',
                 desc='Select a file to load',
                 default=''):
        """Create a Filename with label, text entry, and browse button.
        
            master:  Tkinter widget that will contain the FileEntry
            label:   Text of label next to file entry box
            type:    Do you intend to 'load' or 'save' this file?
            desc:    Brief description (shown in title bar of file
                     browser dialog)
            default: Default filename
        """
        Metawidget.__init__(self, master, str)
        self.variable.set(default)
        self.type = type
        self.desc = desc
        # Create and pack widgets
        self.label = tk.Label(self, text=label, justify='left')
        self.entry = tk.Entry(self, textvariable=self.variable)
        self.button = tk.Button(self, text="Browse...", command=self.browse)
        self.label.pack(side='left')
        self.entry.pack(side='left', fill='x', expand=True)
        self.button.pack(side='left')

    def browse(self, event=None):
        """Event handler when browse button is pressed"""
        if self.type == 'save':
            filename = tkFileDialog.asksaveasfilename(parent=self,
                                                      title=self.desc)
        else: # 'load'
            filename = tkFileDialog.askopenfilename(parent=self,
                                                    title=self.desc)
        # Got a filename? Save it
        if filename:
            self.set(filename)

### --------------------------------------------------------------------

class Color (Metawidget):
    """A widget for choosing a color"""
    def __init__(self,
                 master=None,
                 label="Color",
                 default=''):
        """Create a widget that opens a color-chooser dialog.
        
            master:  Tkinter widget that will contain the ColorPicker
            label:   Text label describing the color to be selected
            default: Default color (named color or hexadecimal RGB)
        """
        Metawidget.__init__(self, master, str)
        self.variable.set(default)
        # Create and pack widgets
        self.label = tk.Label(self, text=label)
        self.button = tk.Button(self, text="None", command=self.change)
        self.label.pack(side='left')
        self.button.pack(side='left')
        
    def change(self):
        """Choose a color, and set the button's label and color to match."""
        rgb, color = tkColorChooser.askcolor(self.get())
        if color:
            self.set(color)
            self.button.config(text=color, foreground=color)
    
### --------------------------------------------------------------------

class FontChooser (tkSimpleDialog.Dialog):
    """A widget for choosing a font"""
    def __init__(self, master=None):
        tkSimpleDialog.Dialog.__init__(self, master, "Font chooser")

    def get_fonts(self):
        """Return a list of font names available in ImageMagick."""
        find = "convert -list type | sed '/Path/,/---/d' | awk '{print $1}'"
        return [line.rstrip('\n') for line in os.popen(find).readlines()]

    def body(self, master):
        """Draw widgets inside the Dialog, and return the widget that should
        have the initial focus. Called by the Dialog base class constructor.
        """
        self.fontlist = ScrollList(master, "Available fonts",
                                   self.get_fonts())
        self.fontlist.pack(fill='both', expand=True)
        return self.fontlist
    
    def apply(self):
        """Set the selected font.
        """
        self.result = self.fontlist.selected.get()


class Font (Metawidget):
    """A font selector widget"""
    def __init__(self, master=None, label='Font', default='Helvetica'):
        """Create a widget that opens a font chooser dialog.
        
            master:  Tkinter widget that will contain this Font
            label:   Text label for the font
            default: Default font
        """
        Metawidget.__init__(self, master, str)
        self.label = tk.Label(self, text=label)
        self.label.pack(side='left')
        self.button = tk.Button(self, textvariable=self.variable,
                             command=self.choose)
        self.button.pack(side='left', padx=8)
        self.variable.set(default)

    def choose(self):
        """Open a font chooser to select a font."""
        chooser = FontChooser()
        if chooser.result:
            self.variable.set(chooser.result)

### --------------------------------------------------------------------

class Optional (tk.Frame):
    """Container that shows/hides an optional Metawidget"""
    def __init__(self,
                 master=None,
                 widget=None,
                 label='Option',
                 *args):
        """Create an Optional widget.

            master:  Tkinter widget that will contain the Optional
            widget:  A Metawidget to show or hide
            label:   Label for the optional widget
        """
        tk.Frame.__init__(self, master)
        self.active = tk.BooleanVar()
        # Create and pack widgets
        self.check = tk.Checkbutton(self, text=label, variable=self.active,
                                    command=self.showHide, justify='left')
        self.check.pack(side='left')
        self.widget = widget(self, '', *args)
        self.widget.pack(side='left', expand=True, fill='x')
        self.widget.disable()
        self.active.set(False)
    
    def showHide(self):
        """Show or hide the sub-widget."""
        if self.active.get():
            self.widget.enable()
        else:
            self.widget.disable()

    def get(self):
        """Return the sub-widget's value if active, or None if inactive."""
        if self.active.get():
            return self.widget.get()
        else:
            return None
    
    def set(self, value):
        """Set sub-widget's value."""
        self.widget.set(value)

### --------------------------------------------------------------------

class OptionFrame (tk.Frame):
    """A Frame containing Metawidgets that control command-line options.
    """
    def __init__(self, master=None):
        """Create an OptionFrame with the given master and control widgets.

            master:  Tkinter widget that will contain this OptionFrame
            args:    Positional arguments to pass to Frame constructor
            kwargs:  Keyword arguments to pass to Frame constructor
        """
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.controls = {}

    def add(self, option, widget):
        """Add a widget controlling the given option.
        """
        assert isinstance(widget, tk.Widget)
        self.controls[option] = widget
        
    def get(self, option):
        """Get the value of the given option from its associated widget.
        """
        return self.controls[option].get()

    def set(self, option, value):
        """Set the value of the widget associated with the given option.
        """
        self.controls[option].set(value)

    def arglist(self):
        """Return a list of command-line arguments for all options.
        """
        args = []
        for option, widget in self.controls.items():
            value = widget.get()
            # Boolean values control a flag
            if value == True:
                args.append("-%s" % option)
            # All others use '-option value'
            elif value:
                args.append("-%s" % option)
                args.append(value)
        return args

### --------------------------------------------------------------------

class PlainLabel (Metawidget):
    """A plain label or spacer widget"""
    def __init__(self,
                 master=None,
                 label="Text",
                 default=''):
        Metawidget.__init__(self, master, str)
        self.variable.set(default)
        # Create and pack widgets
        self.label = tk.Label(self, text=label)
        self.label.pack(side='left')

### --------------------------------------------------------------------
### Not exported yet
### --------------------------------------------------------------------

class ScrollList (Metawidget):
    """A widget for choosing from a list of values
    """
    def __init__(self, master=None, label="List", values=None):
        """Create a ScrollList widget.
        
            master:    Tkinter widget that will contain this ScrollList
            label:     Text label for the list
            values:    List of initial values
        """
        Metawidget.__init__(self, master, list)
        self.selected = tk.StringVar() # Currently selected list item
        # Listbox label
        self.label = tk.Label(self, text=label)
        self.label.pack(anchor=tk.W)
        # Group listbox and scrollbar together
        group = tk.Frame(self)
        self.scrollbar = tk.Scrollbar(group, orient='vertical',
                                      command=self.scroll)
        self.listbox = tk.Listbox(group, width=30, listvariable=self.variable,
                                  yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='left', fill='y', expand=True)
        group.pack()
        self.listbox.bind('<Button-1>', self.select)
        if values:
            self.add(*values)

    def add(self, *values):
        """Add the given values to the list."""
        for value in values:
            self.listbox.insert('end', value)

    def scroll(self, *args):
        """Event handler when the list is scrolled
        """
        apply(self.listbox.yview, args)

    def select(self, event):
        """Event handler when an item in the list is selected
        """
        self.curindex = self.listbox.nearest(event.y)
        self.selected.set(self.listbox.get(self.curindex))

### --------------------------------------------------------------------

class DragList (ScrollList):
    """A scrollable listbox with drag-and-drop support"""
    def __init__(self, master=None, label="List", values=None):
        ScrollList.__init__(self, master, label, values)
        self.listbox.bind('<Button-1>', self.select)
        self.listbox.bind('<B1-Motion>', self.drag)
        self.listbox.bind('<ButtonRelease-1>', self.drop)
        self.curindex = 0

    def select(self, event):
        """Event handler when an item in the list is selected.
        """
        # Set currently selected item and change the cursor to a double-arrow
        ScrollList.select(self, event)
        self.config(cursor="double_arrow")
    
    def drag(self, event):
        """Event handler when an item in the list is dragged
        """
        # If item is dragged to a new location, delete/insert
        loc = self.listbox.nearest(event.y)
        if loc != self.curindex:
            item = self.listbox.get(self.curindex)
            self.listbox.delete(self.curindex)
            self.listbox.insert(loc, item)
            self.curindex = loc

    def drop(self, event):
        """Event handler when an item in the list is "dropped"
        """
        # Change the mouse cursor back to the default arrow.
        self.config(cursor="")

### --------------------------------------------------------------------

class FileList (DragList):
    """A widget for listing several filenames"""
    def __init__(self, master=None, label="File list", files=None):
        DragList.__init__(self, master, label, files)
        # Group Add/Remove buttons
        group = tk.Frame(self)
        self.add = tk.Button(group, text="Add...", command=self.addFiles)
        self.remove = tk.Button(group, text="Remove", command=self.removeFiles)
        self.add.pack(side='left', fill='x', expand=True)
        self.remove.pack(side='left', fill='x', expand=True)
        group.pack(fill='x')

    def addFiles(self):
        """Event handler to add files to the list"""
        files = tkFileDialog.askopenfilenames(parent=self, title='Add files')
        for file in files:
            log.debug("Adding '%s' to the file list" % file)
            self.listbox.insert('end', file)

    def removeFiles(self):
        """Event handler to remove files from the list"""
        selection = self.listbox.curselection()
        # Using reverse order prevents reflow from messing up indexing
        for line in reversed(selection):
            log.debug("Removing '%s' from the file list" %\
                      self.listbox.get(line))
            self.listbox.delete(line)

### --------------------------------------------------------------------

class TextList (DragList):
    """A widget for listing and editing several text strings"""
    def __init__(self, master=None, label="Text list", values=None):
        DragList.__init__(self, master, label, values)
        self.editbox = tk.Entry(self, width=30, textvariable=self.selected)
        self.editbox.bind('<Return>', self.setTitle)
        self.editbox.pack(fill='x', expand=True)

    def setTitle(self, event):
        """Event handler when Enter is pressed after editing a title."""
        newtitle = self.get()
        log.debug("Setting title to '%s'" % newtitle)
        self.listbox.delete(self.curindex)
        self.listbox.insert(self.curindex, newtitle)

### --------------------------------------------------------------------

# TODO: Cleanup/document these

class Panel:
    def __init__(self, title='', *optdefs):
        self.title = title
        self.optdefs = optdefs
        self.widgets = {}

    def create_widget(self, optdef, master):
        """Create and return a widget defined by the given option
        definition tuple, with the given master."""
        option = optdef[0]
        klass = optdef[1]
        args = optdef[2:]
        self.widgets[option] = klass(master, *args)
        return self.widgets[option]

    def draw_in(self, master):
        """Draw all panel widgets in the given master"""
        for optdef in self.optdefs:
            widget = self.create_widget(optdef, master)
            widget.pack(anchor='nw')

### --------------------------------------------------------------------

class Application (tk.Tk):
    def __init__(self, title="Application", panels=None):
        tk.Tk.__init__(self)
        self.title(title)
        self.panels = panels or []
        self.tabs = []
        # TODO: Avoid current/last hack somehow?
        self.current = tk.IntVar()
        self.last = 0

    def run(self):
        """Run the GUI application"""
        # Draw the tab-switching control widget
        self.buttons = tk.Frame(self)
        for index, panel in enumerate(self.panels):
            button = tk.Radiobutton(self.buttons, text=panel.title, value=index, 
                                    variable=self.current, indicatoron=0,
                                    command=self.change_tabs,
                                    selectcolor='white')
            button.pack(anchor='nw', side='left')
        self.buttons.pack(anchor='nw')
        # Draw each tab's panel
        for panel in self.panels:
            tab = tk.Frame(self)
            panel.draw_in(tab)
            self.tabs.append(tab)
        # Display the first tab
        self.tabs[0].pack(anchor='ne')
        self.mainloop()

    def change_tabs(self):
        """Switch to the selected tab panel"""
        index = self.current.get()
        self.tabs[self.last].pack_forget()
        self.tabs[index].pack(anchor='ne')
        self.last = index

