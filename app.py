import customtkinter as ctk
from PIL import Image
import os
from ctypes import windll
import win32gui
import win32api
import win32con

# Estilos do Windows necessários para integração com a barra de tarefas
GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern App")
        self.geometry("1000x700")
        self.resizable(False, False)
        
        # Remove a barra de título e configura a janela
        self.overrideredirect(True)
        self.after(1, lambda: self.set_appwindow())
        
        # Adiciona as bordas arredondadas
        self.after(1, self.set_rounded_corners)
        
        # Variável para controlar estado da janela
        self.minimized = False
        
        # Configurando o grid principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header frame com título e botões
        self.header_frame = ctk.CTkFrame(self, fg_color="#2B2C35", height=70, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Frame para título e botões de navegação
        self.nav_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.nav_container.grid(row=0, column=0, sticky="w", padx=30, pady=20)
        
        # Título Settings
        self.settings_label = ctk.CTkLabel(self.nav_container, text="Auto-SAS", 
                                         font=ctk.CTkFont(size=24, weight="bold"))
        self.settings_label.grid(row=0, column=0, sticky="w", padx=(0, 50))
        
        # Botões de navegação
        self.create_tab_button("Profile", 1)
        self.create_tab_button("Features", 2)
        self.create_tab_button("Subscriptions", 3, active=True)
        self.create_tab_button("Integrations", 4)
        
        # Frame para os botões de controle da janela
        self.window_controls = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.window_controls.grid(row=0, column=1, sticky="e", padx=15)
        
        # Botões de controle
        self.minimize_button = ctk.CTkButton(self.window_controls, text="_", width=35,
                                           command=self.minimize_window, fg_color="#363841",
                                           hover_color="#404149")
        self.minimize_button.grid(row=0, column=0, padx=3)
        
        self.close_button = ctk.CTkButton(self.window_controls, text="×", width=35,
                                        command=self.quit, fg_color="#363841",
                                        hover_color="red")
        self.close_button.grid(row=0, column=1, padx=3)
        
        # Frame scrollável apenas para os cards
        self.cards_scroll = ctk.CTkScrollableFrame(self, fg_color="#2B2C35", corner_radius=0)
        self.cards_scroll.grid(row=1, column=0, sticky="nsew", pady=0)
        self.cards_scroll.grid_columnconfigure(0, weight=1)
        self.cards_scroll.grid_columnconfigure(1, weight=1)
        
        # Criar 10 cards em um layout 2x5
        for i in range(10):
            row = i // 2
            col = i % 2
            self.create_task_card(
                f"Task {i+1}",
                "Diário" if i % 2 == 0 else "Semanal",
                f"0{i+1}/01/2025",
                f"{15+i}/01/2025",
                f"Usuário {i+1}",
                row,
                col
            )
        
        # Bind de eventos para mover a janela
        self.header_frame.bind("<Button-1>", self.start_move)
        self.header_frame.bind("<B1-Motion>", self.do_move)
        
        # Bind para restaurar a janela
        self.bind("<Map>", self.frame_mapped)

    def set_rounded_corners(self):
        # Obtém o handle da janela
        hwnd = windll.user32.GetParent(self.winfo_id())
        
        # Obtém as dimensões da janela
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        
        # Cria uma região arredondada
        region = win32gui.CreateRoundRectRgn(0, 0, width, height, 20, 20)
        
        # Aplica a região à janela
        win32gui.SetWindowRgn(hwnd, region, True)
        
    def set_appwindow(self):
        hwnd = windll.user32.GetParent(self.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        self.withdraw()
        self.after(1, self.deiconify)
        
    def minimize_window(self):
        self.minimized = True
        self.withdraw()
        self.overrideredirect(False)
        self.iconify()
    
    def frame_mapped(self, event=None):
        if self.minimized:
            self.overrideredirect(True)
            self.minimized = False
            self.set_appwindow()
            # Reaplica as bordas arredondadas quando a janela é restaurada
            self.after(1, self.set_rounded_corners)
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
            
    def create_tab_button(self, text, col, active=False):
        fg_color = "#363841" if active else "transparent"
        btn = ctk.CTkButton(self.nav_container, text=text, 
                           fg_color=fg_color, hover_color="#404149",
                           height=35, width=120)
        btn.grid(row=0, column=col, padx=5)
        return btn
    
    def create_task_card(self, titulo, periodo, data_inicio, data_fim, proprietario, row, col):
        # Card frame com corner radius aumentado
        card = ctk.CTkFrame(self.cards_scroll, fg_color="#363841", corner_radius=20)
        card.grid(row=row, column=col, padx=15, pady=8, sticky="ew")
        
        # Configuração do grid do card
        card.grid_columnconfigure(0, weight=1)  # Coluna das informações
        card.grid_columnconfigure(1, weight=0)  # Coluna dos botões
        
        # Frame para informações
        info_container = ctk.CTkFrame(card, fg_color="transparent")
        info_container.grid(row=0, column=0, sticky="nsew", padx=(20,0), pady=15)
        
        # Título
        title = ctk.CTkLabel(info_container, text=titulo, 
                            font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0,5))
        
        # Informações da task
        info_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        info_frame.grid(row=1, column=0, sticky="ew")
        
        # Labels de informação
        labels = [
            f"Período: {periodo}",
            f"Início: {data_inicio}",
            f"Fim: {data_fim}",
            f"Responsável: {proprietario}"
        ]
        
        for idx, text in enumerate(labels):
            label = ctk.CTkLabel(info_frame, text=text, text_color="gray70")
            label.grid(row=idx, column=0, sticky="w", pady=2)
        
        # Frame para botões
        buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, padx=20, pady=15, sticky="ns")
        
        # Botões de ação
        button_names = ["Edit", "Delete", "View"]
        for idx, name in enumerate(button_names):
            btn = ctk.CTkButton(buttons_frame, text=name, width=120, height=30,
                              fg_color="#2B2C35", hover_color="#404149")
            btn.grid(row=idx, column=0, pady=5)

if __name__ == "__main__":
    app = App()
    app.lift()
    app.attributes('-topmost',True)
    app.after_idle(app.attributes,'-topmost',False)
    app.mainloop()
