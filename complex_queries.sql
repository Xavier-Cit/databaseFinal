-- ============================================================
-- 在线课程学习平台 - 复杂SQL查询示例
-- 本文件包含项目要求的所有SQL查询类型
-- ============================================================

USE online_learning_platform;

-- ============================================================
-- 1. 单表查询 (Single-table Query)
-- 查询所有价格大于100元且已发布的课程
-- ============================================================
SELECT 
    course_id,
    title,
    price,
    level,
    rating_avg,
    enrollment_count,
    published_at
FROM course
WHERE price > 100 
  AND status = 'published'
ORDER BY rating_avg DESC, enrollment_count DESC;

-- ============================================================
-- 2. 内连接查询 (Inner Join Query)
-- 查询所有课程及其讲师信息和分类信息
-- ============================================================
SELECT 
    c.course_id,
    c.title AS course_title,
    c.price,
    c.rating_avg,
    u.username AS instructor_name,
    u.email AS instructor_email,
    cat.category_name
FROM course c
INNER JOIN user u ON c.instructor_id = u.user_id
INNER JOIN category cat ON c.category_id = cat.category_id
WHERE c.status = 'published';

-- ============================================================
-- 3. 左外连接查询 (Left Outer Join Query)
-- 查询所有课程及其评价数量（包括没有评价的课程）
-- ============================================================
SELECT 
    c.course_id,
    c.title,
    c.price,
    COUNT(r.review_id) AS review_count,
    COALESCE(AVG(r.rating), 0) AS avg_rating
FROM course c
LEFT JOIN review r ON c.course_id = r.course_id AND r.status = 'approved'
WHERE c.status = 'published'
GROUP BY c.course_id, c.title, c.price
ORDER BY review_count DESC;

-- ============================================================
-- 4. 右外连接查询 (Right Outer Join Query)
-- 查询所有用户的购买记录（包括未购买任何课程的用户）
-- ============================================================
SELECT 
    u.user_id,
    u.username,
    u.email,
    COUNT(DISTINCT o.order_id) AS order_count,
    COALESCE(SUM(o.final_amount), 0) AS total_spent
FROM `order` o
RIGHT JOIN user u ON o.user_id = u.user_id
GROUP BY u.user_id, u.username, u.email
ORDER BY total_spent DESC;

-- ============================================================
-- 5. 自连接查询 (Self Join Query)
-- 查询所有分类及其父分类名称（展示层级关系）
-- ============================================================
SELECT 
    c.category_id,
    c.category_name AS category,
    c.parent_id,
    COALESCE(p.category_name, '顶级分类') AS parent_category,
    c.description
FROM category c
LEFT JOIN category p ON c.parent_id = p.category_id
ORDER BY COALESCE(c.parent_id, c.category_id), c.sort_order;

-- ============================================================
-- 6. 聚合函数与GROUP BY和ORDER BY
-- 统计每个讲师的课程数量、学员总数、平均评分
-- ============================================================
SELECT 
    u.user_id,
    u.username AS instructor_name,
    COUNT(DISTINCT c.course_id) AS course_count,
    SUM(c.enrollment_count) AS total_students,
    ROUND(AVG(c.rating_avg), 2) AS avg_rating,
    SUM(c.price * c.enrollment_count) AS estimated_revenue
FROM user u
INNER JOIN course c ON u.user_id = c.instructor_id
WHERE c.status = 'published'
GROUP BY u.user_id, u.username
HAVING course_count >= 1
ORDER BY total_students DESC, avg_rating DESC;

-- ============================================================
-- 7. 日期和时间函数
-- 查询本月注册用户和最近7天订单统计
-- ============================================================
-- 7.1 按日订单统计
SELECT 
    DATE(created_at) AS order_date,
    COUNT(*) AS order_count,
    SUM(final_amount) AS daily_revenue,
    COUNT(CASE WHEN payment_status = 'paid' THEN 1 END) AS paid_orders
FROM `order`
WHERE created_at >= DATE_SUB(CURRENT_DATE, INTERVAL 365 DAY)
GROUP BY DATE(created_at)
ORDER BY order_date DESC;

-- 7.2 计算课程发布至今的天数
SELECT 
    course_id,
    title,
    published_at,
    DATEDIFF(CURRENT_DATE, DATE(published_at)) AS days_since_publish,
    enrollment_count,
    ROUND(enrollment_count / GREATEST(DATEDIFF(CURRENT_DATE, DATE(published_at)), 1), 2) AS daily_avg_enrollment
FROM course
WHERE status = 'published' AND published_at IS NOT NULL
ORDER BY daily_avg_enrollment DESC;

-- ============================================================
-- 8. 子查询 (Subquery)
-- 查询购买数量超过平均值的课程
-- ============================================================
SELECT 
    course_id,
    title,
    price,
    enrollment_count,
    rating_avg
FROM course
WHERE enrollment_count > (
    SELECT AVG(enrollment_count) 
    FROM course 
    WHERE status = 'published'
)
AND status = 'published'
ORDER BY enrollment_count DESC;

-- ============================================================
-- 9. 相关子查询 (Correlated Subquery)
-- 查询每个分类中评分最高的课程
-- ============================================================
SELECT 
    c.category_id,
    cat.category_name,
    c.course_id,
    c.title,
    c.rating_avg,
    c.enrollment_count
FROM course c
INNER JOIN category cat ON c.category_id = cat.category_id
WHERE c.rating_avg = (
    SELECT MAX(c2.rating_avg)
    FROM course c2
    WHERE c2.category_id = c.category_id
    AND c2.status = 'published'
)
AND c.status = 'published'
ORDER BY c.category_id;

-- ============================================================
-- 10. 集合操作 UNION
-- 合并用户收藏和已购买的课程列表
-- ============================================================
SELECT 
    c.course_id,
    c.title,
    c.price,
    '已购买' AS source
FROM course c
INNER JOIN enrollment e ON c.course_id = e.course_id
WHERE e.user_id = 1

UNION

SELECT 
    c.course_id,
    c.title,
    c.price,
    '已收藏' AS source
FROM course c
INNER JOIN favorite f ON c.course_id = f.course_id
WHERE f.user_id = 1

ORDER BY course_id;

-- ============================================================
-- 11. 多表连接查询 (Multi-table Join)
-- 用户完整学习报告（涉及6个表）
-- ============================================================
SELECT 
    u.user_id,
    u.username,
    up.location,
    c.title AS course_title,
    cat.category_name AS category,
    inst.username AS instructor,
    e.enrolled_at,
    e.progress_percent,
    e.completed_lessons,
    e.total_lessons,
    e.status AS learning_status,
    COALESCE(r.rating, 0) AS my_rating,
    DATEDIFF(CURRENT_DATE, DATE(e.enrolled_at)) AS days_since_enroll
FROM user u
LEFT JOIN user_profile up ON u.user_id = up.user_id
INNER JOIN enrollment e ON u.user_id = e.user_id
INNER JOIN course c ON e.course_id = c.course_id
LEFT JOIN category cat ON c.category_id = cat.category_id
INNER JOIN user inst ON c.instructor_id = inst.user_id
LEFT JOIN review r ON u.user_id = r.user_id AND c.course_id = r.course_id
WHERE u.user_id = 1
ORDER BY e.enrolled_at DESC;

-- ============================================================
-- 12. 除法查询 (Division Query)
-- 查询学完某讲师(instructor_id=3)所有课程的学员
-- 使用计数比较法实现
-- ============================================================
SELECT 
    u.user_id,
    u.username,
    COUNT(DISTINCT e.course_id) AS completed_courses,
    (SELECT COUNT(*) FROM course WHERE instructor_id = 3 AND status = 'published') AS instructor_total_courses
FROM user u
INNER JOIN enrollment e ON u.user_id = e.user_id
INNER JOIN course c ON e.course_id = c.course_id
WHERE c.instructor_id = 3
AND c.status = 'published'
AND e.status = 'completed'
GROUP BY u.user_id, u.username
HAVING completed_courses = (
    SELECT COUNT(*) 
    FROM course 
    WHERE instructor_id = 3 
    AND status = 'published'
);

-- 使用双重NOT EXISTS方法
SELECT DISTINCT u.user_id, u.username, u.email
FROM user u
WHERE NOT EXISTS (
    SELECT 1 FROM course c
    WHERE c.instructor_id = 3
    AND c.status = 'published'
    AND NOT EXISTS (
        SELECT 1 FROM enrollment e
        WHERE e.user_id = u.user_id
        AND e.course_id = c.course_id
        AND e.status = 'completed'
    )
)
AND EXISTS (
    SELECT 1 FROM course WHERE instructor_id = 3 AND status = 'published'
)
AND EXISTS (
    SELECT 1 FROM enrollment WHERE user_id = u.user_id AND status = 'completed'
);
