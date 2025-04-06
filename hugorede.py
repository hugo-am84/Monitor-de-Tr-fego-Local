import psutil
import time
import os
from collections import defaultdict
import tkinter as tk
from tkinter import messagebox
import threading

def bytes_para_mbps(bytes):
    return round((bytes * 8) / (1024 ** 2), 2)

def obter_bytes_por_pid():
    conexoes = psutil.net_connections(kind='inet')
    dados_por_pid = defaultdict(lambda: {'bytes_sent': 0, 'bytes_recv': 0})
    for conn in conexoes:
        if conn.pid:
            try:
                proc = psutil.Process(conn.pid)
                io = proc.io_counters()
                dados_por_pid[conn.pid]['nome'] = proc.name()
                dados_por_pid[conn.pid]['bytes_sent'] += io.write_bytes
                dados_por_pid[conn.pid]['bytes_recv'] += io.read_bytes
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    return dados_por_pid

def iniciar_monitoramento():
    global monitorando, old_stats, old_dados_por_pid
    monitorando = True
    while monitorando:
        time.sleep(1)

        new_stats = psutil.net_io_counters()
        new_dados_por_pid = obter_bytes_por_pid()

        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, "Uso de Rede por Processo:\n\n")

        # Mostrar processos fixos com subprocessos
        for nome_fixo in processos_fixos:
            encontrado = False
            for pid, dados in new_dados_por_pid.items():
                nome = dados.get('nome', '')
                if nome_fixo.lower() in nome.lower() and pid in old_dados_por_pid:
                    encontrado = True
                    sent_diff = dados['bytes_sent'] - old_dados_por_pid[pid]['bytes_sent']
                    recv_diff = dados['bytes_recv'] - old_dados_por_pid[pid]['bytes_recv']
                    text_output.insert(tk.END, f"{nome} (PID {pid})\n")
                    text_output.insert(tk.END, f"  Download: {bytes_para_mbps(recv_diff)} Mbps\n")
                    text_output.insert(tk.END, f"  Upload  : {bytes_para_mbps(sent_diff)} Mbps\n\n")
            if not encontrado:
                text_output.insert(tk.END, f"{nome_fixo} (sem atividade)\n")
                text_output.insert(tk.END, f"  Download: 0.0 Mbps\n")
                text_output.insert(tk.END, f"  Upload  : 0.0 Mbps\n\n")

        # Mostrar demais processos com tráfego
        for pid, dados in new_dados_por_pid.items():
            nome = dados.get('nome', f"PID {pid}")
            if not any(p.lower() in nome.lower() for p in processos_fixos) and pid in old_dados_por_pid:
                sent_diff = dados['bytes_sent'] - old_dados_por_pid[pid]['bytes_sent']
                recv_diff = dados['bytes_recv'] - old_dados_por_pid[pid]['bytes_recv']
                if sent_diff > 0 or recv_diff > 0:
                    text_output.insert(tk.END, f"{nome} (PID {pid})\n")
                    text_output.insert(tk.END, f"  Download: {bytes_para_mbps(recv_diff)} Mbps\n")
                    text_output.insert(tk.END, f"  Upload  : {bytes_para_mbps(sent_diff)} Mbps\n\n")

        # Atualizar total da rede
        sent_total = new_stats.bytes_sent - old_stats.bytes_sent
        recv_total = new_stats.bytes_recv - old_stats.bytes_recv

        total_output.config(state='normal')
        total_output.delete(1.0, tk.END)
        total_output.insert(tk.END, f"TOTAL GERAL DA REDE:\n")
        total_output.insert(tk.END, f"  Download: {bytes_para_mbps(recv_total)} Mbps\n")
        total_output.insert(tk.END, f"  Upload  : {bytes_para_mbps(sent_total)} Mbps\n")
        total_output.insert(tk.END, f"  Pacotes Enviados  : {new_stats.packets_sent}\n")
        total_output.insert(tk.END, f"  Pacotes Recebidos : {new_stats.packets_recv}\n")
        total_output.config(state='disabled')

        # Atualizar dados antigos
        old_stats = new_stats
        old_dados_por_pid = new_dados_por_pid

def parar_monitoramento():
    global monitorando
    monitorando = False
    messagebox.showinfo("Monitoramento", "Monitoramento parado.")

def fechar():
    global monitorando
    monitorando = False
    root.quit()

# Interface gráfica
root = tk.Tk()
root.title("Monitor de Rede por Processo")

# Processos fixos que devem aparecer sempre (subprocessos incluídos)
processos_fixos = ['firefox', 'spotify', 'systemd', 'NetworkManager']

# Estado inicial
old_stats = psutil.net_io_counters()
old_dados_por_pid = obter_bytes_por_pid()
monitorando = False

# Text area: lista por processo
text_output = tk.Text(root, width=70, height=20, wrap='word')
text_output.pack(padx=10, pady=5)

# Text area: total geral fixo
total_output = tk.Text(root, width=70, height=5, bg="#f0f0f0", fg="black", font=("Courier", 10))
total_output.pack(padx=10, pady=(0, 10))
total_output.config(state='disabled')

# Botões em linha
frame_botoes = tk.Frame(root)
frame_botoes.pack(pady=10)

btn_iniciar = tk.Button(frame_botoes, text="Iniciar Monitoramento", width=20, command=lambda: threading.Thread(target=iniciar_monitoramento, daemon=True).start())
btn_iniciar.grid(row=0, column=0, padx=5)

btn_parar = tk.Button(frame_botoes, text="Parar Monitoramento", width=20, command=parar_monitoramento)
btn_parar.grid(row=0, column=1, padx=5)

btn_fechar = tk.Button(frame_botoes, text="Fechar", width=20, command=fechar)
btn_fechar.grid(row=0, column=2, padx=5)

root.mainloop()
