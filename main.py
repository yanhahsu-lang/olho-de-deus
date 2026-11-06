from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.clock import mainthread, Clock
import threading
import math
import g4f
import pyttsx3

# Inicialização do motor de voz
try:
    engine = pyttsx3.init()
except Exception:
    engine = None

# Componente Visual Interativo: HUD e Mapa Global do Olho de Deus
class MapaInterativoOlhoDeDeus(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alvos = []
        self.graus_rotacao = 0
        self.texto_coordenadas = "CLIQUE OU ARRASTE NO MAPA PARA RASTREAR..."
        
        self.bind(on_touch_down=self.interagir_mapa)
        self.bind(on_touch_move=self.interagir_mapa)
        
        Clock.schedule_interval(self.atualizar_visual, 1 / 30.0)

    def interagir_mapa(self, instance, touch):
        if self.collide_point(*touch.pos):
            lat = (touch.y - self.center_y) / (self.height / 180) if self.height else 0
            lon = (touch.x - self.center_x) / (self.width / 360) if self.width else 0
            self.texto_coordenadas = f"SATÉLITE RASTREADO: LAT {lat:.4f} | LON {lon:.4f}"
            self.alvos = [{"pos": touch.pos, "duracao": 30}]
            return True
        return False

    def atualizar_visual(self, dt):
        self.graus_rotacao = (self.graus_rotacao + 2) % 360
        self.canvas.clear()
        cx, cy = self.center_x, self.center_y
        raio_max = min(self.width, self.height) * 0.45
        
        with self.canvas:
            Color(0.01, 0.04, 0.02, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Anéis do Radar
            Color(0.0, 1.0, 0.5, 0.2)
            for i in range(1, 5):
                dist = (raio_max / 4) * i
                Ellipse(pos=(cx - dist, cy - dist), size=(dist * 2, dist * 2))
            
            Line(points=[self.x, cy, self.x + self.width, cy], width=1)
            Line(points=[cx, self.y, cx, self.y + self.height], width=1)
            
            # Linha Varredura Sci-Fi
            Color(0.0, 1.0, 0.5, 0.6)
            rad = math.radians(self.graus_rotacao)
            rx = cx + raio_max * math.cos(rad)
            ry = cy + raio_max * math.sin(rad)
            Line(points=[cx, cy, rx, ry], width=1.5)
            
            # Alvos Rastreamentos Interativos
            for alvo in self.alvos[:]:
                pos_x, pos_y = alvo["pos"]
                Color(1.0, 0.2, 0.2, alvo["duracao"] / 30.0)
                Line(circle=(pos_x, pos_y, 12), width=1.5)
                Line(points=[pos_x - 18, pos_y, pos_x + 18, pos_y], width=1)
                Line(points=[pos_x, pos_y - 18, pos_x, pos_y + 18], width=1)
                alvo["duracao"] -= 0.5
                if alvo["duracao"] <= 0:
                    self.alvos.remove(alvo)

# Estética Cyberpunk / Hacker
class PainelHackerTanjiro(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.02, 0.05, 0.03, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            Color(0.0, 1.0, 0.5, 0.8)
            self.line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)
        self.bind(size=self._atualizar, pos=self._atualizar)

    def _atualizar(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
        self.line.rectangle = (instance.x, instance.y, instance.width, instance.height)

class OlhoDeDeusApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=12, spacing=10)
        
        header = Label(
            text='[ KAMADO_CORE // TERMINAL HACKER - OLHO DE DEUS v5.0 ]',
            size_hint_y=0.07,
            color=(0.0, 1.0, 0.5, 1),
            font_size='16sp',
            bold=True
        )
        root.add_widget(header)

        corpo = BoxLayout(orientation='horizontal', spacing=10)

        # Mascote Tanjiro
        card_mascote = PainelHackerTanjiro(orientation='vertical', padding=10, size_hint_x=0.35)
        avatar_title = Label(
            text='[ MASCOTE ]\nTANJIRO KAMADO',
            color=(0.0, 1.0, 0.5, 1),
            bold=True,
            halign='center',
            size_hint_y=0.2
        )
        card_mascote.add_widget(avatar_title)

        self.status_mascote = Label(
            text=(
                "   /\\_/\\\n"
                "  ( o.o )\n"
                "   > ^ <\n\n"
                "[ MASCOTE IA ]\n"
                "Status: Online\n"
                "Modo: Hacker\n"
                "Olho de Deus:\n"
                "Pronto"
            ),
            color=(0.4, 1.0, 0.6, 1),
            halign='center',
            valign='middle'
        )
        card_mascote.add_widget(self.status_mascote)
        corpo.add_widget(card_mascote)

        # Terminal Principal
        self.terminal = PainelHackerTanjiro(orientation='vertical', padding=10, size_hint_x=0.65)
        self.console_label = Label(
            text=(
                "tanjiro@olho-de-deus:~$ Sistema pronto.\n"
                "tanjiro@olho-de-deus:~$ Escreva o comando e ative o Olho de Deus."
            ),
            size_hint=(1, 1),
            halign='left',
            valign='top',
            color=(0.0, 1.0, 0.5, 1)
        )
        self.console_label.bind(size=self._ajustar_texto)
        self.terminal.add_widget(self.console_label)
        corpo.add_widget(self.terminal)

        root.add_widget(corpo)

        # Entrada e Botão
        controles = BoxLayout(orientation='horizontal', size_hint_y=None, height=48, spacing=8)
        self.input_texto = TextInput(
            hint_text='>> Digite sua ordem para a IA...',
            multiline=False,
            background_color=(0.03, 0.08, 0.05, 1),
            foreground_color=(0.0, 1.0, 0.5, 1),
            cursor_color=(0.0, 1.0, 0.5, 1),
            hint_text_color=(0.2, 0.5, 0.3, 1)
        )
        controles.add_widget(self.input_texto)

        btn_olho = Button(
            text='[ EXECUTAR ] OLHO DE DEUS',
            size_hint_x=None,
            width=230,
            background_color=(0.0, 0.9, 0.5, 1),
            color=(0, 0, 0, 1),
            bold=True
        )
        btn_olho.bind(on_press=self.abrir_olho_de_deus)
        controles.add_widget(btn_olho)

        root.add_widget(controles)
        return root

    def _ajustar_texto(self, instance, value):
        self.console_label.text_size = (instance.width, None)

    def abrir_olho_de_deus(self, instance):
        texto = self.input_texto.text.strip()
        if not texto:
            return

        conteudo_popup = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.mapa_interativo = MapaInterativoOlhoDeDeus()
        conteudo_popup.add_widget(self.mapa_interativo)

        self.coordenadas_label = Label(
            text='RASTREAMENTO GLOBAL: CLIQUE NO MAPA...',
            size_hint_y=0.1,
            color=(0.0, 1.0, 0.5, 1),
            bold=True
        )
        conteudo_popup.add_widget(self.coordenadas_label)

        self.popup_label = Label(
            text='[ TANJIRO // OLHO DE DEUS ] > Processando análise com IA...',
            size_hint_y=0.35,
            halign='left',
            valign='top',
            color=(0.0, 1.0, 0.6, 1)
        )
        self.popup_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
        conteudo_popup.add_widget(self.popup_label)

        def monitorar_coordenadas(dt):
            if hasattr(self, 'mapa_interativo'):
                self.coordenadas_label.text = self.mapa_interativo.texto_coordenadas
        Clock.schedule_interval(monitorar_coordenadas, 1 / 10.0)

        self.popup = Popup(
            title='[ GOD_EYE // INTERACTION MAP ]',
            content=conteudo_popup,
            size_hint=(0.95, 0.95),
            background_color=(0.0, 0.1, 0.05, 0.96)
        )
        self.popup.open()

        self.console_label.text += f"\ntanjiro@olho-de-deus:~$ Ordem executada: '{texto}'"
        self.input_texto.text = ""

        threading.Thread(target=self.processar_resposta, args=(texto,)).start()

    def falar(self, texto):
        if engine:
            try:
                engine.say(texto)
                engine.runAndWait()
            except Exception:
                pass

    def processar_resposta(self, pergunta):
        try:
            prompt_tanjiro = f"Você é Tanjiro Kamado no modo IA Hacker com a tecnologia Olho de Deus. Responda como o mascote da IA: {pergunta}"
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=[{"role": "user", "content": pergunta}],
            )
            resposta = str(response)
            self.atualizar_popup(f"[ OLHO DE DEUS > RESPOSTA FINAL ]\n\n{resposta}")
            threading.Thread(target=self.falar, args=(resposta,)).start()
        except Exception as err:
            self.atualizar_popup(f"[ ERRO ] > Falha na resposta da IA: {err}")

    @mainthread
    def atualizar_popup(self, texto):
        self.popup_label.text = texto

if __name__ == '__main__':
    OlhoDeDeusApp().run()
