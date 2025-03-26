DELIMITER //
CREATE PROCEDURE getImageOwner(IN pImageId INT)
BEGIN
    SELECT userId FROM Images WHERE imageId = pImageId;
END //
DELIMITER ;