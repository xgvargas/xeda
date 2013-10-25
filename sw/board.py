
class PCBEntity(Grid):
    def __init__(self, db, pcbName, statusbar):
        Grid.__init__(self)
        self.statusbar= statusbar

        canvas= gtk.DrawingArea()
        canvas.set_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)
        canvas.connect('event', self.on_canvas_event)
        self.pack_start(canvas, True, True, 0)

        bla= gtk.Label('aqui vai aparecer uma lista com os layers disponiveis...')
        self.pack_start(bla, False, True, 0)

        self.show_all()
        
        self.load_from_db(db, pcbName)
    
    def load_from_db(self, db, table):
        pass
    
    def _draw(self):
        self.cr.set_source_rgba(1, 0.1, 1, .5)
        self.cr.set_line_width(5)
        self.cr.arc(100, 100, 50, 0, 2 * pi)
        self.cr.stroke()
        self.cr.arc(300, 300, 40, 0, 2 * pi)
        self.cr.stroke()

        self.cr.arc(7300, 7300, 40, 0, 2 * pi)
        self.cr.arc(2300, 2300, 40, 0, 2 * pi)
        self.cr.arc(4300, 4300, 40, 0, 2 * pi)
        self.cr.fill()

        self.cr.set_source_rgba(0.1, 0.1, 1, .5)
        self.cr.set_line_width(100)
        
        self.cr.move_to(0, 0)
        self.cr.line_to(self.w, self.h)
        self.cr.stroke()
        
        self.cr.set_source_rgba(.1, 1, 0.1, .5)
        self.cr.move_to(self.w, 0)
        self.cr.line_to(0, self.h)
        self.cr.stroke()
        
        self.cr.rectangle(200, 200, 100, 100)
        self.cr.fill()

        self.cr.set_source_rgba(.1, 1, 0.6, .5)
        self.cr.save()
        self.cr.translate(200, 200)
        self.cr.set_source_rgba(.6, 1, 0.6, .5)
        self.cr.rectangle(10, 10, 100, 100)
        self.cr.fill()
        self.cr.rotate(.6)
        self.cr.translate(-200, -200)
        self.cr.set_source_rgba(.9, .3, 0.8, .5)
        self.cr.rectangle(200, 200, 100, 100)
        self.cr.fill()
        
        self.cr.restore()
        self.cr.rectangle(400, 400, 150, 150)
        self.cr.fill()
        
    def on_canvas_event(self, wd, event):
        Grid.on_canvas_event(self, wd, event)
        
        if event.type is gtk.gdk.MOTION_NOTIFY:
            p= self.screen_to_grid(event.x, event.y)
            self.statusbar.push(0, 'x:%d y:%d' % (p[0], p[1]))

        elif event.type is gtk.gdk.BUTTON_PRESS:
            pass

        elif event.type is gtk.gdk.BUTTON_RELEASE:
            pass

