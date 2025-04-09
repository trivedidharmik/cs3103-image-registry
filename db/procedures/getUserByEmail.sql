DELIMITER $$

CREATE PROCEDURE getUserByEmail(IN user_email VARCHAR(255))
BEGIN
    SELECT userId, username, email, passwordHash, createdAt, isAdmin
    FROM Users
    WHERE email = user_email
    LIMIT 1;
END $$

DELIMITER ;
