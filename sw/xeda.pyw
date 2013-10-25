import sys
try:  
    import pygtk  
    pygtk.require("2.0")  
except:  
    pass  
try:  
    import gtk  
except:  
    print("GTK Not Availible")
    sys.exit(1)

#import gobject
import cairo
from math import pi
import sqlite3


#o legal seria fazer uma classe base com os paramentros basicos, posicao, angulo
#dessa derivo uma classe para cada objetos com uma funcao para desenha-lo e outra que retorna
#uma string com os parametros desse obejto. e o construtor pode receber essa string para reconstrui-lo
#objetos simples seriam instancias dessas classes basicos. componentes, tanto sch quanto pcb, seriam
#agregadores dessas classes bases
#a classe pcb seria um agregador de objetos basicos e de componentes pcb. algo similar para a classe sch
#a classe pcb e sch seria derivada da classe grid que cuida do zoom e do pam da janela
#o draw da classe pcb e sch dispara o draw dos agregados
#falta imaginar algum buffer para manter a imagem original durante alteracoes, assim nao seria necessario redesenhar
#tudo a cada movimento do mouse


class GridUndo:
    def __init__(self):
        self._stack= []
        self._wait= {}

    def undo_begin(self, obj):
        t= obj.pack_data()
        #print t
        self._wait[obj]= t
        
    def undo_end(self, obj):
        if obj in self._wait:
            t= obj.pack_data()
            #print t
            if t != self._wait[obj]:
                self._stack.append( (obj, self._wait[obj]) )
                del self._wait[obj]
                #print 'criado undo'
        
    def undo(self, level= 1):
        for i in xrange(level):
            if len(self._stack) == 0: return

            o, v= self._stack[-1]
            #print 'voltando...'
            #print v
            o.load_data(v)
            del self._stack[-1]
        

class GridConfig:
    _saveData= ( (),  #integers
                 (),  #boolean
                 ()   #strigs
                 )
    
    def __init__(self, data= None):
        if data:
            self.load_data(data)
        
    def load_data(self, data):
        v= data.split(';')
        
        for i, k in enumerate(self._saveData[0]):  #int
            setattr(self, k, int(v[i]))

        v[:len(self._saveData[0])]= []
        for i, k in enumerate(self._saveData[1]):  #bool
            setattr(self, k, v[i] in ('True', '1', 'yes', 'true'))

        v[:len(self._saveData[1])]= []
        for i, k in enumerate(self._saveData[2]):  #string
            setattr(self, k, v[i])
            
    def pack_data(self):
        t= ''
        for c in self._saveData:
            for d in c:
                t+= repr(getattr(self, d))+';'  #FIXME need to scape ';'
            
        return t[:-1]
        


class GridObject(GridConfig):
    _saveData= ( ('posX', 'posY', 'centerX', 'centerY', 'w', 'h', 'angle'), #int
                 ('selected', 'mirrored', 'locked', 'sizeable'), #bool
                 () #string
               )
    posX= 0
    posY= 0
    centerX= 0
    centerY= 0
    w= 0
    h= 0
    angle= 0
    selected= False
    mirrored= False
    locked= False
    glow= False
    dragging= False
    parent= None
    sizeable= True
    boxColor= (1, 1, .4)
    _boxIsOn= False
    
    def is_mouse_over(self, x, y):
        a= self.posX-self.centerX
        b= self.posY-self.centerY

        if self._boxIsOn and self.sizeable:
            #TODO this is so ugly.... maybe i should find another way.....
            s= 10/self.parent.scale
            s2= s/2
            if x >= a and x <= a+s and y >= b and y <= b+s: return 'SW'
            if x >= a+self.w/2-s2 and x <= a+self.w/2+s2 and y >= b and y <= b+s: return 'S'
            if x >= a+self.w-s and x <= a+self.w and y >= b and y <= b+s: return 'SE'
            if x >= a and x <= a+s and y >= b+self.h/2-s2 and y <= b+self.h/2+s2: return 'W'
            if x >= a+self.w-s and x <= a+self.w and y >= b+self.h/2-s2 and y <= b+self.h/2+s2: return 'E'
            if x >= a and x <= a+s and y >= b+self.h-s and y <= b+self.h: return 'NW'
            if x >= a+self.w/2-s2 and x <= a+self.w/2+s2 and y >= b+self.h-s and y <= b+self.h: return 'N'
            if x >= a+self.w-s and x <= a+self.w and y >= b+self.h-s and y <= b+self.h: return 'NE'
          
        if x >= a and x <= a+self.w and y >= b and y <= b+self.h: return 'inside'
            
        return None        
        
    def _draw_normal(self):
        self.parent.cr.set_dash([])
        self.parent.cr.move_to(self.posX-self.centerX, self.posY-self.centerY)
        self.parent.cr.line_to(self.posX-self.centerX+self.w, self.posY-self.centerY+self.h)
        self.parent.cr.move_to(self.posX-self.centerX, self.posY-self.centerY+self.h)
        self.parent.cr.line_to(self.posX-self.centerX+self.w, self.posY-self.centerY)
        self.parent.cr.rectangle(self.posX-self.centerX, self.posY-self.centerY, self.w, self.h)
        self.parent.cr.set_line_width(12)
        self.parent.cr.set_line_cap(cairo.LINE_CAP_ROUND)
        self.parent.cr.set_source_rgb(1, .5, .5)
        self.parent.cr.stroke()

    def _draw_selected(self):
        self.parent.cr.set_dash([])
        self.parent.cr.move_to(self.posX-self.centerX, self.posY-self.centerY)
        self.parent.cr.line_to(self.posX-self.centerX+self.w, self.posY-self.centerY+self.h)
        self.parent.cr.move_to(self.posX-self.centerX, self.posY-self.centerY+self.h)
        self.parent.cr.line_to(self.posX-self.centerX+self.w, self.posY-self.centerY)
        self.parent.cr.rectangle(self.posX-self.centerX, self.posY-self.centerY, self.w, self.h)
        self.parent.cr.set_line_width(18)
        self.parent.cr.set_line_cap(cairo.LINE_CAP_ROUND)
        self.parent.cr.set_source_rgba(1, 1, .5, .6)
        self.parent.cr.stroke()
        
    def _draw_box(self):
        pass
    
    def _draw_glow(self):
        self.parent.cr.rectangle(self.posX-self.centerX, self.posY-self.centerY, self.w, self.h)
        self.parent.cr.set_line_width(2/self.parent.scale)
        self.parent.cr.set_source_rgb(*self.boxColor)
        self.parent.cr.set_dash([5/self.parent.scale])
        self.parent.cr.stroke()
        
        self._boxIsOn= self.sizeable
        if self.sizeable:
            s= 10/self.parent.scale
            self.parent.cr.rectangle(self.posX-self.centerX, self.posY-self.centerY, s, s)
            self.parent.cr.rectangle(self.posX-self.centerX+self.w/2-s/2, self.posY-self.centerY, s, s)
            self.parent.cr.rectangle(self.posX-self.centerX+self.w-s, self.posY-self.centerY, s, s)
            
            self.parent.cr.rectangle(self.posX-self.centerX, self.posY-self.centerY+self.h/2-s/2, s, s)
            self.parent.cr.rectangle(self.posX-self.centerX+self.w-s, self.posY-self.centerY+self.h/2-s/2, s, s)
            
            self.parent.cr.rectangle(self.posX-self.centerX, self.posY-self.centerY+self.h-s, s, s)
            self.parent.cr.rectangle(self.posX-self.centerX+self.w/2-s/2, self.posY-self.centerY+self.h-s, s, s)
            self.parent.cr.rectangle(self.posX-self.centerX+self.w-s, self.posY-self.centerY+self.h-s, s, s)
            self.parent.cr.fill()
    
    def draw(self):
        self._draw_normal()
        if self.selected: self._draw_selected()
        if self.glow: self._draw_glow()
        
    def update(self, msg, **kwargs):
        print kwargs
        dx= kwargs['dx']
        dy= kwargs['dy']
        
        if msg == 'inside':
            self.posX+= dx
            self.posY+= dy
        if 'N' in msg:
            self.h+= dy
            if self.h < 1: self.h= 1
        if 'E' in msg:
            self.w+= dx
            if self.w < 1: self.w= 1
        if 'S' in msg:
            self.h+= -dy
            self.posY+= dy
            if self.h < 1:
                self.posY+= self.h-1
                self.h= 1
        if 'W' in msg:
            self.w+= -dx
            self.posX+= dx
            if self.w < 1:
                self.posX+= self.w-1
                self.w= 1

        if self.posX < 0: self.posX= 0
        if self.posX > self.parent.max_w: self.posX= self.parent.max_w
        if self.posY < 0: self.posY= 0
        if self.posY > self.parent.max_h: self.posY= self.parent.max_h
        
        return True   #FIXME so retorna true para quando precisa redesenhar!
        
    def on_click(self, button, x, y):
        '''returns True when it want to be redrawn
        '''
        self.glow= True
        return True
        
    def on_doble_click(self, button, x, y):
        '''returns True when it want to be redrawn
        '''
        return False


class GridCollection(GridUndo):
    def __init__(self, parent):
        GridUndo.__init__(self)
        self.parent= parent
        self._items= []
        self.in_focus= None
        self._focus_msg= ''
        self._selecteds= [] #list of selected objects
        
    def __iter__(self):
        for o in self._items:
            yield o
    
    def add(self, obj):
        '''adds a new object to this collection
        '''
        if obj not in self._items:
            self._items.append(obj)
            obj.parent= self.parent
            
    def draw(self):
        '''draw all objects over contained in this collection
        '''
        for o in self._items:
            o.draw()

    def reduce_focused(self, focus_list):
        #FIXME aqui everia haver um jeito de selecionar SOMENTE 1 caso a lista seja maior
        # (um popup menu seria bom), a ideia e'sair dessa funcao com somente um item selecionado
        
        return focus_list.keys()[0] #isso forca so o primeiro da lista, mas esta ruim!!!
        
    def is_mouse_over(self, x, y):
        '''returns a dicionary with the object as key and value equal to the object tag of what is over this point
        '''
        f= {}
        for o in self._items:
            a= o.is_mouse_over(x, y)
            if a is not None:
                f[o]= a
        n= len(f)
        
        if f == {}:
            self.in_focus= None
            self._focus_msg= ''
        else:
            self.in_focus= self.reduce_focused(f)
            self._focus_msg= f[self.in_focus]
        
        return n

    def get_insiders(self, x1, y1, x2, y2):
        '''returns a list of objects completely fits inside the rectangle x1,y2-x2,y2
        '''
        if x1 > x2: x1, x2= x2, x1
        if y1 > y2: y1, y2= y2, y1
        self._selecteds= []
        for o in self._items:
            if o.posX-o.centerX >= x1 and o.posX-o.posX+o.h <= x2 and \
                                            o.posY-o.centerY >= y1 and o.posY-o.centerY+o.w <= y2:
                self._selecteds.append(o)
                o.selected= True
                
        return len(self._selecteds)

    def toggle_selection(self, obj):
        if obj in self._selecteds:
            self._selecteds.remove(obj)
            obj.selected= False
        else:
            self._selecteds.append(obj)
            obj.selected= True
            
    def update(self, **kwargs):
        redraw= False
        if self.in_focus:
            m= kwargs.get('msg') or self._focus_msg
            print m
            if self.in_focus in self._selecteds:
                for o in self._selecteds:
                    redraw|= o.update(m, **kwargs)
            else:
                redraw|= self.in_focus.update(m, **kwargs)
                
        return redraw

    def delete(self):
        if self.in_focus:
            if self.in_focus in self._selecteds:
                for o in self._selecteds:
                    self._items.remove(o)
                    del o
            else:
                self._items.remove(self.in_focus)
                del self.in_focus
            
            self.in_focus= None
            self._focus_msg= ''
            self._selecteds= []
    
    def undo_begin(self):
        if self.in_focus:
            if self.in_focus in self._selecteds:
                for o in self._selecteds:
                    GridUndo.undo_begin(self, o)
            else:
                GridUndo.undo_begin(self, self.in_focus)
        
    def undo_end(self):
        if self.in_focus:
            if self.in_focus in self._selecteds:
                for o in self._selecteds:
                    GridUndo.undo_end(self, o)
            else:
                GridUndo.undo_end(self, self.in_focus)
        
    def clean_glow(self):
        for o in self._items:
            o.glow= False
    

class Grid(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.snap= 100
        self.grid= [(100, (.7, .7, .7), .5, 'line'), (1000, (.9, .9, 1), 1, 'line')] #can be 'dot' too
        self.relx= 0
        self.rely= 0
        self.scrx= 0
        self.scry= 0
        self.scale= 1
        self.max_w= 24000
        self.max_h= 12000
        self.max_scale= 5.5
        self.min_scale= 0.06
        self.window_w= 300
        self.window_h= 300
        self.w= 300
        self.h= 300
        self.clickMark= [[0, 0], [0, 0], [0, 0]]
        self.items= GridCollection(self)
        self.objClick= {}
        
        o1= GridObject()
        o1.posX= 1000
        o1.posY= 1000
        o1.centerX= 200
        o1.centerY= 200
        o1.w= 1000
        o1.h= 4000
        self.items.add(o1)

        o2= GridObject()
        o2.posX= 2300
        o2.posY= 900
        o2.centerX= 300
        o2.centerY= 200
        o2.w= 200
        o2.h= 450
        self.items.add(o2)

        for a in xrange(5):
            for b in xrange(5):
                o2= GridObject()
                o2.posX= a*300+15
                o2.posY= b*300+15
                o2.centerX= 0
                o2.centerY= 0
                o2.w= 80
                o2.h= 80
                self.items.add(o2)

    def on_canvas_event(self, wd, event):
        if event.type is gtk.gdk.MOTION_NOTIFY:
            #print 'movimento %d-%d - %d' % (event.x, event.y, event.state)
            
            if event.state == 256: #move with button 1 pressed
                #pam adjust
                if event.x < 25:
                    self.scrx-= 20
                    self.clickMark[0][0]+= 20

                if event.x > self.window_w-25:
                    self.scrx+= 20
                    self.clickMark[0][0]-= 20

                if event.y < 25:
                    self.scry+= 20
                    self.clickMark[0][1]+= 20

                if event.y > self.window_h-25:
                    self.scry-= 20
                    self.clickMark[0][1]-= 20

                self._adjust_pam()

                #snap adjust (to absolute grid not relative!)
                dx= int(((event.x-self.clickMark[0][0])/self.scale)/self.snap)
                if dx != 0:
                    dx*= self.snap
                    self.clickMark[0][0]+= dx*self.scale

                dy= int(((self.clickMark[0][1]-event.y)/self.scale)/self.snap)
                if dy != 0:
                    dy*= self.snap
                    self.clickMark[0][1]-= dy*self.scale
                
                if dx != 0 or dy != 0:
                    #move/resize the box
                    self.items.update(dx= dx, dy= dy)

                    self.redraw()
                    
                    self.wasPam= True  #TODO maybe this should stay out this IF
            
            if event.state == 512: #move with button 2 pressed
                self.scrx+= self.clickMark[1][0]-event.x
                self.scry+= event.y-self.clickMark[1][1]  #remember Y is mirrored
                self._adjust_pam()
                self.clickMark[1]= [event.x, event.y]
                self.redraw()
                self.wasPam= True

        elif event.type is gtk.gdk.BUTTON_PRESS:
            print 'click %d-%d - %d - %d' % (event.x, event.y, event.state, event.button)

            self.wasPam= False
            
            redraw= False
            
            if event.button <= 3:
                self.clickMark[event.button-1]= [event.x, event.y]
            
            old= self.items.in_focus
            if event.button is 1:
                redraw|= self.items.is_mouse_over(*self.screen_to_work(event.x, event.y))
            
            self.items.clean_glow()
            
            self.items.undo_begin()
            if self.items.in_focus:
                if event.state&1: #shift
                    self.items.toggle_selection(self.items.in_focus)
                    redraw= True
                else:
                    redraw|= self.items.in_focus.on_click(event.button, event.x, event.y)
                    
            if old != self.items.in_focus: redraw= True
            
            if redraw: self.redraw()

            #FIXME isso nao vai ficar aqui.....
            if event.button == 3:
                self.set_rel_origin(*self.screen_to_work(*self.clickMark[2]))

        elif event.type is gtk.gdk.BUTTON_RELEASE:
            print 'desclick %d-%d - %d - %d' % (event.x, event.y, event.state, event.button)
            
            if event.button == 2 and not self.wasPam:
                self.pam_to(*self.screen_to_work(*self.clickMark[1]))

            self.items.undo_end()

        elif event.type is gtk.gdk.CONFIGURE:
            #print 'config %d-%d - %d-%d' % (event.x, event.y, event.width, event.height)
            self.window_w= event.width
            self.window_h= event.height
            
        elif event.type is gtk.gdk.SCROLL:
            #print 'roda %d-%d - %d - %d' % (event.x, event.y, event.state, event.direction)
            old= self.screen_to_work(event.x, event.y)
            if event.direction == gtk.gdk.SCROLL_UP and self.scale < self.max_scale: self.scale*= 1.2
            if event.direction == gtk.gdk.SCROLL_DOWN and self.scale > self.min_scale: self.scale/= 1.2
            #print self.scale
            self.scrx= old[0]*self.scale-event.x
            self.scry= old[1]*self.scale-self.window_h+event.y
            self._adjust_pam()
            self.redraw()

        elif event.type is gtk.gdk.EXPOSE:
            #print 'redesenhando....'
            self.cr= event.window.cairo_create()
            self._grid_draw()
            self._draw()
            self.items.draw()
        else:
            print event.type

    def _adjust(self):
        self.w= int(self.window_w/self.scale)
        self.h= int(self.window_h/self.scale)
    
        m= cairo.Matrix(1, 0, 0, -1, 0, 0)
        self.cr.set_matrix(m) #mirror Y

        self.cr.translate(-self.scrx, -self.scry-self.window_h)
        self.cr.scale(self.scale, self.scale)

        #cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        #cr.clip()
        
    def _grid_draw(self):
        self._adjust()

        self.cr.set_source_rgb(0, 0, 0)
        self.cr.rectangle(0, 0, self.max_w, self.max_h)
        self.cr.fill()  #TODO maybe paint will work better here

        for g in self.grid:
            self.cr.set_line_width(g[2])
            self.cr.set_source_rgb(*g[1])
            if g[3] == 'line':  #TODO work with dot too
                for a in xrange(self.relx % g[0], self.max_w, g[0]):
                    self.cr.move_to(a, 0)
                    self.cr.line_to(a, self.max_h)

                for b in xrange(self.rely % g[0], self.max_h, g[0]):
                    self.cr.move_to(0, b)
                    self.cr.line_to(self.max_w, b)
            self.cr.stroke()

        self.cr.move_to(self.relx-20, self.rely-20)
        self.cr.line_to(self.relx+20, self.rely+20)
        self.cr.move_to(self.relx-20, self.rely+20)
        self.cr.line_to(self.relx+20, self.rely-20)
        self.cr.set_line_width(3)
        self.cr.set_source_rgb(1, .5, .5)
        self.cr.stroke()
        
    def _draw(self):
        '''This should be implemented by derived class
        '''
        pass
        
    def _adjust_pam(self):
        if self.scrx < 0: self.scrx= 0
        if self.scrx/self.scale+self.w > self.max_w: self.scrx= (self.max_w-self.w)*self.scale
        if self.scry < 0: self.scry= 0
        if self.scry/self.scale+self.h > self.max_h: self.scry= (self.max_h-self.h)*self.scale
    
    def redraw(self):
        self.queue_draw()
        
    def screen_to_grid(self, x, y):
        '''converts a screen coordinate to a grid relative coordinate
        '''
        gx= int((x+self.scrx)/self.scale)-self.relx
        gy= int((self.window_h-y+self.scry)/self.scale)-self.rely
        return (gx, gy)
    
    def screen_to_work(self, x, y):
        '''converts a screen coordinate to a work coordinate (from absolute 0, 0)
        '''
        wx= int((x+self.scrx)/self.scale)
        wy= int((self.window_h-y+self.scry)/self.scale)
        return (wx, wy)

    def get_snap(self, x, y):
        return (0, 0)
        
    def set_rel_origin(self, x, y):
        self.relx= x
        self.rely= y
        self.redraw()
    
    def pam_to(self, wx, wy):
        '''center window on x,y
        '''
        self.scrx= wx*self.scale-(self.window_w/2)
        self.scry= wy*self.scale-self.window_h+(self.window_h/2)
        self._adjust_pam()
        self.redraw()
        
    def relative_pam(self, dx, dy):
        '''apply dx,dy to current pam
        '''
        #TODO it could run a thread to animate this...
        self.scrx+= dx
        self.scry+= dy
        self._adjust_pam()
        self.redraw()
        

class PCBEntity(Grid):
    def __init__(self, db, pcbName, statusbar):
        Grid.__init__(self)
        self.statusbar= statusbar

        canvas= gtk.DrawingArea()
        canvas.set_flags(gtk.CAN_FOCUS)
        canvas.set_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | \
                                                   gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.KEY_PRESS_MASK)
        canvas.connect('event', self.on_canvas_event)
        canvas.grab_focus()
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
        self.cr.arc(100, 100, 50, 0, pi+1)
        self.cr.stroke()
        self.cr.arc(300, 300, 40, 0, 2*pi)
        self.cr.stroke()

        self.cr.arc(7300, 7300, 40, 0, 2 * pi)
        self.cr.arc(2300, 2300, 40, 0, 2 * pi)
        self.cr.arc(4300, 4300, 40, 0, 2 * pi)
        self.cr.fill()

        self.cr.set_source_rgba(.1, 1, 0.1, .5)
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
            self.statusbar.push(0, 'x:%d y:%d (%d-%d - %d-%d - %d-%d)' % (p[0], p[1], event.x, event.y, self.scrx, self.scry, self.relx, self.rely))

        elif event.type is gtk.gdk.BUTTON_PRESS:
            pass

        elif event.type is gtk.gdk.BUTTON_RELEASE:
            pass


class XEDA:
    def __init__(self):
        builder= gtk.Builder()
        builder.add_objects_from_file("main.glade", ('window_main', 'liststore1', 'action_undo') )
        builder.connect_signals(self)
        #builder.get_object("windowMain").show()
        self.statusbar= builder.get_object('statusbar1')
        self.notebook_main= builder.get_object('notebook_main')
        
        self.on_toolbutton1_clicked(None)

    def gtk_main_quit(self, widget):
        print 'saindo foraaaa'
        sys.exit(0)
        
    def on_menu_about_activate(self, m):
        builder= gtk.Builder()
        builder.add_objects_from_file("main.glade", ('window_about', ) )
        builder.connect_signals(self)
        builder.get_object("window_about").show()
        
    def on_window_about_response(self, w, b):
        w.destroy()

    def on_imagemenuitem1_activate(self, a):
        print 'aqui foi o activate'
        
    def on_button1_clicked(self, a):
        print a
        
    def on_button2_clicked(self, a):
        pass

    def on_button3_clicked(self, a):
        pass

    def on_toolbutton1_clicked(self, a):
        self.bla= PCBEntity('db', 'placa', self.statusbar)
        tab_label = gtk.Label('nome')
        self.notebook_main.append_page(self.bla, tab_label)
        #notebook.show_all()

    def on_toolbutton3_clicked(self, a):
        pass

    def on_action_undo_activate(self, a):
        self.bla.items.undo()
        self.bla.redraw()
        

xeda= XEDA()
gtk.main()

