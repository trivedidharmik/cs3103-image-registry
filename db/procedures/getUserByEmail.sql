DELIMITER $$

CREATE PROCEDURE getUserByEmail(IN user_email VARCHAR(255))
BEGIN
    SELECT userId, email, passwordHash, createdAt
    FROM Users
    WHERE email = user_email
    LIMIT 1;
END $$

DELIMITER ;
