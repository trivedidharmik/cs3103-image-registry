DELIMITER //
CREATE PROCEDURE getPublicAndUserPrivateImages(IN pUserId INT)
BEGIN
    SELECT * FROM Images 
    WHERE isVisible = 'public'
    OR (isVisible = 'private' AND userId = pUserId)
    ORDER BY uploadedAt DESC;
END //
DELIMITER ;