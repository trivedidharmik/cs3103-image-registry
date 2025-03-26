DELIMITER //
CREATE PROCEDURE updateImageData(
    IN pImageId INT,
    IN pTitle VARCHAR(255),
    IN pDescription TEXT,
    IN pVisibility ENUM('public', 'private')
)
BEGIN
    UPDATE Images
    SET title = pTitle,
        description = pDescription,
        isVisible = pVisibility
    WHERE imageId = pImageId;
END //
DELIMITER ;