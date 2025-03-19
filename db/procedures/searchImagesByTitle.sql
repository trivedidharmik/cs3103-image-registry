DELIMITER //
CREATE PROCEDURE searchImagesByTitle(IN pKeyword VARCHAR(255))
BEGIN
    SELECT * FROM Images WHERE title LIKE CONCAT('%', pKeyword, '%') AND isVisible = 'public';
END //
DELIMITER ;