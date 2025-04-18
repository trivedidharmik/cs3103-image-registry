DELIMITER //
CREATE PROCEDURE verifyEmail(IN pUserId INT, IN pToken VARCHAR(255))
BEGIN
    DECLARE tokenCount INT;
    SELECT COUNT(*) INTO tokenCount FROM VerificationTokens WHERE userId = pUserId AND token = pToken AND expiresAt > NOW();
    IF tokenCount > 0 THEN
        DELETE FROM VerificationTokens WHERE userId = pUserId;
        INSERT INTO ValidatedEmails (userId) VALUES (pUserId);
        SELECT 1 AS success;
    ELSE
        SELECT 0 AS success;
    END IF;
END //
DELIMITER ;