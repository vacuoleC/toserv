# 开发说明

> 本文档面向开发者，介绍项目的技术栈、文件结构、每个文件的作用与实现细节，以及各层之间的协作流程。

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **后端框架** | Flask 3.x | Web 框架，处理路由和请求响应 |
| **认证** | Flask-Login | 会话管理、登录状态维护 |
| **表单验证** | Flask-WTF + WTForms | 表单字段定义、防 CSRF 攻击 |
| **ORM** | Flask-SQLAlchemy | 数据库操作，支持 SQLite |
| **前端** | HTML5 + CSS3 + 原生 JS + Jinja2 | 页面渲染、样式和交互 |
| **生产服务器** | Gunicorn | WSGI 服务器，替代 Flask 内置服务器 |

---

## 文件结构

```
week10/
├── app/
│   ├── __init__.py       # Flask 应用工厂，所有扩展初始化
│   ├── models.py         # 数据库模型定义
│   ├── forms.py          # WTF 表单字段定义
│   ├── services.py       # 业务逻辑层（新增）
│   └── routes/
│       ├── auth.py       # 认证路由：登录 / 登出
│       └── main.py       # 业务路由：CRUD + 批量操作
├── templates/            # Jinja2 模板文件
│   ├── base.html         # 基础模板
│   ├── auth/
│   │   └── login.html    # 登录页
│   └── main/
│       ├── index.html    # 主页（列表）
│       ├── form.html     # 新增 / 编辑表单页
│       └── view.html     # 记录详情页
├── static/
│   ├── css/style.css    # 全局样式
│   └── js/main.js       # 前端交互脚本（预留）
├── data/                 # 数据库存储目录
├── config.py             # 应用配置
├── run.py                # 开发服务器启动入口
├── init_db.py            # 数据库初始化脚本
├── requirements.txt      # Python 依赖清单
└── README.md             # 使用说明
```

---

## 文件详解

### app/__init__.py

**作用**：Flask 应用工厂，集中初始化所有扩展、注册蓝图、配置路径。

**关键内容**：

- 创建 Flask 实例时，通过 `template_folder` 和 `static_folder` 指向项目根目录的 `templates/` 和 `static/`
- 初始化 `db`（SQLAlchemy）、`login_manager`、`csrf` 三个扩展
- 注册 `user_loader` 回调函数，供 Flask-Login 从 session 中恢复用户对象
- 注册 `auth_bp`（前缀 `/auth`）和 `main_bp`（前缀 `/`）两个蓝图

**流程解读**：应用启动 → `create_app()` 被调用 → 初始化扩展 → 注册蓝图 → 创建数据库表（`db.create_all()`）

**调用方式**：

```python
from app import create_app
app = create_app()          # 参数可选，默认读取 config.Config
```

---

### config.py

**作用**：集中管理应用配置，包括密钥、数据库路径、会话设置、文件上传限制。

**关键内容**：

```python
SECRET_KEY          # CSRF 和 session 签名密钥（生产环境需替换）
SQLALCHEMY_DATABASE_URI  # SQLite 数据库路径（相对于项目根目录的 data/app.db）
PERMANENT_SESSION_LIFETIME  # 会话有效期 7 天
UPLOAD_FOLDER       # 文件上传目录（data/uploads）
MAX_CONTENT_LENGTH  # 最大上传大小 16MB
```

**调用方式**：无需直接调用，`create_app()` 中通过 `app.config.from_object("config.Config")` 加载。

---

### app/models.py

**作用**：定义数据库表结构，对应 `User`、`Record`、`OperationLog` 三张表。

**模型说明**：

| 类名 | 表名 | 字段 | 说明 |
|------|------|------|------|
| `User` | `users` | id, username, password_hash, created_at | 用户表，继承 `UserMixin` 以支持 Flask-Login |
| `Record` | `records` | id, title, content, user_id, created_at, updated_at | 业务记录表 |
| `OperationLog` | `operation_logs` | id, user_id, action, target_type, target_id, description, created_at | 操作日志表 |

**User 模型方法**：

```python
user.set_password(password)    # 输入：明文密码，输出：设置 password_hash
user.check_password(password)  # 输入：明文密码，输出：bool，是否匹配
```

**调用方式**：

```python
from app.models import User, Record, OperationLog
user = User.query.get(user_id)           # 根据 ID 查询用户
Record.query.filter_by(user_id=uid)     # 查询某用户的所有记录
```

---

### app/forms.py

**作用**：使用 WTForms 定义表单字段和校验规则，Flask-WTF 自动处理 CSRF token。

**表单说明**：

| 表单类 | 字段 | 校验规则 |
|--------|------|----------|
| `LoginForm` | username, password | 非空、长度 3-20 |
| `RecordForm` | title, content | 非空、标题最长 200、content 最长 5000 |
| `RegisterForm` | username, password, password_confirm | 密码确认一致性、用户名唯一性 |

**调用方式**：

```python
from app.forms import LoginForm, RecordForm
form = LoginForm()                    # 实例化
form.validate_on_submit()             # 验证提交数据，返回 bool
form.username.data                    # 获取字段值
```

---

### app/services.py

**作用**：业务逻辑层，所有数据库读写操作集中在此，routes 层只负责调用。

**服务类说明**：

#### `UserService`

```python
UserService.authenticate(username, password)
    # 输入: str, str → 输出: User | None
    # 说明: 验证用户名密码，返回用户对象或 None

UserService.get_by_id(user_id)
    # 输入: int → 输出: User | None

UserService.create_user(username, password)
    # 输入: str, str → 输出: User
    # 说明: 创建新用户，已存在则抛出 ValueError
```

#### `RecordService`

```python
RecordService.create(title, content, user_id)
    # 输入: str, str, int → 输出: Record
    # 说明: 新建记录并写入操作日志

RecordService.get_by_id(record_id, user_id)
    # 输入: int, int → 输出: Record
    # 说明: 带权限校验获取记录，未找到则 404

RecordService.list_by_user(user_id, page=1, per_page=10)
    # 输入: int, int, int → 输出: Pagination 对象
    # 说明: 分页查询用户记录

RecordService.update(record, title, content)
    # 输入: Record, str, str → 输出: Record
    # 说明: 更新记录并写入操作日志

RecordService.delete(record)
    # 输入: Record → 输出: None
    # 说明: 删除记录并写入操作日志

RecordService.batch_delete(record_ids, user_id)
    # 输入: list[int], int → 输出: int（删除数量）
    # 说明: 批量删除，带权限校验
```

#### `OperationLogService`

```python
OperationLogService.log(user_id, action, target_type, description, target_id=None)
    # 输入: int, str, str, str, int|None → 输出: None
    # 说明: 写入一条操作日志（不 commit，需外层统一 commit）
```

**调用方式**：

```python
from app.services import RecordService, UserService
record = RecordService.get_by_id(record_id, current_user.id)
RecordService.create(title="新标题", content="内容", user_id=current_user.id)
```

---

### app/routes/auth.py

**作用**：处理登录和登出请求，调用服务层后返回响应。

**路由说明**：

| 路由 | 方法 | 页面 | 说明 |
|------|------|------|------|
| `/auth/login` | GET, POST | 登录页 | 验证用户名密码，成功跳转主页 |
| `/auth/logout` | GET | - | 退出登录，清除会话 |

**流程解读**：

```
用户提交登录 → 表单验证 → UserService.authenticate() → 成功则 login_user()
→ 记录日志 → db.session.commit() → 跳转主页
失败 → flash 错误消息 → 重新渲染登录页
```

**调用方式**：无需直接调用，Flask 自动根据 URL 分发。

---

### app/routes/main.py

**作用**：处理所有业务页面的请求，调用 `RecordService` 完成 CRUD 操作。

**路由说明**：

| 路由 | 方法 | 页面 | 说明 |
|------|------|------|------|
| `/` | GET | 主页（列表） | 显示当前用户记录，支持分页 |
| `/record/new` | GET, POST | 新增表单页 | 新建记录 |
| `/record/<id>` | GET | 详情页 | 查看单条记录 |
| `/record/<id>/edit` | GET, POST | 编辑表单页 | 编辑记录 |
| `/record/<id>/delete` | POST | - | 删除单条记录 |
| `/record/batch-delete` | POST | - | 批量删除记录 |

**流程解读**（以新增记录为例）：

```
GET /record/new → 渲染空白表单
POST /record/new → 表单验证 → RecordService.create() → flash 成功消息
→ 跳转主页
```

**调用方式**：无需直接调用，Flask 自动根据 URL 分发。

---

### run.py

**作用**：开发环境启动入口，使用 Flask 内置开发服务器。

**调用方式**：

```bash
python run.py        # 启动后访问 http://127.0.0.1:5000
```

**生产部署时请替换为 Gunicorn**：

```bash
gunicorn -w 2 -b 0.0.0.0:5000 "app:create_app()"
```

---

### init_db.py

**作用**：初始化数据库表，并创建默认管理员账户。

**调用方式**：

```bash
python init_db.py    # 首次运行，执行后输出"默认管理员已创建"
```

**输出**：默认管理员 `admin` / `admin123`。

---

### templates/base.html

**作用**：基础模板，定义全局 HTML 结构、样式引用、导航栏和消息提示。

**核心 block**：

| block 名称 | 用途 |
|------------|------|
| `title` | 页面标题 |
| `header` | 顶部导航栏 |
| `content` | 页面主体内容 |
| `scripts` | JavaScript 脚本 |
| `footer` | 底部版权信息 |

---

### templates/auth/login.html

**作用**：登录页面表单，继承 `base.html`，包含用户名和密码输入框。

---

### templates/main/index.html

**作用**：主页，显示记录列表、分页控件、批量删除按钮。

**前端逻辑**（内嵌 JS）：

- 监听复选框变化，勾选后显示"批量删除"按钮
- 全选功能：点击表头复选框选中所有记录
- 点击批量删除按钮：将选中的 record_ids 添加到表单并提交

---

### templates/main/form.html

**作用**：新增 / 编辑记录表单页，通过 `action` 参数区分标题（"新增"或"编辑"）。

---

### templates/main/view.html

**作用**：记录详情页，显示标题、创建时间、更新时间、内容和操作按钮。

---

## 层间协作流程

```
用户请求
   ↓
routes 层（auth.py / main.py）
   ↓ 调用
services 层（UserService / RecordService / OperationLogService）
   ↓ 调用
models 层（User / Record / OperationLog）
   ↓ 操作
SQLite 数据库（data/app.db）
```

**请求 → 响应典型流程**（以查看记录为例）：

1. 用户访问 `/record/1`
2. Flask 分发到 `main.view_record(1)`
3. 调用 `RecordService.get_by_id(1, current_user.id)` 做权限校验
4. 通过 `Record.query.filter_by()` 查到 Record 对象
5. 写入操作日志 `OperationLogService.log()`
6. 渲染 `templates/main/view.html`，返回给用户

**分层原则**：

- **routes**：只处理请求/响应，不直接操作数据库
- **services**：处理所有业务规则（权限校验、参数校验、日志记录），操作数据库
- **models**：只描述数据结构，不包含业务逻辑