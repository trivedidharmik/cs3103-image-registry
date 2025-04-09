
DELIMITER //
CREATE PROCEDURE removeEmailValidation(IN p_userId INT)
BEGIN
    DELETE FROM ValidatedEmails WHERE userId = p_userId;
END //
DELIMITER ;