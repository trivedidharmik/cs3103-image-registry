DELIMITER //
CREATE PROCEDURE getMostActiveUploaders()
BEGIN
    SELECT userId, COUNT(*) AS imageCount FROM Images GROUP BY userId ORDER BY imageCount DESC LIMIT 10;
END //
DELIMITER ;