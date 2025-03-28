DELIMITER //
CREATE PROCEDURE getAllUsers()
BEGIN
    SELECT userId, username, email, createdAt, isAdmin FROM Users;
END //
DELIMITER ;