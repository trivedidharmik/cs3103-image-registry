DELIMITER //
CREATE PROCEDURE searchImages(IN pKeyword VARCHAR(255), IN pUserId INT)
BEGIN
    SELECT * FROM Images 
    WHERE (title LIKE CONCAT('%', pKeyword, '%') OR description LIKE CONCAT('%', pKeyword, '%')) 
    AND (isVisible = 'public' OR (isVisible = 'private' AND userId = pUserId));
END //
DELIMITER ;