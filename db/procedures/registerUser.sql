DELIMITER //
CREATE PROCEDURE registerUser(IN pUsername VARCHAR(255), IN pEmail VARCHAR(255), IN pPasswordHash VARCHAR(255))
BEGIN
    INSERT INTO Users (username, email, passwordHash) VALUES (pUsername, pEmail, pPasswordHash);
    SET @userId = LAST_INSERT_ID();
    CALL generateVerificationToken(@userId);
END //
DELIMITER ;