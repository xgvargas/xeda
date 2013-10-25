
class Grid(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.snap= 50
        self.grid= [(100, (.7, .7, .7), .5, 'line'), (1000, (.9, .9, 1), 1, 'line')] #can be 'dot' too
        self.relx= 0
        self.rely= 0
        self.scrx= 0
        self.scry= 0
        self.scale= 1
        self.window_w= 300
        self.window_h= 300
        self.w= 300
        self.h= 300

    def on_canvas_event(self, wd, event):
        if event.type is gtk.gdk.MOTION_NOTIFY:
            print 'movimento %d-%d - %d' % (event.x, event.y, event.state)
            #movimento com botao 2 apertado muda o pam e redesenha

        elif event.type is gtk.gdk.BUTTON_PRESS:
            print 'click %d-%d - %d - %d' % (event.x, event.y, event.state, event.button)
            #click com botao dois salva x,y para fazer pam relativo

        elif event.type is gtk.gdk.BUTTON_RELEASE:
            print 'desclick %d-%d - %d - %d' % (event.x, event.y, event.state, event.button)
            #quando solta o botao 2 marca fim do pam

        elif event.type is gtk.gdk.CONFIGURE:
            #print 'config %d-%d - %d-%d' % (event.x, event.y, event.width, event.height)
            self.window_w= event.width
            self.window_h= event.height
            
        elif event.type is gtk.gdk.SCROLL:
            #print 'roda %d-%d - %d - %d' % (event.x, event.y, event.state, event.direction)
            if event.direction == gtk.gdk.SCROLL_UP:
                if self.scale < 5.5:
                    self.scale*= 1.2
                    
            if event.direction == gtk.gdk.SCROLL_DOWN:
                if self.scale > 0.06:
                    self.scale/= 1.2
            print self.scale
            event.window.invalidate_rect( (0, 0, self.window_w, self.window_h), False)  #repaint

        elif event.type is gtk.gdk.EXPOSE:
            #print 'redesenhando....'
            self.cr= event.window.cairo_create()
            self._grid_draw()
            self._draw()

    def _adjust(self):
        self.w= int(self.window_w/self.scale)
        self.h= int(self.window_h/self.scale)
    
        m= cairo.Matrix(1, 0, 0, -1, 0, 0)
        self.cr.set_matrix(m) #mirror Y

        self.cr.translate(0, -self.window_h)
        
        self.cr.scale(self.scale, self.scale)

        #cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        #cr.clip()
        
    def screen_to_grid(self, x, y):
        gx= x/self.scale
        gy= (self.window_h-y)/self.scale
        return (gx, gy)
        
    def _grid_draw(self):
        self._adjust()

        self.cr.set_source_rgb(0, 0, 0)
        self.cr.rectangle(0, 0, self.w, self.h)
        self.cr.fill()  #TODO maybe paint will work better here

        for g in self.grid:
            self.cr.set_line_width(g[2])
            self.cr.set_source_rgb(*g[1])
            if g[3] == 'line':  #TODO work with dot too
                for a in xrange(0, self.w, g[0]):
                    self.cr.move_to(a, 0)
                    self.cr.line_to(a, self.h)

                for b in xrange(0, self.h, g[0]):
                    self.cr.move_to(0, b)
                    self.cr.line_to(self.w, b)
                self.cr.stroke()

