#!/bin/bash

set -e

APP_DIR="/opt/wx_api"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="wx_api"

function install_service() {
    if systemctl list-units --full -all | grep -q "$SERVICE_NAME.service"; then
        echo "服务已存在，状态如下："
        systemctl status $SERVICE_NAME
        return
    fi

    echo "创建应用目录..."
    mkdir -p $APP_DIR

    echo "创建 Python 虚拟环境..."
    python3 -m venv $VENV_DIR

    echo "激活虚拟环境并升级 pip、安装依赖..."
    source $VENV_DIR/bin/activate
    pip install --upgrade pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple
    if [ -f "$APP_DIR/requirements.txt" ]; then
        pip install -r $APP_DIR/requirements.txt -i https://mirrors.aliyun.com/pypi/simple
    fi
    deactivate

    echo "创建 systemd 服务..."
    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=wx_api Service
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/python $APP_DIR/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    echo "重新加载 systemd..."
    sudo systemctl daemon-reload

    echo "启用并启动服务..."
    sudo systemctl enable $SERVICE_NAME
    sudo systemctl start $SERVICE_NAME

    echo "安装完成！可以使用：systemctl status $SERVICE_NAME 查看状态"
}

function uninstall_service() {
    echo "停止服务..."
    sudo systemctl stop $SERVICE_NAME || true
    sudo systemctl disable $SERVICE_NAME || true

    echo "删除 systemd 服务文件..."
    sudo rm -f /etc/systemd/system/$SERVICE_NAME.service

    echo "重新加载 systemd..."
    sudo systemctl daemon-reload

    echo "卸载完成！（未删除目录与文件）"
}

function restart_service() {
    echo "重启服务..."
    sudo systemctl restart $SERVICE_NAME
    echo "服务已重启。"
}

function view_log() {
    echo "查看日志：按 Ctrl+C 退出"
    sudo journalctl -u $SERVICE_NAME -f
}

function menu() {
    echo "请选择操作："
    echo "1) 安装并启动服务"
    echo "2) 卸载服务"
    echo "3) 查看日志"
    echo "4) 重启服务"
    echo "q) 退出"
    read -p "输入选项: " choice
    case $choice in
        1) install_service ;;
        2) uninstall_service ;;
        3) view_log ;;
        4) restart_service ;;
        q|Q) exit 0 ;;
        *) echo "无效选项" ;;
    esac
}

# 循环菜单
while true; do
    menu
done
```