DELIMITER //
CREATE PROCEDURE getImageByFileName(IN pFileName VARCHAR(255))
BEGIN
    SELECT userId, isVisible 
    FROM Images 
    WHERE fileName = pFileName;
END //
DELIMITER ;