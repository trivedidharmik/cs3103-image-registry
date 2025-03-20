DELIMITER //
CREATE PROCEDURE generateVerificationToken(IN pUserId INT)
BEGIN
    DECLARE v_token VARCHAR(255);
    SET v_token = UUID();
    INSERT INTO VerificationTokens (userId, token, expiresAt) VALUES (pUserId, v_token, NOW() + INTERVAL 1 DAY);
    SELECT pUserId AS userId, v_token AS token;
END //
DELIMITER ;