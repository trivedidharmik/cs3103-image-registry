DELIMITER //
CREATE PROCEDURE insertImage(IN pUserId INT, IN pFileName VARCHAR(255), IN pFileExtension VARCHAR(10), IN pTitle VARCHAR(255), IN pDescription TEXT, IN pIsVisible ENUM('public', 'private'))
BEGIN
    INSERT INTO Images (userId, fileName, fileExtension, title, description, isVisible) VALUES (pUserId, pFileName, pFileExtension, pTitle, pDescription, pIsVisible);
END //
DELIMITER ;