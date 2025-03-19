DELIMITER //
CREATE PROCEDURE deleteImage(IN pImageId INT, IN pUserId INT)
BEGIN
    DELETE FROM Images WHERE imageId = pImageId AND userId = pUserId;
END //
DELIMITER ;