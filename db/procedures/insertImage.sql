DELIMITER //
CREATE PROCEDURE insertImage(IN pUserId INT, IN pUrl VARCHAR(255), IN pTitle VARCHAR(255), IN pDescription TEXT, IN pIsVisible ENUM('public', 'private'))
BEGIN
    INSERT INTO Images (userId, url, title, description, isVisible) VALUES (pUserId, pUrl, pTitle, pDescription, pIsVisible);
END //
DELIMITER ;