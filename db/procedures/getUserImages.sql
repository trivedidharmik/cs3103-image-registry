DELIMITER //

CREATE PROCEDURE getUserImages(IN pUserId INT)
BEGIN
    SELECT imageId, url, title, description, uploadedAt, isVisible 
    FROM Images 
    WHERE userId = pUserId;
END //

DELIMITER ;
