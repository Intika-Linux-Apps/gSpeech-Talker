#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

import os, sys, pynotify, shutil, tempfile, ConfigParser, subprocess, multiprocessing

import pygtk
pygtk.require('2.0')
import gtk

import pygst
pygst.require("0.10")
import gst

APPNAME = "gSpeech"
SCRIPT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))

import gettext
localdir = os.path.abspath(SCRIPT_DIR) + "/locale"
gettext.install(APPNAME, localdir)

#########################
# Application info
ICON = os.path.join(SCRIPT_DIR, 'icons', APPNAME + '.svg')
VERSION = "0.4.5.4"
AUTHORNAME = "Lahire Biette"
AUTHOREMAIL = "<tuxmouraille@gmail.com>"
AUTHOR = AUTHORNAME + ' ' + AUTHOREMAIL
COMMENT = _("A little script to read SVOX Pico texts selected with the mouse.")
COPYRIGHT_YEAR = '2011,2012'
COPYRIGHTS = u"Copyright © %s %s" % (COPYRIGHT_YEAR, AUTHORNAME)
AUTHORS = [
    _(u"Developers :"),
    u"%s" % (AUTHOR),
    #~ "",
    #~ _(u"Contributors:"),
]

TRANSLATORS = u"pt-PT, pt-BR, es-ES & it-IT :\n\
Dupouy Paul"

#~ ARTISTS = []
WEBSITE = 'https://github.com/tuxmouraille/MesApps/tree/master/gSpeech'

LICENSE = """Copyright © %s - %s.

%s is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

%s is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with %s.  If not, see <http://www.gnu.org/licenses/>.
""" % (COPYRIGHT_YEAR, AUTHOR, APPNAME, APPNAME, APPNAME)

# Supported SVOX Pico's languages
LISTLANG = ["de-DE", "en-GB", "en-US", "es-ES", "fr-FR", "it-IT"]


# Temporaries files
CACHEFOLDER = os.getenv('HOME') + '/.cache/' + APPNAME + '/'

if not os.path.exists(CACHEFOLDER):
    os.makedirs(CACHEFOLDER)

# Temporary PID file
PID = CACHEFOLDER + 'gspeech.pid'
# Temporary wav speech file
SPEECH = CACHEFOLDER + 'speech.wav'

###############################
###############################


# Main Class
class MainApp:
    """ the main class of the software """
    def __init__(self):
        # init app name in notification
        pynotify.init('gSpeech')
        # define speech language
        self.lang = DefaultLang
        # select related icon
        #~ self.icon = APPNAME + '-' + self.lang
        self.icon = ICON

        if IsAppIndicator == True :
            self.ind = appindicator.Indicator(APPNAME, self.icon, appindicator.CATEGORY_APPLICATION_STATUS)
            self.ind.set_status (appindicator.STATUS_ACTIVE)
            self.onRightClick(self)

        elif IsAppIndicator == False :
            # create GTK status icon
            self.tray = gtk.StatusIcon()
            self.tray.set_from_icon_name(self.icon) # select icon
            self.tray.connect('popup-menu', self.onRightClick) # right click
            self.tray.connect('activate', self.onLeftClick) # left click
            self.tray.set_tooltip((_(u"SVOX Pico simple GUI")))


        self.window = gtk.Dialog(APPNAME,
                           None,
                           gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        self.window.set_border_width(10)
        self.window.set_keep_above(True)
        self.window.set_icon_from_file(ICON)
        self.window.connect('delete-event', lambda w, e: w.hide() or True)

        hbox = gtk.HBox()

        # Create an accelerator group
        self.accelgroup = gtk.AccelGroup()
        # Add the accelerator group to the toplevel window
        self.window.add_accel_group(self.accelgroup)

        button = gtk.Button()
        button.set_image(gtk.image_new_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU))
        button.set_label(_(u"Read clipboard content"))
        button.connect("clicked", self.onExecute)
        button.add_accelerator("clicked",self.accelgroup , ord('c'), gtk.gdk.SHIFT_MASK, gtk.ACCEL_VISIBLE)
        hbox.pack_start(button, expand=False, fill=False)


        button = gtk.Button()
        button.set_image(gtk.image_new_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU))
        button.set_label(_(u"Read selected text"))
        button.connect("clicked", self.onExecute)
        button.add_accelerator("clicked",self.accelgroup , ord('x'), gtk.gdk.SHIFT_MASK, gtk.ACCEL_VISIBLE)
        hbox.pack_end(button, expand=False, fill=False)

        self.window.vbox.pack_start(hbox, expand=False, fill=False)


        hbox = gtk.HBox()

        self.WinPlayPause = gtk.Button(stock = gtk.STOCK_MEDIA_PAUSE)
        self.WinPlayPause.connect("clicked", self.onPlayPause)
        button.add_accelerator("clicked",self.accelgroup , ord('p'), gtk.gdk.SHIFT_MASK, gtk.ACCEL_VISIBLE)
        hbox.pack_start(self.WinPlayPause, expand=False, fill=False)

        button = gtk.Button(stock = gtk.STOCK_MEDIA_STOP)
        button.connect("clicked", self.onStop)
        button.add_accelerator("clicked",self.accelgroup , ord('q'), gtk.gdk.SHIFT_MASK, gtk.ACCEL_VISIBLE)
        hbox.pack_start(button, expand=False, fill=False)

        button = gtk.Button(stock = gtk.STOCK_SAVE)
        button.connect("clicked", self.onSave)
        button.add_accelerator("clicked",self.accelgroup , ord('s'), gtk.gdk.SHIFT_MASK, gtk.ACCEL_VISIBLE)
        hbox.pack_end(button, expand=False, fill=False)

        self.window.vbox.pack_start(hbox, expand=False, fill=False)

        hbox = gtk.HBox()

        combobox = gtk.combo_box_new_text()
        hbox.pack_start(combobox, expand=False, fill=False)
        count = 0
        for i in LISTLANG:
            combobox.append_text(i)
            if i == self.lang:
                combobox.set_active(count)
            count += 1
        combobox.connect('changed', self.changed_cb)

        button = gtk.Button(stock = gtk.STOCK_CLOSE)
        #~ button.connect_object("clicked", gtk.Widget.destroy, self.window)
        button.connect_object("clicked", gtk.Widget.hide, self.window)
        hbox.pack_end(button, expand=False, fill=False)

        self.window.vbox.pack_start(hbox, expand=False, fill=False)


    def changed_cb(self, combobox):
        model = combobox.get_model()
        index = combobox.get_active()
        if index:
            self.onLang(self, model[index][0])
        return


    # action on right click
    def onRightClick(self, icon=None, event_button=None, event_time=None):
        # create menu
        menu = gtk.Menu()

        mediawin = gtk.ImageMenuItem(_(u"Multimedia window"))
        mediawin.connect('activate', self.onMediaDialog)
        mediawin.show()
        menu.append(mediawin)

        # Separator
        rmItem =  gtk.SeparatorMenuItem()
        rmItem.show()
        menu.append(rmItem)

        # Execute menu item : execute speeching from Desktop clipboard
        rmItem = gtk.ImageMenuItem()
        rmItem.set_label(_(u"Read clipboard content"))
        rmItem.connect('activate', self.onExecute)
        rmItem.show()
        menu.append(rmItem)


        # Execute menu item : execute speeching from X.org clipboard
        rmItem = gtk.ImageMenuItem()
        rmItem.set_label(_(u"Read selected text"))
        rmItem.connect('activate', self.onExecute)
        rmItem.show()
        menu.append(rmItem)

        # Play item menu
        self.PlayPause = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PAUSE)
        self.PlayPause.connect('activate', self.onPlayPause)
        self.PlayPause.show()
        menu.append(self.PlayPause)

        # Stop  item menu
        rmItem = gtk.ImageMenuItem(gtk.STOCK_MEDIA_STOP)
        rmItem.connect('activate', self.onStop)
        rmItem.show()
        menu.append(rmItem)

        # Save item menu
        rmItem = gtk.ImageMenuItem(gtk.STOCK_SAVE)
        rmItem.connect('activate', self.onSave)
        rmItem.show()
        menu.append(rmItem)

        # Separator
        rmItem =  gtk.SeparatorMenuItem()
        rmItem.show()
        menu.append(rmItem)

        # Preference item menu
        rmItem = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        rmItem.show()
        # Creating and linking langues submenu
        menulngs = gtk.Menu()
        rmItem.set_submenu(menulngs)

        # Creating languages items in submenu
        # one empty item to initiate radioitem group
        smItem = gtk.RadioMenuItem(None, None)
        for i in LISTLANG:
            # Creating new item
            smItem = gtk.RadioMenuItem(smItem, i, True)
            # ... adding item in submenu
            menulngs.append(smItem)
            # linking it with onLang fonction
            smItem.connect("toggled", self.onLang, i)
            # i is defaut language activating radio button
            if i == self.lang :
                smItem.set_active(True)
            # show item
            smItem.show()

        menu.append(rmItem)

        ## Reload item menu
        item = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        item.connect('activate', self.onReload)
        item.show()
        menu.append(item)

        # About item menu : show About dialog
        about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        about.connect('activate', self.onAbout)
        about.show()
        menu.append(about)

        # Quit item menu
        item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        item.connect('activate', self.destroy)
        item.show()
        menu.append(item)

        if IsAppIndicator == True :
            menu.show()
            self.ind.set_menu(menu)

        elif IsAppIndicator == False :
            menu.popup(None, None, gtk.status_icon_position_menu, event_button, event_time, self.tray)


    ## onReload item function: reload script
    def onReload(self, widget):
        myscript = os.path.abspath(sys.argv[0])
        subprocess.Popen(myscript)
        sys.exit()

    # action on language submenu items
    def onLang(self, widget, lng):
        self.lang = lng
        #~ self.icon = APPNAME + '-' + self.lang
        self.icon = os.path.join(SCRIPT_DIR, 'icons', APPNAME + '-' + self.lang + '.svg')

        if IsAppIndicator == True :
            self.ind.set_icon(self.icon)

        elif IsAppIndicator == False :
            self.tray.set_from_icon_name(self.icon)

    # show about dialog
    def onAbout(self, widget):
        self.aboutdiag = AboutDialog()
        self.aboutdiag

    # show multimedia control dialog
    def onMediaDialog(self, widget):
        if self.window.get_property('visible'):
            self.window.hide()
        else :

            self.window.show_all()

    # error message on playing function
    def onMessage(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            #file ended, stop
            self.player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            #Error ocurred, print and stop
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err, debug

    # left click on status icon function
    # function like this and not merge with onExecute
    # to have possibility to use for something different
    def onLeftClick(self, widget, data=None):
        self.onExecute(self, widget)

    # on Execute item function : execute speech
    def onExecute(self, widget, data=None):
        pynotify.Notification(APPNAME, _(u"I'm reading the text. One moment please."), self.icon).show()

        if widget.get_label() == _(u"Read selected text") :
            text = gtk.clipboard_get(selection="PRIMARY").wait_for_text()
        else :
            text = gtk.clipboard_get(selection="CLIPBOARD").wait_for_text()

        #~ text = text.lower()
        text = text.replace('\"', '')
        text = text.replace('`', '')
        text = text.replace('´', '')
        text = text.replace('-','')

        dic = CONFIGDIR + '/' + self.lang + '.dic'

        if os.path.exists(dic) :
            for line in open(dic,'r').readlines():

                bad = line.split('=')[0]
                #~ bad = bad.lower()
                try :
                    good = line.split('=')[1]
                except :
                    good = ' '
                text = text.replace(bad, good)
        if len(text) <= 32768:
            os.system('pico2wave -l %s -w %s \"%s\" ' % ( self.lang, SPEECH, text ))
        else:
            discours = text.split('\n\n')
            commands = []
            fichiers = []
            noms = []
            text = ''
            for idx,paragraph in enumerate(discours):
                text += paragraph
                if idx == len(discours)-1 or len(text) + len(discours[idx+1]) >= 32767:
                    filename = CACHEFOLDER + 'speech' + str(idx) + '.wav'
                    commands.append('pico2wave -l %s -w %s \"%s\" ' % ( self.lang, filename, text ))
                    noms.append(filename)
                    text = ''
            nproc = int(.5 * multiprocessing.cpu_count())
            if nproc == 0: nproc = 1
            multiprocessing.Pool(nproc).map(os.system, commands)
            os.system('sox %s %s' % ( ' '.join(noms), SPEECH ))
            player = self.onPlayer(SPEECH)
            self.player.set_state(gst.STATE_PLAYING)
            for fichier in noms:
                os.remove(fichier)

    # player fonction
    def onPlayer(self,file):
        #Element playbin automatic plays any file
        self.player = gst.element_factory_make("playbin", "player")
        #Set the uri to the file
        self.player.set_property("uri", "file://" + file)
        #Enable message bus to check for errors in the pipeline
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.onMessage)

    # play, pause and stop function for respectivs items
    def onPlayPause(self, widget, data=None):
        if widget.get_label() == gtk.STOCK_MEDIA_PLAY :
            self.player.set_state(gst.STATE_PLAYING)
        else :
            self.player.set_state(gst.STATE_PAUSED)

        self.buttonState()


    def onStop(self, widget, data=None):
        self.player.set_state(gst.STATE_NULL)
        self.buttonState()


    def buttonState(self):
        if gst.STATE_PLAYING == self.player.get_state()[1] :
            self.PlayPause.set_label(gtk.STOCK_MEDIA_PAUSE)
            self.PlayPause.set_image(gtk.image_new_from_stock(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_MENU))
            self.WinPlayPause.set_label(gtk.STOCK_MEDIA_PAUSE)
            self.WinPlayPause.set_image(gtk.image_new_from_stock(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_MENU))

        elif gst.STATE_PAUSED == self.player.get_state()[1] or gst.STATE_NULL == self.player.get_state()[1] :
            self.PlayPause.set_label(gtk.STOCK_MEDIA_PLAY)
            self.PlayPause.set_image(gtk.image_new_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU))
            self.WinPlayPause.set_label(gtk.STOCK_MEDIA_PLAY)
            self.WinPlayPause.set_image(gtk.image_new_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU))



    # saving file speech on clicking Save item
    def onSave(self, widget, data=None):
        SaveFile()

    # destroy app on clicking Quit item
    def destroy(self, widget, data=None):
        # remove temporary sound file
        if os.path.isfile(SPEECH):
            os.remove(SPEECH)
        # remove file with current process pid
        if os.path.isfile(PID):
            os.remove(PID)
        # quit program
        gtk.main_quit()

    def main(self):
        gtk.main()



# About dialog class
class AboutDialog:
    """ the about dialog class """
    def __init__(self):
        # Create AboutDialog object
        dialog = gtk.AboutDialog()
        dialog.set_logo_icon_name(APPNAME)
        dialog.set_name(APPNAME)
        dialog.set_version(VERSION)
        dialog.set_copyright(COPYRIGHTS)
        dialog.set_license(LICENSE)
        dialog.set_authors(AUTHORS)
        dialog.set_comments(COMMENT)
        dialog.set_translator_credits(TRANSLATORS)
        dialog.set_website(WEBSITE)
        dialog.set_website_label(_("%s's Website") % APPNAME)
        #~ dialog.set_artists(ARTISTS)

        dialog.connect("response", lambda self, *f: self.destroy())
        dialog.show_all()


# Audio speech wav file class saving
class SaveFile:
    """ the class to save the speech .wav file """
    def __init__(self):
        dialog = gtk.FileChooserDialog(_(u"Save the speech"),
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OK, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_current_folder(os.path.expanduser('~'))

        #~ dialog.set_modal(False)
        #~ dialog.set_transient_for(window)
        #~ dialog.set_decorated(False)


        filter = gtk.FileFilter()
        filter.set_name(_(u"Wave file (*.wav)"))
        filter.add_mime_type("audio/x-wav")
        filter.add_pattern("*.wav")
        dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename2 = dialog.get_filename()
            shutil.copy(SPEECH, filename2)

        dialog.destroy()



def IniRead(configfile, section, key, default):
    if os.path.isfile(configfile):
        parser = ConfigParser.SafeConfigParser()
        parser.read(configfile)

        try:
            var = parser.get( section , key )
        except:
            var = default
    else:
        var = default

    if var.lower() in ['1', 'yes', 'true', 'on'] :
        return True
    elif var.lower() in ['0', 'no', 'false', 'off'] :
        return False
    else :
        return var


if __name__ == "__main__":
    # is PID exists?
    if os.path.isfile(PID):
        # yes. read it
        file = open(PID, 'r')
        # convert content into integer, to retreive PID
        pid = int(file.read())
        # try to kill PID
        try:
            os.kill(pid, 0)
        # error. process not exists, pass
        except OSError:
            pass
        # process exists. print error message and quit
        else:
            # process existing => show error message
            print "** %s is already running\nOtherwise, delete %s" % (APPNAME,PID)
            quit()

    # finding pid of this process
    pid = "%s" % os.getpid()
    # write pid in PID
    file = open(PID, 'w')
    file.write(pid)
    file.close()


    CONFIGDIR = os.path.join(os.path.expanduser('~'), '.config/gSpeech')
    if not os.path.isdir(CONFIGDIR) :
        os.mkdir(CONFIGDIR, 0775)

    CONFIGFILE = os.path.join(CONFIGDIR,'gspeech.conf')
    if not os.path.isfile(CONFIGFILE) :
        config = ConfigParser.RawConfigParser()
        config.add_section('CONFIGURATION')
        config.set('CONFIGURATION', 'USEAPPINDICATOR', 'True')
        config.set('CONFIGURATION', 'DEFAULTLANGUAGE', '')
        #~ config.set('CONFIGURATION', 'SHOWMEDIADIALOG', 'False')
        with open(CONFIGFILE, 'wb') as configfile:
            config.write(configfile)

    IsAppIndicator = bool(IniRead(CONFIGFILE, 'CONFIGURATION', 'USEAPPINDICATOR', 'True' ))

    DefaultLang = str(IniRead(CONFIGFILE, 'CONFIGURATION', 'DEFAULTLANGUAGE', '' ))
    DefaultLang = DefaultLang[ : 2 ] + '-' + DefaultLang[ 3 : ][ : 2 ]
    # if SVOX Pico not support this language, find os environment language
    if not DefaultLang in LISTLANG :
        DefaultLang = os.environ.get('LANG', 'en_US')[ : 2 ] + '-' + os.environ.get('LANG', 'en_US')[ 3 : ][ : 2 ]
        # if SVOX Pico not support this language, use US english
        if not DefaultLang in LISTLANG :
            DefaultLang = "en-US"

    try :
        import appindicator

    except :
        IsAppIndicator = False


    gSpeech = MainApp()
    gSpeech.main()

