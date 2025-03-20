DELIMITER //

CREATE PROCEDURE getImageById(IN pImageId INT)
BEGIN
    SELECT imageId, userId, fileName, fileExtension, title, description, uploadedAt, isVisible 
    FROM Images 
    WHERE imageId = pImageId;
END //

DELIMITER ;
