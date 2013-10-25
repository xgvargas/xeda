
class ObjectXEDA:
    kind= -1
    name= ''
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
    
    def is_over(self, x, y):
        '''responde se a coordenada indicado esta sobre esse objeto
        '''
        pass
        
    def start_drag(self):
        pass
        
    def stop_drag(self):
        pass



class SCHObject(ObjectXEDA):
    '''
componentes (descritos aqui)
fios
juncoes
power
portas (entre folhas)
net names
textos livres
caixa de texto
bus
entradas de bus
graficos (linhas, circulos, retangulos, arcos, poligonos)
    '''
    def __init__(self):
        self.pn= '74hc123'
        self.ref= 'U12'
        self.comment= '74HC123'
        #parts deveria ser uma lista de parts do componentes, cada lista com uma lista dos pinos desta parte
        #seguida dos graficos dessa parte
        self.parts= 2
        self.pins= [[(0, 0, 'bla', 'id', 'angle', 'clk', 'dot', 'show-name', 'show-id'), (50, 0, 'ble', 'id', 'angle', 'clk', 'dot', 'show-name', 'show-id'), (200, 0, 'bli', 'id', 'angle', 'clk', 'dot', 'show-name', 'show-id')],
                    [(0, 100, 'da', 'id', 'angle', 'clk', 'dot', 'show-name', 'show-id'), (50, 150, 'de', 'id', 'angle', 'clk', 'dot', 'show-name', 'show-id'), (200, 300, 'di', 'id', 'angle', 'clk', 'dot', 'show-name', 'show-id'), (250, 50, 'do', 'id', 'angle', 'clk', 'dot', 'show-name', 'show-id')]
                    ]
        self.partId= 0
        self.drawns= []
        self.foots= ['so16', 'so16.3', 'dip16']
        self.footId= 1
    
    def draw(self):
        pass



class PCBObject(ObjectXEDA):
    '''
componentes (como descritos aqui)
pad isolado
via
linhas
arcos (partindo do centro e dos extermos)
textos
    '''
    def __init__(self):
        self.foot= 'sop23'
        self.ref= 'U12'
        self.comment= 'teste'
        self.pads= [(0, 0, 'id', 'quadrado', 'w', 'h', 'top', 'furo-diametro', 'net-name', 'mask'),
                    (25, 0, 'id', 'quadrado', 'w', 'h', 'top', 'furo-diametro', 'net-name', 'mask')
                    ]
        self.drawns= []
        
    def draw(self):
        pass
        