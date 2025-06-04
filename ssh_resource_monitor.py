import sys
import paramiko
import time
from collections import defaultdict
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel,
    QGridLayout, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg


class SSHMonitorGraph(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sunucu Kaynak İzleyici - Grafik")
        self.resize(1200, 800)
        self.ssh_client = None

        self.prev_net_stats = {}
        self.net_check_time = 0

        layout = QGridLayout()

        layout.addWidget(QLabel("IP:"), 0, 0)
        self.ip_edit = QLineEdit("127.0.0.1")
        layout.addWidget(self.ip_edit, 0, 1)

        layout.addWidget(QLabel("Port:"), 1, 0)
        self.port_edit = QLineEdit("22")
        layout.addWidget(self.port_edit, 1, 1)

        layout.addWidget(QLabel("Kullanıcı:"), 2, 0)
        self.user_edit = QLineEdit("root")
        layout.addWidget(self.user_edit, 2, 1)

        layout.addWidget(QLabel("Şifre:"), 3, 0)
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_edit, 3, 1)

        self.connect_btn = QPushButton("Bağlan")
        layout.addWidget(self.connect_btn, 4, 0, 1, 2)
        self.connect_btn.clicked.connect(self.toggle_connection)

        # Grafik widgetları
        self.cpu_plot = pg.PlotWidget(title="Site Bazında CPU Kullanımı (%)")
        self.cpu_plot.setLabel('left', 'CPU %')
        self.cpu_plot.setLabel('bottom', 'Site/Process')
        self.cpu_plot.showGrid(x=True, y=True)

        self.ram_plot = pg.PlotWidget(title="Site Bazında RAM Kullanımı (%)")
        self.ram_plot.setLabel('left', 'RAM %')
        self.ram_plot.setLabel('bottom', 'Site/Process')
        self.ram_plot.showGrid(x=True, y=True)

        self.net_plot = pg.PlotWidget(title="Toplam Ağ Trafiği (MB/s)")
        self.net_plot.setLabel('left', 'MB/s')
        self.net_plot.setLabel('bottom', 'Zaman (s)')
        self.net_plot.showGrid(x=True, y=True)

        layout.addWidget(self.cpu_plot, 5, 0, 1, 2)
        layout.addWidget(self.ram_plot, 6, 0, 1, 2)
        layout.addWidget(self.net_plot, 7, 0, 1, 2)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)

        # Ağ trafiği için zaman serisi veri
        self.net_recv_history = []
        self.net_trans_history = []
        self.max_history = 30  # son 30 ölçüm
        self.start_time = time.time()

    def toggle_connection(self):
        if self.ssh_client:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        ip = self.ip_edit.text()
        port = int(self.port_edit.text())
        username = self.user_edit.text()
        password = self.pass_edit.text()

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh_client.connect(ip, port=port, username=username, password=password, timeout=10)
            self.connect_btn.setText("Bağlantıyı Kes")
            self.log_message("Sunucuya bağlanıldı.")
            self.timer.start(3000)
            self.prev_net_stats = {}
            self.net_check_time = time.time()
            self.net_recv_history.clear()
            self.net_trans_history.clear()
        except Exception as e:
            self.ssh_client = None
            self.log_message(f"Hata: {e}")
            QMessageBox.critical(self, "Bağlantı Hatası", str(e))

    def disconnect(self):
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
            self.timer.stop()
            self.connect_btn.setText("Bağlan")
            self.log_message("Bağlantı kesildi.")
            self.cpu_plot.clear()
            self.ram_plot.clear()
            self.net_plot.clear()

    def log_message(self, msg):
        print(msg)

    def run_command(self, cmd):
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
        return stdout.read().decode()

    def parse_ps_output(self, output):
        lines = output.strip().split('\n')
        headers = lines[0].split()
        data = []
        for line in lines[1:]:
            parts = line.split(None, len(headers) - 1)
            entry = dict(zip(headers, parts))
            data.append(entry)
        return data

    def update_stats(self):
        if not self.ssh_client:
            return
        try:
            # Process bilgisi
            cpu_cmd = "ps aux"
            ps_output = self.run_command(cpu_cmd)
            processes = self.parse_ps_output(ps_output)

            # Site/process bazında toplam CPU ve RAM hesapla
            cpu_usage = defaultdict(float)
            ram_usage = defaultdict(float)

            for p in processes:
                cmd = p.get("COMMAND", "")
                # Burası site/process adını kısaltmak için örnek, kendi sunucuya göre uyarlayabilirsin
                site = cmd.split()[0] if cmd else "unknown"
                cpu = float(p.get("%CPU", "0"))
                mem = float(p.get("%MEM", "0"))
                cpu_usage[site] += cpu
                ram_usage[site] += mem

            # En çok kullanılan 10 siteyi al
            top_cpu = sorted(cpu_usage.items(), key=lambda x: x[1], reverse=True)[:10]
            top_ram = sorted(ram_usage.items(), key=lambda x: x[1], reverse=True)[:10]

            # Ağ trafiği
            net_output = self.run_command("cat /proc/net/dev")
            lines = net_output.strip().split('\n')[2:]

            now = time.time()
            interval = now - self.net_check_time if self.net_check_time else 1
            self.net_check_time = now

            net_data = {}
            total_recv = 0
            total_trans = 0
            for line in lines:
                if ':' not in line:
                    continue
                iface, data = line.split(':', 1)
                iface = iface.strip()
                fields = data.strip().split()
                recv_bytes = int(fields[0])
                trans_bytes = int(fields[8])
                net_data[iface] = (recv_bytes, trans_bytes)

            speeds = {}
            for iface, (recv, trans) in net_data.items():
                if iface in self.prev_net_stats:
                    prev_recv, prev_trans = self.prev_net_stats[iface]
                    recv_speed = (recv - prev_recv) / interval / 1024 / 1024
                    trans_speed = (trans - prev_trans) / interval / 1024 / 1024
                else:
                    recv_speed = 0
                    trans_speed = 0
                speeds[iface] = (recv_speed, trans_speed)
                total_recv += recv_speed
                total_trans += trans_speed

            self.prev_net_stats = net_data

            # Grafik çizim
            self.plot_bar(self.cpu_plot, top_cpu, "CPU %")
            self.plot_bar(self.ram_plot, top_ram, "RAM %")

            # Ağ trafiği zaman serisi
            if len(self.net_recv_history) >= self.max_history:
                self.net_recv_history.pop(0)
                self.net_trans_history.pop(0)
            self.net_recv_history.append(total_recv)
            self.net_trans_history.append(total_trans)

            x = list(range(len(self.net_recv_history)))
            self.net_plot.clear()
            self.net_plot.addLegend()

            self.net_plot.plot(x, self.net_recv_history, pen='r', name='Alınan')
            self.net_plot.plot(x, self.net_trans_history, pen='b', name='Gönderilen')

        except Exception as e:
            self.log_message(f"Güncelleme hatası: {e}")
            self.disconnect()

    def plot_bar(self, plot_widget, data, y_label):
        plot_widget.clear()
        names = [item[0] for item in data]
        values = [item[1] for item in data]

        bg = pg.BarGraphItem(x=range(len(data)), height=values, width=0.6, brush='orange')
        plot_widget.addItem(bg)

        # X eksenine isimleri yazdır
        axis = plot_widget.getAxis('bottom')
        axis.setTicks([list(zip(range(len(names)), names))])



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SSHMonitorGraph()
    window.show()
    sys.exit(app.exec_())
