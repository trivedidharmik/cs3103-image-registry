DELIMITER //
CREATE PROCEDURE getMostActiveUploaders()
BEGIN
    SELECT
        u.userId,
        u.username,
        COUNT(i.imageId) AS imageCount
    FROM Images i WHERE isVisible = 'public'
    JOIN Users u ON i.userId = u.userId
    GROUP BY u.userId
    ORDER BY imageCount DESC
    LIMIT 3;
END //
DELIMITER ;
