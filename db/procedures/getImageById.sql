DELIMITER //

CREATE PROCEDURE getImageById(IN pImageId INT)
BEGIN
    SELECT imageId, userId, url, title, description, uploadedAt, isVisible 
    FROM Images 
    WHERE imageId = pImageId;
END //

DELIMITER ;
