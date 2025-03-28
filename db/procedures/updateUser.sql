DELIMITER //
CREATE PROCEDURE updateUser(
    IN uid INT,
    IN newUsername VARCHAR(255),
    IN newEmail VARCHAR(255),
    IN newPasswordHash VARCHAR(255)
)
BEGIN
    UPDATE Users
    SET 
        username = COALESCE(newUsername, username),
        email = COALESCE(newEmail, email),
        passwordHash = COALESCE(newPasswordHash, passwordHash)
    WHERE userId = uid;
END //
DELIMITER ;