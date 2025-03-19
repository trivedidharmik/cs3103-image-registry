DELIMITER //
CREATE PROCEDURE getUserImageCount(IN p_userId INT)
BEGIN
    SELECT COUNT(*) FROM Images WHERE userId = p_userId;
END //
DELIMITER ;