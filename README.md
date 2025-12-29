# 在线课程学习平台

数据库课程设计项目 - Web应用开发

## 项目概述

一个基于Flask的在线课程学习平台，实现了完整的用户管理、课程管理、订单管理和学习进度跟踪功能。

## 技术栈

- **后端**: Python Flask
- **前端**: HTML5 + CSS3 + Bootstrap 5 + JavaScript
- **数据库**: SQLite (开发) / MySQL (生产)

## 快速开始

```bash
# 进入项目目录
cd online_learning_platform

# 运行应用
python app.py

# 访问 http://localhost:5000
```

## 测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 学员 | zhangsan@example.com | password123 |
| 讲师 | wanglaoshi@example.com | password123 |
| 管理员 | admin@example.com | password123 |

## 功能特性

### 用户管理
- 注册、登录、登出
- 个人资料编辑
- 角色权限控制

### 课程管理 (CRUD)
- 创建课程
- 编辑课程
- 删除课程
- 课程列表展示

### 学习功能
- 课程购买
- 学习进度跟踪
- 课程收藏

### SQL查询演示
访问 `/demo/queries` 查看11种SQL查询类型的演示

## 数据库设计

### 实体列表 (15个)
1. user - 用户表
2. user_profile - 用户详情表 (1:1)
3. role - 角色表
4. user_role - 用户角色关联表 (M:N)
5. category - 分类表 (自关联)
6. course - 课程表
7. chapter - 章节表
8. lesson - 课时表
9. order - 订单表
10. order_item - 订单明细表
11. enrollment - 选课记录表
12. learning_progress - 学习进度表
13. review - 评价表
14. favorite - 收藏表
15. cart - 购物车表

### 关系类型
- **一对一**: user ↔ user_profile
- **一对多**: course → chapter → lesson
- **多对多**: user ↔ course (通过enrollment)
- **自关联**: category.parent_id → category.category_id

## 项目结构

```
online_learning_platform/
├── app.py                 # Flask主应用
├── learning_platform.db   # SQLite数据库
├── static/
│   ├── css/style.css     # 自定义样式
│   └── js/main.js        # JavaScript
├── templates/
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页
│   ├── login.html        # 登录
│   ├── register.html     # 注册
│   ├── courses.html      # 课程列表
│   ├── course_detail.html# 课程详情
│   ├── profile.html      # 个人中心
│   ├── learn.html        # 学习页面
│   ├── demo_queries.html # SQL演示
│   └── admin/
│       ├── courses.html  # 课程管理
│       └── course_form.html # 课程表单
├── sql/
│   ├── database_schema.sql  # MySQL建表脚本
│   └── complex_queries.sql  # 复杂查询示例
└── docs/
    └── project_report.docx  # 项目报告
```

## SQL查询类型

1. 单表查询
2. 内连接 (INNER JOIN)
3. 左外连接 (LEFT JOIN)
4. 自连接 (Self Join)
5. 聚合函数 + GROUP BY + ORDER BY
6. 日期函数
7. 子查询
8. 相关子查询
9. UNION集合操作
10. 多表连接查询
11. 除法查询
