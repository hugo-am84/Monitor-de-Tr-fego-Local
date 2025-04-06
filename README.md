# Monitor de Rede por Processo (GUI)

Uma ferramenta gráfica simples, leve e funcional feita em Python com Tkinter para monitorar o tráfego de rede por processo no Linux.

Este monitor exibe:
- Upload e download em tempo real (em Mbps)
- Pacotes enviados e recebidos
- Processos fixos como `firefox`, `spotify`, `systemd` e `NetworkManager`, mesmo quando sem atividade
- Outros processos que estejam ativamente usando a rede

---

## 📸 Interface

![Monitor de Rede por Processo](screenshot.png) <!-- Adicione um screenshot se quiser -->

---

## 🚀 Como usar

### 1. Instale os requisitos:

```bash
sudo apt install python3 python3-tk
pip install psutil
