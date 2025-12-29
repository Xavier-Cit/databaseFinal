-- ============================================================
-- 在线课程学习平台 - 数据库设计脚本
-- Online Learning Platform Database Schema
-- ============================================================
-- 作者: Claude AI Assistant
-- 创建日期: 2025年
-- 数据库: MySQL 8.0+
-- ============================================================

-- 创建数据库
DROP DATABASE IF EXISTS online_learning_platform;
CREATE DATABASE online_learning_platform 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE online_learning_platform;

-- ============================================================
-- 1. 用户角色表 (Role)
-- ============================================================
CREATE TABLE role (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='用户角色表';

-- ============================================================
-- 2. 用户表 (User)
-- ============================================================
CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    status ENUM('active', 'inactive', 'banned') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login DATETIME,
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='用户基本信息表';

-- ============================================================
-- 3. 用户详情表 (UserProfile) - 与User一对一关系
-- ============================================================
CREATE TABLE user_profile (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    avatar_url VARCHAR(500),
    bio TEXT,
    gender ENUM('male', 'female', 'other'),
    birth_date DATE,
    location VARCHAR(100),
    occupation VARCHAR(100),
    website VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='用户详细信息表 - 与用户表一对一';

-- ============================================================
-- 4. 用户角色关联表 (UserRole) - 多对多关系
-- ============================================================
CREATE TABLE user_role (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES role(role_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='用户角色关联表 - 多对多关系';

-- ============================================================
-- 5. 课程分类表 (Category) - 自关联，支持层级分类
-- ============================================================
CREATE TABLE category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_id INT DEFAULT NULL,
    description TEXT,
    icon VARCHAR(100),
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES category(category_id) ON DELETE SET NULL,
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB COMMENT='课程分类表 - 支持自关联层级结构';

-- ============================================================
-- 6. 课程表 (Course)
-- ============================================================
CREATE TABLE course (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    subtitle VARCHAR(300),
    description TEXT,
    instructor_id INT NOT NULL,
    category_id INT,
    cover_image VARCHAR(500),
    price DECIMAL(10, 2) DEFAULT 0.00,
    original_price DECIMAL(10, 2),
    level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    language VARCHAR(50) DEFAULT '中文',
    duration_hours DECIMAL(5, 2) DEFAULT 0,
    status ENUM('draft', 'pending', 'published', 'archived') DEFAULT 'draft',
    is_featured BOOLEAN DEFAULT FALSE,
    enrollment_count INT DEFAULT 0,
    rating_avg DECIMAL(3, 2) DEFAULT 0.00,
    rating_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    published_at DATETIME,
    FOREIGN KEY (instructor_id) REFERENCES user(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE SET NULL,
    INDEX idx_instructor (instructor_id),
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    INDEX idx_price (price),
    INDEX idx_rating (rating_avg),
    FULLTEXT INDEX idx_title_desc (title, description)
) ENGINE=InnoDB COMMENT='课程主表';

-- ============================================================
-- 7. 章节表 (Chapter)
-- ============================================================
CREATE TABLE chapter (
    chapter_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    sort_order INT DEFAULT 0,
    is_free BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE,
    INDEX idx_course (course_id),
    INDEX idx_sort (sort_order)
) ENGINE=InnoDB COMMENT='课程章节表';

-- ============================================================
-- 8. 课时表 (Lesson)
-- ============================================================
CREATE TABLE lesson (
    lesson_id INT AUTO_INCREMENT PRIMARY KEY,
    chapter_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content_type ENUM('video', 'article', 'quiz', 'assignment') DEFAULT 'video',
    video_url VARCHAR(500),
    video_duration INT DEFAULT 0 COMMENT '视频时长（秒）',
    article_content TEXT,
    sort_order INT DEFAULT 0,
    is_free BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapter(chapter_id) ON DELETE CASCADE,
    INDEX idx_chapter (chapter_id),
    INDEX idx_sort (sort_order)
) ENGINE=InnoDB COMMENT='课时/视频表';

-- ============================================================
-- 9. 订单表 (Order)
-- ============================================================
CREATE TABLE `order` (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(50) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    final_amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('alipay', 'wechat', 'credit_card', 'free') DEFAULT 'alipay',
    payment_status ENUM('pending', 'paid', 'refunded', 'cancelled') DEFAULT 'pending',
    paid_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE RESTRICT,
    INDEX idx_user (user_id),
    INDEX idx_order_no (order_no),
    INDEX idx_status (payment_status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB COMMENT='订单表';

-- ============================================================
-- 10. 订单明细表 (OrderItem)
-- ============================================================
CREATE TABLE order_item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    course_id INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES `order`(order_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE RESTRICT,
    INDEX idx_order (order_id),
    INDEX idx_course (course_id)
) ENGINE=InnoDB COMMENT='订单明细表';

-- ============================================================
-- 11. 选课记录表 (Enrollment) - User与Course多对多关系
-- ============================================================
CREATE TABLE enrollment (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    order_id INT,
    progress_percent DECIMAL(5, 2) DEFAULT 0.00,
    completed_lessons INT DEFAULT 0,
    total_lessons INT DEFAULT 0,
    status ENUM('active', 'completed', 'expired') DEFAULT 'active',
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    last_accessed_at DATETIME,
    UNIQUE KEY uk_user_course (user_id, course_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES `order`(order_id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_course (course_id),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='选课记录表 - 用户与课程多对多关系';

-- ============================================================
-- 12. 学习进度表 (LearningProgress)
-- ============================================================
CREATE TABLE learning_progress (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    lesson_id INT NOT NULL,
    watched_duration INT DEFAULT 0 COMMENT '已观看时长（秒）',
    progress_percent DECIMAL(5, 2) DEFAULT 0.00,
    is_completed BOOLEAN DEFAULT FALSE,
    last_position INT DEFAULT 0 COMMENT '上次播放位置（秒）',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_lesson (user_id, lesson_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(lesson_id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_lesson (lesson_id)
) ENGINE=InnoDB COMMENT='学习进度表';

-- ============================================================
-- 13. 课程评价表 (Review)
-- ============================================================
CREATE TABLE review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    content TEXT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    helpful_count INT DEFAULT 0,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'approved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_course (user_id, course_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE,
    INDEX idx_course (course_id),
    INDEX idx_rating (rating),
    INDEX idx_created (created_at)
) ENGINE=InnoDB COMMENT='课程评价表';

-- ============================================================
-- 14. 收藏表 (Favorite)
-- ============================================================
CREATE TABLE favorite (
    favorite_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_course (user_id, course_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_course (course_id)
) ENGINE=InnoDB COMMENT='课程收藏表';

-- ============================================================
-- 15. 购物车表 (Cart)
-- ============================================================
CREATE TABLE cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_course (user_id, course_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
) ENGINE=InnoDB COMMENT='购物车表';

-- ============================================================
-- 插入示例数据
-- ============================================================

-- 插入角色
INSERT INTO role (role_name, description) VALUES
('student', '学员 - 可以浏览和购买课程'),
('instructor', '讲师 - 可以创建和管理课程'),
('admin', '管理员 - 拥有所有权限');

-- 插入用户 (密码均为 password123 的bcrypt哈希)
INSERT INTO user (username, email, password_hash, phone, status) VALUES
('张三', 'zhangsan@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4p.K5q3Q5d7KzKmS', '13800138001', 'active'),
('李四', 'lisi@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4p.K5q3Q5d7KzKmS', '13800138002', 'active'),
('王老师', 'wanglaoshi@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4p.K5q3Q5d7KzKmS', '13800138003', 'active'),
('刘老师', 'liulaoshi@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4p.K5q3Q5d7KzKmS', '13800138004', 'active'),
('陈老师', 'chenlaoshi@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4p.K5q3Q5d7KzKmS', '13800138005', 'active'),
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4p.K5q3Q5d7KzKmS', '13800138000', 'active'),
('赵六', 'zhaoliu@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4p.K5q3Q5d7KzKmS', '13800138006', 'active'),
('孙七', 'sunqi@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4p.K5q3Q5d7KzKmS', '13800138007', 'active'),
('周八', 'zhouba@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4p.K5q3Q5d7KzKmS', '13800138008', 'active'),
('吴九', 'wujiu@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4p.K5q3Q5d7KzKmS', '13800138009', 'active');

-- 插入用户详情
INSERT INTO user_profile (user_id, avatar_url, bio, gender, location, occupation) VALUES
(1, '/static/images/avatar1.png', '热爱学习的程序员', 'male', '北京', '软件工程师'),
(2, '/static/images/avatar2.png', '前端开发爱好者', 'female', '上海', '前端工程师'),
(3, '/static/images/avatar3.png', '10年Python开发经验，专注AI教育', 'male', '深圳', '高级工程师'),
(4, '/static/images/avatar4.png', '全栈开发专家，擅长Web开发', 'male', '杭州', '技术总监'),
(5, '/static/images/avatar5.png', '数据科学家，机器学习专家', 'female', '广州', '数据科学家'),
(6, '/static/images/avatar6.png', '平台管理员', 'male', '北京', '运营经理');

-- 分配用户角色
INSERT INTO user_role (user_id, role_id) VALUES
(1, 1), (2, 1), (3, 2), (3, 1), (4, 2), (5, 2), (6, 3), (7, 1), (8, 1), (9, 1), (10, 1);

-- 插入课程分类（包含自关联的层级结构）
INSERT INTO category (category_id, category_name, parent_id, description, sort_order) VALUES
(1, '编程开发', NULL, '各类编程语言和开发技术', 1),
(2, '前端开发', 1, 'HTML/CSS/JavaScript等前端技术', 1),
(3, '后端开发', 1, 'Python/Java/Node.js等后端技术', 2),
(4, '移动开发', 1, 'iOS/Android/Flutter移动应用开发', 3),
(5, '数据科学', NULL, '数据分析、机器学习、人工智能', 2),
(6, '机器学习', 5, '传统机器学习算法与应用', 1),
(7, '深度学习', 5, '神经网络与深度学习', 2),
(8, '数据分析', 5, '数据处理与可视化', 3),
(9, '设计创意', NULL, 'UI/UX设计、平面设计', 3),
(10, '职业技能', NULL, '办公软件、项目管理等', 4);

-- 插入课程
INSERT INTO course (course_id, title, subtitle, description, instructor_id, category_id, price, original_price, level, duration_hours, status, is_featured, enrollment_count, rating_avg, rating_count, published_at) VALUES
(1, 'Python入门到精通', '零基础学Python，21天掌握编程', 'Python是目前最流行的编程语言之一，本课程从零开始，带你系统学习Python编程。', 3, 3, 199.00, 399.00, 'beginner', 42.5, 'published', TRUE, 1580, 4.85, 328, '2024-01-15 10:00:00'),
(2, 'Web前端开发实战', 'HTML+CSS+JavaScript全栈前端', '从HTML基础到React框架，完整的前端学习路径。', 4, 2, 299.00, 599.00, 'intermediate', 68.0, 'published', TRUE, 1230, 4.72, 256, '2024-02-20 10:00:00'),
(3, '机器学习入门', '用Python实现机器学习算法', '系统学习机器学习算法，包括回归、分类、聚类等。', 5, 6, 399.00, 799.00, 'intermediate', 55.5, 'published', TRUE, 890, 4.90, 178, '2024-03-10 10:00:00'),
(4, 'MySQL数据库精讲', '从入门到高级优化', '深入学习MySQL数据库，包括SQL语法、索引优化、事务处理等。', 3, 3, 149.00, 299.00, 'beginner', 35.0, 'published', FALSE, 760, 4.65, 152, '2024-04-05 10:00:00'),
(5, 'Vue.js 3.0实战', '最新Vue3组合式API开发', '学习Vue3最新特性，构建现代化Web应用。', 4, 2, 259.00, 499.00, 'intermediate', 48.0, 'published', TRUE, 650, 4.78, 130, '2024-05-12 10:00:00'),
(6, '深度学习与神经网络', 'TensorFlow与PyTorch双框架', '从理论到实践，掌握深度学习核心技术。', 5, 7, 499.00, 999.00, 'advanced', 72.0, 'published', TRUE, 420, 4.92, 84, '2024-06-20 10:00:00'),
(7, 'Flask Web开发', 'Python Web框架实战', '使用Flask构建完整的Web应用程序。', 3, 3, 199.00, 399.00, 'intermediate', 38.0, 'published', FALSE, 380, 4.60, 76, '2024-07-15 10:00:00'),
(8, 'React Native移动开发', '一套代码，多端运行', '使用React Native开发iOS和Android应用。', 4, 4, 349.00, 699.00, 'intermediate', 52.0, 'published', FALSE, 290, 4.55, 58, '2024-08-08 10:00:00'),
(9, '数据分析与可视化', 'Python数据分析三剑客', '学习Pandas、Matplotlib、Seaborn进行数据分析。', 5, 8, 249.00, 499.00, 'beginner', 42.0, 'published', FALSE, 520, 4.70, 104, '2024-09-01 10:00:00'),
(10, 'Git版本控制', '团队协作必备技能', '掌握Git工作流程，提升团队协作效率。', 3, 1, 0.00, 0.00, 'beginner', 8.0, 'published', FALSE, 2100, 4.45, 420, '2024-01-01 10:00:00');

-- 插入章节
INSERT INTO chapter (chapter_id, course_id, title, description, sort_order, is_free) VALUES
(1, 1, '第一章：Python环境搭建', '安装Python，配置开发环境', 1, TRUE),
(2, 1, '第二章：Python基础语法', '变量、数据类型、运算符', 2, TRUE),
(3, 1, '第三章：流程控制', '条件语句、循环语句', 3, FALSE),
(4, 1, '第四章：函数与模块', '函数定义、参数、模块导入', 4, FALSE),
(5, 1, '第五章：面向对象编程', '类与对象、继承、多态', 5, FALSE),
(6, 2, '第一章：HTML基础', 'HTML标签、结构、语义化', 1, TRUE),
(7, 2, '第二章：CSS样式', '选择器、盒模型、布局', 2, TRUE),
(8, 2, '第三章：JavaScript入门', '变量、函数、DOM操作', 3, FALSE),
(9, 2, '第四章：React框架', 'React组件、状态管理', 4, FALSE),
(10, 3, '第一章：机器学习概述', '什么是机器学习', 1, TRUE),
(11, 3, '第二章：数据预处理', '特征工程、数据清洗', 2, FALSE),
(12, 3, '第三章：监督学习', '回归与分类算法', 3, FALSE);

-- 插入课时
INSERT INTO lesson (lesson_id, chapter_id, title, content_type, video_url, video_duration, sort_order, is_free) VALUES
(1, 1, '1.1 Python简介', 'video', 'https://video.example.com/python/1-1.mp4', 600, 1, TRUE),
(2, 1, '1.2 Windows安装Python', 'video', 'https://video.example.com/python/1-2.mp4', 480, 2, TRUE),
(3, 1, '1.3 Mac安装Python', 'video', 'https://video.example.com/python/1-3.mp4', 420, 3, TRUE),
(4, 1, '1.4 IDE选择与配置', 'video', 'https://video.example.com/python/1-4.mp4', 720, 4, TRUE),
(5, 2, '2.1 变量与命名规则', 'video', 'https://video.example.com/python/2-1.mp4', 540, 1, TRUE),
(6, 2, '2.2 数据类型详解', 'video', 'https://video.example.com/python/2-2.mp4', 900, 2, TRUE),
(7, 2, '2.3 运算符', 'video', 'https://video.example.com/python/2-3.mp4', 660, 3, FALSE),
(8, 2, '2.4 字符串操作', 'video', 'https://video.example.com/python/2-4.mp4', 780, 4, FALSE),
(9, 3, '3.1 if条件语句', 'video', 'https://video.example.com/python/3-1.mp4', 600, 1, FALSE),
(10, 3, '3.2 for循环', 'video', 'https://video.example.com/python/3-2.mp4', 720, 2, FALSE),
(11, 3, '3.3 while循环', 'video', 'https://video.example.com/python/3-3.mp4', 540, 3, FALSE),
(12, 6, '1.1 HTML文档结构', 'video', 'https://video.example.com/web/1-1.mp4', 480, 1, TRUE),
(13, 6, '1.2 常用HTML标签', 'video', 'https://video.example.com/web/1-2.mp4', 720, 2, TRUE),
(14, 7, '2.1 CSS选择器', 'video', 'https://video.example.com/web/2-1.mp4', 660, 1, TRUE),
(15, 7, '2.2 盒模型详解', 'video', 'https://video.example.com/web/2-2.mp4', 600, 2, FALSE);

-- 插入订单
INSERT INTO `order` (order_id, order_no, user_id, total_amount, discount_amount, final_amount, payment_method, payment_status, paid_at, created_at) VALUES
(1, 'ORD202401150001', 1, 199.00, 0.00, 199.00, 'alipay', 'paid', '2024-01-15 14:30:00', '2024-01-15 14:25:00'),
(2, 'ORD202401200002', 1, 299.00, 50.00, 249.00, 'wechat', 'paid', '2024-01-20 10:15:00', '2024-01-20 10:10:00'),
(3, 'ORD202402050003', 2, 399.00, 0.00, 399.00, 'alipay', 'paid', '2024-02-05 16:45:00', '2024-02-05 16:40:00'),
(4, 'ORD202402100004', 7, 199.00, 0.00, 199.00, 'wechat', 'paid', '2024-02-10 09:00:00', '2024-02-10 08:55:00'),
(5, 'ORD202402150005', 8, 498.00, 98.00, 400.00, 'alipay', 'paid', '2024-02-15 11:30:00', '2024-02-15 11:25:00'),
(6, 'ORD202403010006', 9, 299.00, 0.00, 299.00, 'credit_card', 'paid', '2024-03-01 15:00:00', '2024-03-01 14:55:00'),
(7, 'ORD202403100007', 10, 199.00, 0.00, 199.00, 'alipay', 'pending', NULL, '2024-03-10 20:00:00'),
(8, 'ORD202401010008', 1, 0.00, 0.00, 0.00, 'free', 'paid', '2024-01-01 08:00:00', '2024-01-01 08:00:00');

-- 插入订单明细
INSERT INTO order_item (order_id, course_id, price) VALUES
(1, 1, 199.00), (2, 2, 299.00), (3, 3, 399.00), (4, 1, 199.00),
(5, 1, 199.00), (5, 2, 299.00), (6, 2, 299.00), (7, 1, 199.00), (8, 10, 0.00);

-- 插入选课记录
INSERT INTO enrollment (user_id, course_id, order_id, progress_percent, completed_lessons, total_lessons, status, enrolled_at, last_accessed_at) VALUES
(1, 1, 1, 75.50, 8, 11, 'active', '2024-01-15 14:30:00', '2024-12-28 20:00:00'),
(1, 2, 2, 30.00, 3, 10, 'active', '2024-01-20 10:15:00', '2024-12-27 18:30:00'),
(1, 10, 8, 100.00, 5, 5, 'completed', '2024-01-01 08:00:00', '2024-01-10 15:00:00'),
(2, 3, 3, 45.00, 5, 12, 'active', '2024-02-05 16:45:00', '2024-12-28 21:00:00'),
(7, 1, 4, 20.00, 2, 11, 'active', '2024-02-10 09:00:00', '2024-12-25 10:00:00'),
(8, 1, 5, 100.00, 11, 11, 'completed', '2024-02-15 11:30:00', '2024-06-20 14:00:00'),
(8, 2, 5, 60.00, 6, 10, 'active', '2024-02-15 11:30:00', '2024-12-28 16:00:00'),
(9, 2, 6, 10.00, 1, 10, 'active', '2024-03-01 15:00:00', '2024-12-20 11:00:00');

-- 插入学习进度
INSERT INTO learning_progress (user_id, lesson_id, watched_duration, progress_percent, is_completed, last_position) VALUES
(1, 1, 600, 100.00, TRUE, 600),
(1, 2, 480, 100.00, TRUE, 480),
(1, 3, 420, 100.00, TRUE, 420),
(1, 4, 720, 100.00, TRUE, 720),
(1, 5, 540, 100.00, TRUE, 540),
(1, 6, 900, 100.00, TRUE, 900),
(1, 7, 660, 100.00, TRUE, 660),
(1, 8, 400, 51.28, FALSE, 400),
(2, 12, 480, 100.00, TRUE, 480),
(2, 13, 300, 41.67, FALSE, 300);

-- 插入课程评价
INSERT INTO review (user_id, course_id, rating, content, helpful_count, created_at) VALUES
(1, 1, 5, '非常棒的课程！王老师讲得很清楚，从零基础到能独立写程序，真的很有成就感。', 45, '2024-03-15 10:00:00'),
(1, 10, 4, 'Git入门很实用，就是有些高级用法讲得不够深入。', 12, '2024-01-12 15:00:00'),
(2, 3, 5, '机器学习入门的最佳选择！陈老师的讲解深入浅出，配合实战项目效果很好。', 38, '2024-04-20 14:00:00'),
(7, 1, 5, '买过很多Python课程，这个是最好的，循序渐进，案例丰富！', 28, '2024-04-10 09:00:00'),
(8, 1, 4, '整体不错，但希望能多一些实战项目。', 15, '2024-06-25 16:00:00'),
(8, 2, 5, '前端课程非常全面，从HTML到React都讲到了，很满意！', 22, '2024-08-10 11:00:00'),
(9, 2, 4, '内容很好，就是更新有点慢。', 8, '2024-05-15 20:00:00');

-- 插入收藏
INSERT INTO favorite (user_id, course_id, created_at) VALUES
(1, 3, '2024-02-01 10:00:00'),
(1, 5, '2024-02-15 14:00:00'),
(1, 6, '2024-03-01 09:00:00'),
(2, 1, '2024-01-20 16:00:00'),
(2, 5, '2024-02-10 11:00:00'),
(7, 2, '2024-02-12 15:00:00'),
(7, 3, '2024-02-20 10:00:00'),
(8, 3, '2024-03-05 14:00:00'),
(9, 1, '2024-03-10 09:00:00');

-- 插入购物车
INSERT INTO cart (user_id, course_id, added_at) VALUES
(1, 4, '2024-12-20 10:00:00'),
(1, 8, '2024-12-22 15:00:00'),
(2, 2, '2024-12-25 11:00:00'),
(2, 6, '2024-12-26 09:00:00'),
(7, 5, '2024-12-27 14:00:00');
