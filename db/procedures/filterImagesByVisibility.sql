DELIMITER //
CREATE PROCEDURE filterImagesByVisibility(IN pVisibility ENUM('public', 'private'))
BEGIN
    SELECT * FROM Images WHERE isVisible = pVisibility;
END //
DELIMITER ;