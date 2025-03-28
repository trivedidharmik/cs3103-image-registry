DELIMITER //
CREATE PROCEDURE getUserById(IN uid INT)
BEGIN
    SELECT userId, username, email, passwordHash, isAdmin 
    FROM Users WHERE userId = uid;
END //
DELIMITER ;