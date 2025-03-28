DELIMITER //
CREATE PROCEDURE searchImages(IN pKeyword VARCHAR(255))
BEGIN
    SELECT * FROM Images 
    WHERE (title LIKE CONCAT('%', pKeyword, '%') OR description LIKE CONCAT('%', pKeyword, '%')) 
    AND isVisible = 'public';
END //
DELIMITER ;