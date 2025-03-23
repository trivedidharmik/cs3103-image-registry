DELIMITER //

CREATE PROCEDURE getUserImages(IN pUserId INT)
BEGIN
    SELECT imageId, fileName, fileExtension, title, description, uploadedAt, isVisible 
    FROM Images 
    WHERE userId = pUserId;
END //

DELIMITER ;
