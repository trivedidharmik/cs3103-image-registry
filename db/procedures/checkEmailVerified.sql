DELIMITER //
CREATE PROCEDURE checkEmailVerified(IN p_userId INT)
BEGIN
    SELECT userId FROM ValidatedEmails WHERE userId = p_userId;
END //
DELIMITER ;