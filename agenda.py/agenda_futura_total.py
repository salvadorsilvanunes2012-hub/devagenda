import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, QObject, pyqtSlot

FICHEIRO_DADOS = "dados_agenda_futura_v3.json"

def carregar_dados_reais():
    if os.path.exists(FICHEIRO_DADOS):
        try:
            with open(FICHEIRO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "pagina_atual": "schedule",
        "tarefas": [
            {"texto": "Bug fixes", "concluido": True},
            {"texto": "Refactor code", "concluido": True},
            {"texto": "Database migration", "concluido": False},
            {"texto": "Implement feature", "concluido": False}
        ],
        "snippet": "async FetchData() {\n  const res = await api.get();\n  return res.status;\n}",
        "eventos": [
            {"dia": "Tue", "hora": "8:00", "titulo": "Meeting", "duracao": "8:00 - 9:00", "cor": "#06b6d4"},
            {"dia": "Tue", "hora": "10:00", "titulo": "Design Review", "duracao": "10:00 - 11:30", "cor": "#8b5cf6"},
            {"dia": "Fri", "hora": "8:00", "titulo": "JS Engine", "duracao": "8:00 - 9:00", "cor": "#10b981"},
            {"dia": "Fri", "hora": "10:00", "titulo": "C++ Refactor", "duracao": "10:00 - 11:00", "cor": "#ef4444"},
            {"dia": "Fri", "hora": "12:00", "titulo": "Code Review", "duracao": "12:00 - 14:00", "cor": "#8b5cf6"}
        ],
        "habitos": {
            "titulo": "Corrida Semanal",
            "meta_dias": 25,
            "dias_marcados": [],
            "dias_extras_recuperacao": 0,
            "concluido": False
        }
    }

def guardar_dados_reais(dados):
    with open(FICHEIRO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

class Bridge(QObject):
    def __init__(self, janela_principal):
        super().__init__()
        self.janela = janela_principal

    @pyqtSlot(str)
    def mudarPagina(self, pagina):
        dados = carregar_dados_reais()
        dados["pagina_atual"] = pagina
        guardar_dados_reais(dados)
        self.janela.recarregar_interface()

    @pyqtSlot(str, bool)
    def atualizarTarefa(self, texto_tarefa, estado):
        dados = carregar_dados_reais()
        for t in dados["tarefas"]:
            if t["texto"] == texto_tarefa:
                t["concluido"] = estado
        guardar_dados_reais(dados)

    @pyqtSlot(str)
    def adicionarTarefa(self, texto_tarefa):
        if texto_tarefa.strip():
            dados = carregar_dados_reais()
            dados["tarefas"].append({"texto": texto_tarefa, "concluido": False})
            guardar_dados_reais(dados)
            self.janela.recarregar_interface()

    @pyqtSlot(str)
    def guardarSnippet(self, novo_codigo):
        dados = carregar_dados_reais()
        dados["snippet"] = novo_codigo
        guardar_dados_reais(dados)

    @pyqtSlot(str, str, str, str, str)
    def adicionarEvento(self, dia, hora, titulo, duracao, cor):
        if titulo.strip():
            dados = carregar_dados_reais()
            dados["eventos"].append({
                "dia": dia,
                "hora": hora,
                "titulo": titulo,
                "duracao": duracao if duracao else f"{hora} - ...",
                "cor": cor if cor else "#8b5cf6"
            })
            guardar_dados_reais(dados)
            self.janela.recarregar_interface()

    @pyqtSlot(int)
    def alternarDiaHabito(self, dia):
        dados = carregar_dados_reais()
        if "habitos" not in dados:
            dados["habitos"] = {"titulo": "Nova Meta", "meta_dias": 25, "dias_marcados": [], "dias_extras_recuperacao": 0, "concluido": False}
        
        habitos = dados["habitos"]
        dias = habitos["dias_marcados"]
        
        if dia in dias:
            dias.remove(dia)
        else:
            dias.append(dia)
        
        # Verificar se atingiu a meta total (Meta base + dias de recuperação adicionados)
        meta_total = habitos.get("meta_dias", 25) + habitos.get("dias_extras_recuperacao", 0)
        if len(dias) >= meta_total:
            habitos["concluido"] = True
        else:
            habitos["concluido"] = False

        guardar_dados_reais(dados)
        self.janela.recarregar_interface()

    @pyqtSlot(str)
    def atualizarTituloHabito(self, novo_titulo):
        dados = carregar_dados_reais()
        if "habitos" not in dados:
            dados["habitos"] = {"dias_marcados": [], "meta_dias": 25, "dias_extras_recuperacao": 0}
        dados["habitos"]["titulo"] = novo_titulo
        guardar_dados_reais(dados)

    @pyqtSlot(int)
    def adicionarDiasRecuperacao(self, qtd):
        dados = carregar_dados_reais()
        if "habitos" in dados:
            dados["habitos"]["dias_extras_recuperacao"] = dados["habitos"].get("dias_extras_recuperacao", 0) + qtd
            guardar_dados_reais(dados)
            self.janela.recarregar_interface()

    @pyqtSlot(str)
    def reiniciarCicloHabitos(self, novo_titulo):
        dados = carregar_dados_reais()
        dados["habitos"] = {
            "titulo": novo_titulo if novo_titulo.strip() else "Nova Rotina",
            "meta_dias": 25,
            "dias_marcados": [],
            "dias_extras_recuperacao": 0,
            "concluido": False
        }
        guardar_dados_reais(dados)
        self.janela.recarregar_interface()

def gerar_html():
    dados = carregar_dados_reais()
    pagina = dados.get("pagina_atual", "schedule")
    
    agora = datetime.now()
    meses_pt = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    mes_atual_str = f"{meses_pt[agora.month - 1]} {agora.year}"

    html_tarefas = ""
    for t in dados["tarefas"]:
        checked = "checked" if t["concluido"] else ""
        style = "text-decoration: line-through; color: var(--text-muted);" if t["concluido"] else ""
        html_tarefas += f"""
        <div class="task-item">
            <input type="checkbox" {checked} onclick="mudarEstado('{t['texto']}', this.checked)">
            <span style="{style}">{t['texto']}</span>
        </div>
        """

    conteudo_principal = ""

    if pagina == "schedule":
        dias_semana = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        colunas_html = ""
        for dia in dias_semana:
            cartoes_dia = ""
            for ev in dados["eventos"]:
                if ev["dia"] == dia:
                    cartoes_dia += f"""
                    <div class="card" style="border-left-color: {ev['cor']};">
                        <div class="card-title">{ev['titulo']}</div>
                        <div class="card-time">{ev['duracao']}</div>
                    </div>
                    """
            colunas_html += f"""
            <div class="day-column" onclick="abrirModalAgendar('{dia}')">
                <div class="day-header">{dia}</div>
                {cartoes_dia}
                <div class="add-slot-hint">+ Agendar</div>
            </div>
            """

        conteudo_principal = f"""
        <div class="main-content">
            <div class="header">
                <h1>Schedule &bull; <span style="color: var(--accent-purple);">{mes_atual_str}</span></h1>
                <span style="color: var(--text-muted); font-size: 0.9rem;">⚡ DevAgenda Pro (Ativo)</span>
            </div>
            <div class="calendar-grid">
                <div class="time-col">
                    <span>8:00</span><span>10:00</span><span>12:00</span><span>14:00</span><span>16:00</span><span>18:00</span>
                </div>
                {colunas_html}
            </div>
        </div>
        """
    elif pagina == "calendario_mes":
        dias_mes_html = ""
        for d in range(1, 32):
            dias_mes_html += f"""<div class="month-day-box"><span>{d}</span></div>"""

        conteudo_principal = f"""
        <div class="main-content">
            <div class="header">
                <h1>Calendário Mensal &bull; <span style="color: var(--accent-purple);">{mes_atual_str}</span></h1>
            </div>
            <div class="month-grid">
                {dias_mes_html}
            </div>
        </div>
        """
    elif pagina == "habitos":
        habitos_dados = dados.get("habitos", {"titulo": "Corrida Semanal", "meta_dias": 25, "dias_marcados": [], "dias_extras_recuperacao": 0, "concluido": False})
        titulo_habito = habitos_dados.get("titulo", "Corrida Semanal")
        meta_base = habitos_dados.get("meta_dias", 25)
        dias_extras = habitos_dados.get("dias_extras_recuperacao", 0)
        dias_marcados = habitos_dados.get("dias_marcados", [])
        concluido = habitos_dados.get("concluido", False)

        total_dias_render = meta_base + dias_extras

        dias_habito_html = ""
        for d in range(1, total_dias_render + 1):
            is_checked = d in dias_marcados
            box_class = "habit-box checked" if is_checked else "habit-box"
            dias_habito_html += f"""
            <div class="{box_class}" onclick="alternarDia({d})">
                <span class="day-num">Dia {d}</span>
            </div>
            """

        painel_conclusao_html = ""
        if concluido:
            painel_conclusao_html = f"""
            <div style="background: rgba(16, 185, 129, 0.15); border: 2px solid var(--accent-green); padding: 20px; border-radius: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="color: var(--accent-green); font-size: 1.4rem; margin-bottom: 5px;">🎉 Missão cumprida! Parabéns!</h2>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">Completaste todos os dias com sucesso. Pronto para o próximo desafio?</p>
                </div>
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="novoNomeRotina" placeholder="Nome da nova rotina..." style="background: var(--bg-main); border: 1px solid var(--border-color); color: white; padding: 10px; border-radius: 8px; outline: none; width: 220px;">
                    <button onclick="reiniciarCiclo()" style="background: var(--accent-green); color: #0d0f12; border: none; padding: 10px 20px; font-weight: bold; border-radius: 8px; cursor: pointer;">Recomeçar Ciclo</button>
                </div>
            </div>
            """

        conteudo_principal = f"""
        <div class="main-content">
            <div class="header">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <h1>Meta & Hábitos:</h1>
                    <input type="text" value="{titulo_habito}" oninput="atualizarTitulo(this.value)" style="background: var(--bg-card); border: 1px solid var(--border-color); color: var(--accent-green); font-size: 1.3rem; font-weight: bold; padding: 5px 12px; border-radius: 8px; outline: none; width: 280px;">
                </div>
                <div style="display: flex; gap: 15px; align-items: center;">
                    <span style="color: var(--text-muted); font-size: 0.9rem;">Meta: <b>{len(dias_marcados)} / {total_dias_render} dias</b></span>
                    <button onclick="adicionarRecuperacaoPrompt()" style="background: var(--bg-card); border: 1px solid var(--accent-orange); color: var(--accent-orange); padding: 6px 12px; border-radius: 8px; cursor: pointer; font-size: 0.8rem; font-weight: bold;" title="Adicionar dias de recuperação se faltaste">⚠️ Adicionar Dias Extra</button>
                </div>
            </div>

            {painel_conclusao_html}

            <div class="habit-grid">
                {dias_habito_html}
            </div>
        </div>
        """
    elif pagina == "snippets":
        conteudo_principal = f"""
        <div class="main-content">
            <div class="header">
                <h1>Painel de Código & Snippets</h1>
            </div>
            <div class="code-card" style="height: 400px;">
                <textarea style="height: 100%; font-size: 1rem;" oninput="guardarSnippet(this.value)">{dados['snippet']}</textarea>
            </div>
        </div>
        """
    else:
        conteudo_principal = f"""
        <div class="main-content">
            <div class="header">
                <h1>Definições do Sistema</h1>
            </div>
            <p style="color: var(--text-muted);">Mês ativo do sistema: <b>{mes_atual_str}</b>. Base de dados local ligada.</p>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>DevAgenda Pro</title>
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <style>
            :root {{
                --bg-main: #0d0f12;
                --bg-card: #161920;
                --bg-card-hover: #1e222b;
                --border-color: #262c38;
                --text-main: #f3f4f6;
                --text-muted: #9ca3af;
                --accent-purple: #8b5cf6;
                --accent-blue: #3b82f6;
                --accent-green: #10b981;
                --accent-orange: #f59e0b;
            }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }}
            body {{ background-color: var(--bg-main); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; }}
            
            .sidebar-left {{
                width: 70px; background-color: #090a0d; border-right: 1px solid var(--border-color);
                display: flex; flex-direction: column; align-items: center; padding-top: 20px; gap: 20px;
            }}
            .sidebar-icon {{
                width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center;
                justify-content: center; color: var(--text-muted); cursor: pointer; transition: 0.2s; font-size: 1.2rem;
            }}
            .sidebar-icon:hover, .sidebar-icon.active {{ background-color: var(--bg-card); color: var(--accent-purple); }}

            .main-content {{ flex: 1; display: flex; flex-direction: column; padding: 20px; overflow-y: auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }}
            .header h1 {{ font-size: 1.5rem; font-weight: 600; }}

            .calendar-grid {{ display: grid; grid-template-columns: 80px repeat(6, 1fr); gap: 12px; flex: 1; }}
            .time-col {{ display: flex; flex-direction: column; gap: 75px; color: var(--text-muted); font-size: 0.85rem; padding-top: 15px; }}
            
            .day-column {{
                background-color: rgba(22, 25, 32, 0.4); border-radius: 12px; padding: 10px;
                border: 1px solid rgba(38, 44, 56, 0.4); display: flex; flex-direction: column; gap: 10px;
                min-height: 550px; cursor: pointer; transition: background 0.2s; position: relative;
            }}
            .day-column:hover {{ background-color: rgba(22, 25, 32, 0.7); border-color: var(--accent-purple); }}
            .day-header {{ text-align: center; font-size: 0.9rem; font-weight: 600; color: var(--text-muted); padding-bottom: 8px; border-bottom: 1px solid var(--border-color); }}
            .add-slot-hint {{ position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); font-size: 0.75rem; color: var(--text-muted); opacity: 0.5; }}
            .day-column:hover .add-slot-hint {{ opacity: 1; color: var(--accent-purple); }}

            .month-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; }}
            .month-day-box {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; min-height: 90px; padding: 10px; }}
            .month-day-box span {{ font-weight: bold; color: var(--accent-purple); }}

            /* HÁBITOS / TRACKER GRID */
            .habit-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 12px; }}
            .habit-box {{
                background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px;
                min-height: 90px; padding: 12px; cursor: pointer; position: relative; transition: 0.2s;
                overflow: hidden; display: flex; align-items: flex-start; justify-content: flex-end;
            }}
            .habit-box:hover {{ border-color: var(--accent-green); background: var(--bg-card-hover); }}
            .habit-box .day-num {{ font-weight: bold; color: var(--text-muted); font-size: 0.9rem; z-index: 2; transition: color 0.2s; }}
            
            /* ESTILO CINEMATOGRÁFICO DE PREENCHIMENTO TOTAL */
            .habit-box.checked {{
                background-color: var(--accent-green);
                border-color: var(--accent-green);
            }}
            .habit-box.checked .day-num {{
                color: #0d0f12;
            }}

            .card {{ background-color: var(--bg-card); border-radius: 10px; padding: 12px; border-left: 4px solid var(--accent-purple); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }}
            .card-title {{ font-size: 0.9rem; font-weight: 600; margin-bottom: 4px; }}
            .card-time {{ font-size: 0.75rem; color: var(--text-muted); }}

            .sidebar-right {{ width: 340px; background-color: #090a0d; border-left: 1px solid var(--border-color); padding: 20px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }}
            .section-title {{ font-size: 0.85rem; font-weight: 600; color: var(--text-muted); letter-spacing: 1px; margin-bottom: 10px; text-transform: uppercase; }}
            .code-card {{ background-color: var(--bg-card); border-radius: 12px; padding: 15px; border: 1px solid var(--border-color); }}
            textarea {{ width: 100%; background: transparent; border: none; color: #61afef; font-family: 'Courier New', monospace; font-size: 0.8rem; resize: none; height: 70px; outline: none; }}
            
            .task-item {{ display: flex; align-items: center; gap: 10px; background-color: var(--bg-card); padding: 10px 12px; border-radius: 8px; margin-bottom: 8px; font-size: 0.85rem; border: 1px solid var(--border-color); }}
            .task-item input[type="checkbox"] {{ accent-color: var(--accent-purple); width: 16px; height: 16px; cursor: pointer; }}
            .add-task-box {{ display: flex; gap: 5px; margin-bottom: 10px; }}
            .add-task-box input {{ flex: 1; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 10px; color: white; outline: none; }}
            .add-task-box button {{ background: var(--accent-purple); color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-weight: bold; }}

            .deadline-card {{ background-color: var(--bg-card); border-radius: 10px; padding: 12px; margin-bottom: 8px; border: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; }}
            .deadline-info h4 {{ font-size: 0.85rem; margin-bottom: 2px; }}
            .deadline-info p {{ font-size: 0.75rem; color: var(--text-muted); }}
            .dot {{ width: 8px; height: 8px; border-radius: 50%; background-color: var(--accent-green); }}

            /* MODAL */
            #modalOverlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); justify-content: center; align-items: center; z-index: 1000; }}
            .modal {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 24px; width: 360px; display: flex; flex-direction: column; gap: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
            .modal h3 {{ font-size: 1.1rem; color: var(--text-main); }}
            .modal label {{ font-size: 0.8rem; color: var(--text-muted); }}
            .modal input, .modal select {{ background: #0d0f12; border: 1px solid var(--border-color); border-radius: 8px; padding: 8px 12px; color: white; outline: none; font-size: 0.9rem; }}
            .modal-buttons {{ display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px; }}
            .modal-buttons button {{ padding: 8px 16px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer; }}
            .btn-cancel {{ background: transparent; color: var(--text-muted); }}
            .btn-save {{ background: var(--accent-purple); color: white; }}
        </style>
    </head>
    <body>

        <div class="sidebar-left">
            <div class="sidebar-icon {'active' if pagina == 'schedule' else ''}" onclick="mudarPagina('schedule')" title="Dashboard / Schedule">📊</div>
            <div class="sidebar-icon {'active' if pagina == 'calendario_mes' else ''}" onclick="mudarPagina('calendario_mes')" title="Calendário Mensal">📅</div>
            <div class="sidebar-icon {'active' if pagina == 'habitos' else ''}" onclick="mudarPagina('habitos')" title="Tracker de Metas e Hábitos">🎯</div>
            <div class="sidebar-icon {'active' if pagina == 'snippets' else ''}" onclick="mudarPagina('snippets')" title="Snippets de Código">⚡</div>
            <div class="sidebar-icon {'active' if pagina == 'settings' else ''}" onclick="mudarPagina('settings')" title="Definições">⚙️</div>
        </div>

        {conteudo_principal}

        <div class="sidebar-right">
            <div>
                <div class="section-title">Tasks (Snippet Ativo)</div>
                <div class="code-card">
                    <textarea id="snippetInput" oninput="guardarSnippet(this.value)">{dados['snippet']}</textarea>
                </div>
            </div>

            <div>
                <div class="section-title">Reminders & To-Do</div>
                <div class="add-task-box">
                    <input type="text" id="novaTarefaTexto" placeholder="Nova tarefa...">
                    <button onclick="adicionarNova()">+</button>
                </div>
                <div id="listaReminders">
                    {html_tarefas}
                </div>
            </div>

            <div>
                <div class="section-title">Project Deadlines ({mes_atual_str})</div>
                <div class="deadline-card">
                    <div class="deadline-info">
                        <h4>Website Redesign</h4>
                        <p>Thu, Apr 20</p>
                    </div>
                    <div class="dot"></div>
                </div>
            </div>
        </div>

        <!-- MODAL -->
        <div id="modalOverlay">
            <div class="modal">
                <h3>Agendar em <span id="modalDiaTitulo"></span></h3>
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <label>Título do Evento:</label>
                    <input type="text" id="eventoTitulo" placeholder="Ex: Code Review, Sprint...">
                </div>
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <label>Hora:</label>
                    <select id="eventoHora">
                        <option value="8:00">8:00</option><option value="10:00">10:00</option>
                        <option value="12:00">12:00</option><option value="14:00">14:00</option>
                        <option value="16:00">16:00</option><option value="18:00">18:00</option>
                    </select>
                </div>
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <label>Duração:</label>
                    <input type="text" id="eventoDuracao" placeholder="Ex: 8:00 - 9:30">
                </div>
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <label>Cor:</label>
                    <select id="eventoCor">
                        <option value="#8b5cf6">Roxo</option><option value="#06b6d4">Azul</option>
                        <option value="#10b981">Verde</option><option value="#ef4444">Vermelho</option>
                    </select>
                </div>
                <div class="modal-buttons">
                    <button class="btn-cancel" onclick="fecharModal()">Cancelar</button>
                    <button class="btn-save" onclick="salvarNovoEvento()">Guardar</button>
                </div>
            </div>
        </div>

        <script>
            let bridge;
            let diaSelecionado = 'Mon';

            new QWebChannel(qt.webChannelTransport, function(channel) {{
                bridge = channel.objects.bridge;
            }});

            function mudarPagina(pag) {{
                if (bridge) bridge.mudarPagina(pag);
            }}

            function mudarEstado(texto, estado) {{
                if (bridge) bridge.atualizarTarefa(texto, estado);
            }}

            function adicionarNova() {{
                let input = document.getElementById('novaTarefaTexto');
                if (input.value.trim() !== "" && bridge) {{
                    bridge.adicionarTarefa(input.value);
                    input.value = "";
                }}
            }}

            function guardarSnippet(codigo) {{
                if (bridge) bridge.guardarSnippet(codigo);
            }}

            function alternarDia(dia) {{
                if (bridge) bridge.alternarDiaHabito(dia);
            }}

            function atualizarTitulo(titulo) {{
                if (bridge) bridge.atualizarTituloHabito(titulo);
            }}

            function adicionarRecuperacaoPrompt() {{
                let qtd = prompt("Quantos dias em falta/recuperação pretendes adicionar ao calendário?", "2");
                if (qtd !== null && !isNaN(qtd) && parseInt(qtd) > 0 && bridge) {{
                    bridge.adicionarDiasRecuperacao(parseInt(qtd));
                }}
            }}

            function reiniciarCiclo() {{
                let novoNome = document.getElementById('novoNomeRotina').value;
                if (bridge) bridge.reiniciarCicloHabitos(novoNome);
            }}

            function abrirModalAgendar(dia) {{
                diaSelecionado = dia;
                document.getElementById('modalDiaTitulo').innerText = dia;
                document.getElementById('modalOverlay').style.display = 'flex';
            }}

            function fecharModal() {{
                document.getElementById('modalOverlay').style.display = 'none';
            }}

            function salvarNovoEvento() {{
                let titulo = document.getElementById('eventoTitulo').value;
                let hora = document.getElementById('eventoHora').value;
                let duracao = document.getElementById('eventoDuracao').value;
                let cor = document.getElementById('eventoCor').value;

                if (titulo.trim() !== "" && bridge) {{
                    bridge.adicionarEvento(diaSelecionado, hora, titulo, duracao, cor);
                    fecharModal();
                    document.getElementById('eventoTitulo').value = "";
                }}
            }}
        </script>
    </body>
    </html>
    """

class AppTotalmenteFuncional(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DevAgenda Pro - Totalmente Funcional")
        self.resize(1280, 768)

        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        self.channel = QWebChannel()
        self.bridge = Bridge(self)
        self.channel.registerObject("bridge", self.bridge)
        self.browser.page().setWebChannel(self.channel)

        self.recarregar_interface()

    def recarregar_interface(self):
        html = gerar_html()
        self.browser.setHtml(html, QUrl("http://localhost"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = AppTotalmenteFuncional()
    janela.show()
    sys.exit(app.exec())