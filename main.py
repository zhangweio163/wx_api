from base.app import app
from controller.app_controller import app_bp
from controller.login_controller import login_bp
from controller.org_controller import org_bp
import conf.setting as setting
# ===== 显式导入 controller 中的所有模块，触发路由注册 =====
app.register_blueprint(app_bp)
app.register_blueprint(login_bp)
app.register_blueprint(org_bp)


# ===== 打印所有路由 =====
def print_routes():
    print("\nRegistered Routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        print(f"{rule.endpoint:30s} {methods:20s} {str(rule)}")

print_routes()

# ===== 启动应用 =====
if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=setting.debug, port=8000)