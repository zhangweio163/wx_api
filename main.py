import os

import conf.setting as setting


def create_app():
    from base.app import app
    from controller.app_controller import app_bp
    from controller.login_controller import login_bp
    from controller.org_controller import org_bp
    from controller.audit_controller import app_bp as audit_bp

    # 注册蓝图
    app.register_blueprint(app_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(audit_bp)

    return app

def print_routes(app):
    print("\nRegistered Routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        print(f"{rule.endpoint:30s} {methods:20s} {str(rule)}")

if __name__ == "__main__":
    app = create_app()

    # 只在子进程打印一次
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        print_routes(app)

    app.run(host="0.0.0.0", debug=setting.debug, port=8000)