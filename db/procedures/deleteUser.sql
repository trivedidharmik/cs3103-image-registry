DELIMITER //
CREATE PROCEDURE deleteUser(IN p_userId INT)
BEGIN
    DELETE FROM Images WHERE userId = p_userId;
    DELETE FROM ValidatedEmails WHERE userId = p_userId;
    DELETE FROM VerificationTokens WHERE userId = p_userId;
    DELETE FROM Users WHERE userId = p_userId;
END //
DELIMITER ;