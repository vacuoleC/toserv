# 信息管理系统

> 基于 Flask 的轻量级信息管理 Web 应用，支持用户认证、数据增删改查和操作日志记录。

## 功能概览

### 用户认证

| 功能 | 说明 |
|------|------|
| 用户登录 | 输入用户名和密码，系统验证后登录 |
| 会话保持 | 登录后 7 天内无需重新登录 |
| 权限控制 | 未登录用户无法访问主页，自动重定向到登录页 |
| 安全退出 | 一键退出，清除会话 |

### 数据管理

| 功能 | 说明 |
|------|------|
| 新增记录 | 填写标题和内容，保存后自动入库 |
| 查看详情 | 点击标题查看记录完整内容 |
| 编辑记录 | 修改已有记录的内容 |
| 单个删除 | 逐条删除，确认后生效 |
| 批量删除 | 勾选多条记录，一键批量删除 |
| 分页展示 | 每页 10 条记录，支持翻页 |

### 操作日志

所有关键操作（登录、登出、新增、编辑、删除、查看）均自动记录到数据库，包含操作人、操作时间和操作描述。

## 快速开始

### 环境要求

- Python 3.9+
- pip

### 安装依赖

```bash
# 克隆项目后
pip install -r requirements.txt
```

### 初始化数据库

```bash
python init_db.py
```

初始化后会创建默认管理员账户：

- **用户名**：`admin`
- **密码**：`admin123`

### 启动应用

```bash
python run.py
```

然后访问 **http://127.0.0.1:5000**

## 页面说明

### 登录页

输入管理员账号密码登录。登录成功后自动跳转到主页。

### 主页

显示当前用户的所有记录列表，包含以下操作：

- **新增记录**：创建新的业务记录
- **编辑**：修改已有记录
- **删除**：删除单条记录
- **批量删除**：勾选多条记录后点击按钮批量删除
- **退出登录**：安全退出当前账户

## 部署到服务器

### 方式一：Gunicorn（推荐生产环境）

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 "app:create_app()"
```

### 方式二：Nginx + Gunicorn

```bash
# 1. 安装 Nginx
sudo apt install nginx

# 2. 配置反向代理（/etc/nginx/sites-available/flask-app）
# 3. 启用站点
sudo ln -s /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/

# 4. 重载 Nginx
sudo systemctl reload nginx

# 5. 用 systemd 管理 Gunicorn
```

## 项目结构

```
week10/
├── app/
│   ├── __init__.py      # Flask 应用工厂
│   ├── models.py        # 数据模型
│   ├── forms.py         # 表单定义
│   ├── services.py      # 业务逻辑层
│   └── routes/
│       ├── auth.py      # 认证路由
│       └── main.py      # 业务路由
├── templates/           # Jinja2 模板
├── static/               # 静态资源
├── data/                 # 数据库存储目录
├── config.py             # 配置
├── run.py                # 启动入口
├── init_db.py           # 数据库初始化
└── requirements.txt     # 依赖清单
```

## 技术栈

- **后端**：Flask + Flask-Login + Flask-WTF + Flask-SQLAlchemy
- **前端**：HTML5 + CSS3 + 原生 JavaScript + Jinja2
- **数据库**：SQLite
- **生产服务器**：Gunicorn + Nginx